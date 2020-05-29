// TODO
// Check for and gracefully handle invalid certificate
// Check for and gracefully handle no internet
// Seperate queried data into buckets for sending
// Use seperate table for tracking if someting sent with a union seletc

// Maybe just detect @oada/client failure, and re-queue with some sort of delay?
// const dns = require('dns').promises; // DNS Lookup used to check internet connectivity


// Quick fix while https://github.com/sindresorhus/is/issues/85 is still an issue
declare global {
  interface SymbolConstructor {
    readonly observable: symbol;
  }
}

// Packages
import { assert } from '@sindresorhus/is';
import { config } from 'dotenv';
import { Client } from 'pg';
import moment from 'moment';
import ksuid from 'ksuid';
import pEachSeries from 'p-each-series';
import { connect } from '@oada/client';
import { V1 as Location } from '@oada/types/oada/isoblue/location/v1';

import { isoblueDataTree } from './trees';

// dotenv
config();

// Main promise chain starts here
// Desired program flow:
//
// 1) Ensure postgres table is setup
// 2) Await internet connection
// 3) Connect oada-cache to server
// 4) While true:
//   4a) Await internet connection
//   4b) Query db for x unsent messages
//   4c) Massage data into proper oada-upoad format
//   4d) Sort data into batches based on topic and hour collected
//   4e) Upload data using oada-cache, verify success
//   4f) Mark entries successfully updated as sent in db
//   4g) Optional pause to not overload oada server
// 5) Gracefully handle errors

interface DataIndex {
  [key: string]: {
    gpsId: Array<string>;
    locations: {
      [key: string]: Omit<Location, Location['_type']>;
    };
  };
}

async function main(): Promise<void> {

  // Options
  const batchsize = process.env.oada_server_batchsize;
  assert.numericString(batchsize);
  const id = process.env.isoblue_id;
  assert.string(id);
  const domain = process.env.oada_server_url;
  assert.string(domain);
  const token = process.env.oada_server_token;
  assert.string(token);
  const db_user = process.env.db_user;
  assert.string(db_user);
  const db_host = process.env.db_host;
  assert.string(db_host);
  const db_database = process.env.db_database;
  assert.string(db_database);
  const db_password = process.env.db_password;
  assert.string(db_password);
  const db_port = Number(process.env.db_port);
  assert.integer(db_port);


  console.log(`Options from enviroment lets:
    Batch size: ${batchsize}
    ID: ${id}
    Domain: ${domain}
    Token: ${token}
    DB User: ${db_user}
    DB Host: ${db_host}
    DB Database: ${db_database}
    DB Password ${db_password}
    DB Port ${db_port}`);

  console.log('Creating databse client');
  //const db = new Client({ connectionString: conString });
  
  const db = new Client({
    user: db_user,
    host: db_host,
    database: db_database,
    password: db_password,
    port: db_port,
  })
  console.log('Connecting to database');

  try{ 
    await db.connect();
  }catch{
    console.log('Something went wrong connecting to the database... exiting');
    process.exit(-1);
  }

  // ADB: It is not clear to me if this service should own this table or not ... we
  // ADB: should think about this, because I could see many things wanting GPS.
  // ADB: Maybe this service should own a link table to mark `gps`.`id` as sent?
  console.log('Ensure DB table exists');
  await db.query(
    `CREATE TABLE IF NOT EXISTS gps (
      "id" BIGSERIAL NOT NULL,
      "time" timestamptz NOT NULL,
      "lat" double precision NOT NULL,
      "lng" double precision NOT NULL,
      "sent" boolean NOT NULL
    )`
  );

  console.log(`Connecting to OADA: ${domain}`);
  const oada = await connect({ domain, token });
  
  console.log(`Entering for loop`);
  for (;;) {
    const gps = await db.query(
      `SELECT id, extract(epoch from time) as time, lat, lng, sent
       FROM gps
       WHERE sent = FALSE
       ORDER BY time DESC
       LIMIT $1`,
      [batchsize]
    );

    // If we get no data from the databse, we sent everything
    // For debugging, exit. Eventually should wait and requery
    if (!gps.rows.length) {
      console.log('No unsent data found in database');
      await sleep(1000);
      continue;
    }
    
    console.info(`Found batch of ${gps.rows.length} GPS points`);
    console.debug(`Head time: ${gps.rows[0].time}`);

    const data: DataIndex = {};
    gps.rows.forEach((p) => {
      console.debug(`Processing GPS id: ${p.id}`);

      const t = moment.unix(p.time);
      const day = t.format('YYYY-MM-DD');
      const hour = t.format('HH');
      const path = `/bookmarks/isoblue/device-index/${id}/location/day-index/${day}/hour-index/${hour}`;
      const pId = ksuid.randomSync().string;

      if (!data[path]) {
        data[path] = {
          gpsId: [],
          locations: {},
        };
      }

      data[path].gpsId.push(p.id);
      data[path].locations[pId] = {
        id: pId,
        time: {
          value: p.time,
        },
        location: {
          lat: p.lat,
          lng: p.lng,
        },
      };
      
    });
    console.debug(`Done with the forEach loop\n`);
    await pEachSeries(Object.keys(data), async (path) => {
      console.debug(`Iterating pEachSeries loop with path ${path}`);
      var update_success = true;
      var res;
      try {
        console.debug(`GPS ID ${data[path].gpsId.join(',')} to OADA ${path}`);
        //console.debug(`Data[path]: %j`, data[path]);
        console.debug(`Calling oata.put:`);
        res = await oada.put({
          tree: isoblueDataTree,
          path,
          data: {data: data[path].locations},
        });
        console.debug(`oada put finished: `, res);
      } catch (e) {
        console.error(`Error Uploading to OADA: %p`, e, e.message, (<Error>e).message, ` `, res);
        update_success = false;
        // Do something with the error ?
        // Maybe just treat this as an indication that Internet is gone?
      }
      console.debug(`Done uploading to OADA`);
      if (update_success){
        try {
          console.debug(`Updating database for id ${data[path].gpsId}`);
          // Matching arrays do not always work like expected
          // https://github.com/brianc/node-postgres/wiki/FAQ#11-how-do-i-build-a-where-foo-in--query-to-find-rows-matching-an-array-of-values
          await db.query(
            'UPDATE gps SET sent = TRUE WHERE id = ANY($1)',
            [data[path].gpsId]
          );
        } catch (e) {
          console.error(`Error updating database with sent information: `, (<Error>e).message);
          // Do something with the error?
          // This seems pretty fatal
        }
      }
      await sleep(500);
    });
    console.debug(`End of pEachSeries loop`)
  }
}

// Sleep - used to pause after put to not overload server as well as yielding if
// there is no data to upload

// ADB: This seems fine for now ... in the future @oada/client will have built
// in concurrancy controls and I don't think you'll need any of the `sleep`s. In
// that case, you can control how many open requests you have to OADA, and you
// should go as fast as you can, within that limit ... I suppose the "caught up"
// case should maybe sleep a bit.
//
// A few other options:
//   - Move the work into a function, and use `setInterval` and `clearInterval`
//   to get a nice once-per-second rate going ... which you override to go
//   faster when there is still data in the database, e.g., "not caught up"
//
//   - Use p-queue to control the calls to OADA / DB (any Promise), and then use
//   queue length to make decisions on weather or not to continue searching.
//   p-queue comes with the ability to have a call back when the queue gets
//   below a certain size / empty. You could fetch from the DB in that case, and
//   the load up OADA calls.
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

main().catch((err) => {
  console.error(`Something unexpected happened! ${err}`);
  process.exit(-1);
});
