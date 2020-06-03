// TODO
// Check for and gracefully handle invalid certificate
// Check for and gracefully handle no internet
// Use seperate table for tracking if someting sent with a union select

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

// Main program starts here
// Desired program flow:
//
// 1) Ensure postgres table is setup
// 2) Await internet connection
// 3) Connect oada-cache to server
// 4) While true:
//   4a) Await internet connection
//   4b) Query db for x unsent messages
//   4c) Massage data into proper oada-upload format
//   4d) Sort data into batches based on topic and hour collected
//   4e) Upload data using oada-cache/client, verify success
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
  }catch (e){
    console.error('Fatal: Error connecting to the database: ', (<Error>e).message,);
    process.exit(-1);
  }

  console.log('Ensuring GPS DB table exists');
  await db.query(
    `CREATE TABLE IF NOT EXISTS gps (
      id BIGSERIAL UNIQUE NOT NULL,
      time timestamptz NOT NULL,
      lat double precision NOT NULL,
      lng double precision NOT NULL
    );`
  );
  console.log(`Ensuring own sent table exists`);
  await db.query(`
    CREATE TABLE IF NOT EXISTS gps_sent (
      g_id BIGSERIAL NOT NULL references gps(id),
      sent boolean DEFAULT FALSE
    );`
  );

  console.log(`Ensuring triggers to sync gps ids to sent db are created`);
  console.debug(`\tCreating sent row procedure`);
  await db.query(`
    CREATE OR REPLACE FUNCTION create_sent_row_procedure() RETURNS trigger AS $$
    BEGIN
    INSERT INTO gps_sent(g_id, sent)
    VALUES(NEW.id, FALSE);
    
    RETURN NEW;
    END;
    $$
    LANGUAGE 'plpgsql';`
  );

  // TODO: Currently we delete the trigger and recreate it. Apparently there is no
  // 'CREATE TRIGGER IF NOT EXISTS'. Is there a better way to ensure a trigger is 
  // created that may already exist?
  console.debug(`\tCreating trigger for creating rows`);
  await db.query(`
    DROP TRIGGER IF EXISTS create_sent_row_trig on public.gps;
    CREATE TRIGGER create_sent_row_trig
           AFTER INSERT on gps
           FOR EACH ROW
           EXECUTE FUNCTION create_sent_row_procedure();`
  );
  console.debug(`\tCreating delete row procedure`);
  await db.query(`
    CREATE OR REPLACE FUNCTION delete_sent_row_procedure() RETURNS trigger AS $$
    BEGIN
    DELETE FROM gps_sent where g_id = OLD.id;
    
    RETURN OLD;
    END;
    $$
    LANGUAGE 'plpgsql';`
  );
  console.debug('\tCreating trigger for deleting rows');
  await db.query(`
    DROP TRIGGER IF EXISTS delete_sent_row_trig on public.gps;
    CREATE TRIGGER delete_sent_row_trig
           BEFORE DELETE on gps
           FOR EACH ROW
           EXECUTE FUNCTION delete_sent_row_procedure();`
  );

  // This statement took more than 10 minuites of one of the
  // cloudradio machines when the database was loaded with 
  // > 300,000 data points. That is about a season of data
  // but should still be careful. Going to leave it commented out
  // for now until we determine a more efficient way to do this
  /*console.log(`Copying id's not already in the sent db`);
  await db.query(`SELECT id FROM gps WHERE gps.id NOT IN (SELECT g_id from gps_sent)`);*/

  console.log(`Connecting to OADA: ${domain}`);
  const oada = await connect({ domain, token });
  
  for (;;) {
    const gps = await db.query(
      `SELECT gps.id, extract(epoch from gps.time) as time, gps.lat, gps.lng, gps_sent.sent
        FROM gps
        JOIN gps_sent ON gps.id = gps_sent.g_id

        WHERE sent = FALSE
        ORDER BY time DESC
        LIMIT $1;`,
      [batchsize]
    );

    // If we get no data from the databse, we sent everything.
    // Wait 1s for the data to start to refill the db and requery
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
    await pEachSeries(Object.keys(data), async (path) => {
      var update_success = true;
      var res;
      try {
        console.debug(`GPS ID ${data[path].gpsId.join(',')} to OADA ${path}`);
        res = await oada.put({
          tree: isoblueDataTree,
          path,
          data: {data: data[path].locations},
        });
        console.debug(`oada put finished: `, res);
      } catch (e) {
        // Sending is not a success. This is either due to a misconfiguration or lack of internet.
        // Assume that everything is configured correctly, and rebuild the queue for the next try.
        console.error(`Error Uploading to OADA: %p`, e, e.message, (<Error>e).message, ` `, res);
        update_success = false;
      }
      console.debug(`Done uploading to OADA`);
      if (update_success){
        try {
          console.debug(`Updating database for ids ${data[path].gpsId}`);
          // Matching arrays do not always work like expected
          // https://github.com/brianc/node-postgres/wiki/FAQ#11-how-do-i-build-a-where-foo-in--query-to-find-rows-matching-an-array-of-values
          await db.query(
            'UPDATE gps_sent SET sent = TRUE WHERE g_id = ANY($1)',
            [data[path].gpsId]
          );
        } catch (e) {
          console.error(`Error updating database with sent information: `, (<Error>e).message);
          // Do something with the error?
          // This seems pretty fatal, exit and hope that when docker restarting the process fixes it
          console.error(`FATAL: Database exit error`);
          process.exit(-1);
        }
      }
      await sleep(500);
    });
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
  console.error(`Something unexpected happened! ${err}\n`, (<Error>err).message);
  process.exit(-1);
});
