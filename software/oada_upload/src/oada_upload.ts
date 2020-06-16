// TODO
// Check for and gracefully handle invalid certificate
// Check for and gracefully handle no internet
// Standardize when console.log/debug/infos should be used
// Generally lessen printing to stdout/error
// Other minor TODOs sprinkled throught code

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
// 3) Connect oada-cache/client to server
// 4) While true:
//   4a) Await internet connection
//   4b) Query db for x unsent messages
//   4c) Massage data into proper oada-upload format
//   4d) Sort data into batches based on topic and hour collected
//   4e) Upload data using oada-cache/client, verify success
//   4f) Mark entries successfully updated as sent in db
//   4g) Optional pause to not overload oada server
// 5) Gracefully handle errors


// Database:
// The database schema has been a moving target but this is it's current state:
//
// One databse for GPS points/timestamps only. Eventually this should be made read-only
// to everyone but the process filling the db. This process ensures that the db is setup
// in case it boots before the process filling it but does not write to it
//
// One db "owned" by this process. It is linked to the GPS DB using triggers or foreign
// keys + cascades on update/delete. This is used by this process to keep track of which
// messages are sent and which are not

// Definition of an interface (similar to an object) used
// to organize data pulled from the database
interface DataIndex {
  [key: string]: {
    epochs: Array<string>;
    timetzs: Array<string>;
    locations: {
      [key: string]: Omit<Location, Location['_type']>;
    };
  };
}

