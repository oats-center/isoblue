// TODO
// Check for and gracefully handle invalid certificate
// Check for and gracefully handle no internet
// Seperate queried data into buckets for sending
// Use seperate table for tracking if someting sent with a union seletc

// Maybe just detect @oada/client failure, and re-queue with some sort of delay?
// const dns = require('dns').promises; // DNS Lookup used to check internet connectivity

// Packages
import { assert } from '@sindresorhus/is';
import { config } from 'dotenv';
import { Client } from 'pg';
import moment from 'moment';
import ksuid from 'ksuid';
import { connect } from '@oada/client';

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

async function main(): Promise<void> {
  const db = new Client();

  // Options
  const batchsize = process.env.oada_server_batchsize;
  assert.numericString(batchsize);
  const id = process.env.isoblue_id;
  assert.string(id);
  const domain = process.env.oada_server_url;
  assert.string(domain);
  const token = process.env.oada_server_token;
  assert.string(token);
  const conString = process.env.db_connection_string;
  assert.string(conString);

  console.log(`Options from enviroment lets:
    Batch size: ${batchsize}
    ID: ${id}
    Domain: ${domain}
    Token: ${token}
    db_connection_string: ${conString}`);

  console.log('Connecting to database');
  await db.connect();

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
      return sleep(1000);
    }

    console.info(`Found batch of ${gps.rows.length} GPS points`);
    console.debug(`Head time: ${gps.rows[0].time}`);

    await Promise.all(
      gps.rows.map(async (p) => {
        const gpsId = p.id;
        console.debug(`Processing GPS id: ${gpsId}`);

        const t = moment.unix(p.time);
        const day = t.format('YYYY-MM-DD');
        const hour = t.format('HH');
        const path = `/bookmarks/isoblue/${id}/location/day-index/${day}/hour-index/${hour}`;
        const pId = ksuid.randomSync().string;
        const data = {
          data: {
            [pId]: {
              id: pId,
              time: {
                value: p.time,
              },
              location: {
                lat: p.lat,
                lng: p.lng,
              },
            },
          },
        };

        try {
          console.debug(`Sending point ${gpsId} to OADA`);
          await oada.put({ tree: isoblueDataTree, path, data });
        } catch (e) {
          // Do something with the error ?
          // Maybe just treat this as an indication that Internet is gone?
        }

        try {
          console.log('Updating database');
          await db.query('UPDATE gps SET send = TRUE WHERE id = $1', [gpsId]);
        } catch (e) {
          // Do something with the error?
          // This seems pretty fatal
        }
        await sleep(500);
      })
    );
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