// Main function
async function main(): Promise<void> {

  // Pull options from enviroment variables which are defined
  // in a *.env file or docker-compose.yml. This is the nominal
  // way to pass options with docker. Do basic type checking
  // TODO: Further option validation, docker secrets
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
  assert.string(db_password);  // Passwords with special chars have caused issues in the past
  const db_port = Number(process.env.db_port);
  assert.integer(db_port);


  // Print out options read in from enviromental variables for manual validation
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

  // Open a connection to the database using pg-node
  // Previously used a connection string, but this did
  // not seem to work
  console.log('Creating databse client');
  const db = new Client({
    user: db_user,
    host: db_host,
    database: db_database,
    password: db_password,
    port: db_port,
  })
  console.log('Connecting to database');

  // With the db client setup, initiate a connection to the database
  try{ 
    await db.connect();
  }catch (e){
    // The databse is hosted on the docker network, so there really shouldn't be any reason we
    // cannot connect. If we cannot connect this could mean either there is a severe 
    // misconfiguration (in which we cannot do much) or the db is still booting 
    // (Happens occasionally when the db booting for the first time). 
    // TODO: If the DB is still booting, exiting to restart is fine, but should 
    // investigate if there are ways to detect this wait before connecting
    console.error('Fatal: Error connecting to the database: ', (<Error>e).message,);
    process.exit(-1);
  }

  // First query to the database: activating the timescabledb extension
  console.log(`Activating timescaledb extension`);
  await db.query(`
    CREATE EXTENSION IF NOT EXISTS timescaledb;`
  );

  // Create the GPS DB table
  console.log('Ensuring GPS DB table exists');
  await db.query(`
    CREATE TABLE IF NOT EXISTS gps (
    time timestamptz UNIQUE NOT NULL,
    lat double precision NOT NULL,
    lng double precision NOT NULL
    );`
  );

  // Enable timescabledb hypertable for this table
  console.log(`Ensuring that GPS DB table is a timescaledb hypertable`);
  await db.query(`
    SELECT create_hypertable('gps', 'time', if_not_exists => TRUE, migrate_data => TRUE);`
  );

  // Create table to track what data has been sent
  // Previously we used IDs to keep track, but this has caused issues with timescaledb,
  // so we are currently using the timestamp itself
  console.log(`Ensuring own sent table exists`);
  await db.query(`
    CREATE TABLE IF NOT EXISTS gps_sent (
      g_time timestamptz UNIQUE NOT NULL,
      sent boolean DEFAULT FALSE
    );`
  );

  // Timescabdb hypertable for our sent table as well
  console.log(`Ensuring sent table is a timescaledb hypertable`);
  await db.query(`
    SELECT create_hypertable('gps_sent', 'g_time', if_not_exists => TRUE, migrate_data => TRUE);
  `);


  // To keep data synced in our sent table, we need to add triggers that will automagically
  // insert/delete a row in out table when one is inserted into the gps table. We cannot use
  // foreign keys easily due to timescaledb restrictions
  // Postgres requires us to define a function and then a trigger for it as opposed to
  // other databases that put the function inline with the tigger creation
  console.log(`Ensuring triggers to sync gps ids to sent db are created`);
  console.debug(`\tCreating sent row procedure`);
  await db.query(`
    CREATE OR REPLACE FUNCTION create_sent_row_procedure() RETURNS trigger AS $$
    BEGIN
    INSERT INTO gps_sent(g_time, sent)
    VALUES(NEW.time, FALSE);
    
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

  // Same as previous two for when rows are deleted
  console.debug(`\tCreating delete row procedure`);
  await db.query(`
    CREATE OR REPLACE FUNCTION delete_sent_row_procedure() RETURNS trigger AS $$
    BEGIN
    DELETE FROM gps_sent where g_time = OLD.time;
    
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

  // I notice that occasionally the first few rows of the gps database
  // would not be synced to the sent databse. This aims to sync them maunally
  // The below statement took more than 10 minuites before switch to
  // timescaledb on one of the cloudradio machines when the 
  // database was loaded with > 300,000 data points. That is 
  // about a season of gps data but should still be careful.
  // Going to leave it commented out for now until we determine 
  // a more efficient way to do this 
  /*console.log(`Copying time id's not already in the sent db`);
  await db.query(`SELECT time FROM gps WHERE gps.time NOT IN (SELECT g_time from gps_sent)`);*/

  console.log(`Connecting to OADA: ${domain}`);
  const oada = await connect({ domain, token });
  
  // Infinite loop to continuously check the db for unsent data
  for (;;) {
    // Extract x number of unsent data points
    const gps = await db.query(
      `SELECT gps.time as time_tz, extract(epoch from gps.time) as time_epoch, gps.lat, gps.lng, gps_sent.sent
        FROM gps
        JOIN gps_sent ON gps.time = gps_sent.g_time

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
    console.debug(`Head time: ${gps.rows[0].time_tz}`);

    // Create DataIndex object(?) for filling data in
    const data: DataIndex = {};
    // For each datapoint used, extract data and begin to sort them into buckets to be uploaded
    // Due to how the OADA server is setup, we the buckets will be by hour collected
    gps.rows.forEach((p) => {
      //console.debug(`Processing GPS time: ${p.time_tz}`);

      // Extract time and use it to create path that it will be uploaded it
      const t = moment.unix(p.time_epoch);
      const day = t.format('YYYY-MM-DD');
      const hour = t.format('HH');
      const path = `/bookmarks/isoblue/device-index/${id}/location/day-index/${day}/hour-index/${hour}`;
      // Create a UUID that can be coarsely sorted by time of creation
      // TODO: find a way to use the timestamp to create the id instead of the current time
      const pId = ksuid.randomSync().string;

      // If the current bucket does not exist, create it
      if (!data[path]) {
        data[path] = {
          epochs: [],
          timetzs: [],
          locations: {},
        };
      }

      // Insert our data into the bucket
      data[path].epochs.push(p.time_ecpoch);
      data[path].timetzs.push(p.time_tz);
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
    // pEachSeries executes the following code for each bucket (path) that we created sequentially 
    await pEachSeries(Object.keys(data), async (path) => {
      var update_success = true;
      var res;

      // Attempt the put to OADA
      try {
        //console.debug(`GPS ID ${data[path].epochs.join(',')} to OADA ${path}`);
        console.debug(`${data[path].epochs.length} points to OADA ${path}`);
        res = await oada.put({
          tree: isoblueDataTree,
          path,
          data: JSON.stringify({data: data[path].locations}),
        });
        //console.debug(`oada put finished: `, res);
        console.debug(`OADA put finished`);
      } catch (e) {
        // The PUT is not a success. This is either due to a misconfiguration or lack of internet.
        // Assume that everything is configured correctly rebuild the queue for the next try.
        console.error(`Error Uploading to OADA: %p`, e, e.message, (<Error>e).message, ` `, res);
        update_success = false;
      }
      console.debug(`Done uploading to OADA`);
      if (update_success){ // Replace the if with a 'continue' in the previous error state?

        // Update the databse that all of the ids are now sent successfully
        try {
          console.debug(`Updating database for ${data[path].timetzs.length} ids`);
          // Matching arrays do not always work like expected
          // https://github.com/brianc/node-postgres/wiki/FAQ#11-how-do-i-build-a-where-foo-in--query-to-find-rows-matching-an-array-of-values
          
          console.debug(`${data[path].timetzs.length} rows to update`)

          await db.query(`
            UPDATE gps_sent SET sent = TRUE WHERE g_time = ANY($1)`,
            [data[path].timetzs]
          );
        } catch (e) {
          console.error(`Error updating database with sent information: `, (<Error>e).message);
          // Do something with the error?
          // This seems pretty fatal, exit and hope that when docker restarting the process fixes it
          console.error(`FATAL: Database exit error`);
          process.exit(-1);
        }
      }
      // Wait half a second between uploads to not overwhelm the isoblue, OADA server, or the programmer trying to debug stuff
      // Should be removed enentually. Likely once OADA-Client has concurrency control
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
