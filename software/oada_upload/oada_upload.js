"use strict";

// TODO
// Check for and gracefully handle invalid certificate
// Check for and gracefully handle no internet
// Seperate queried data into buckets for sending
// Use seperate table for tracking if someting sent with a union seletc

// Packages
const readline = require('readline');
const oada = require("@oada/oada-cache");
const pg = require('pg'); // Postgres
const dns = require('dns').promises // DNS Lookup used to check internet connectivity
const Promise = require("bluebird");


// Options
const batchsize = process.env.oada_server_batchsize;
const basestring = process.env.oada_server_basepath;
const id = process.env.isoblue_id;
const server = process.env.oada_server_url;
const token = process.env.oada_server_token;
const conString = process.env.db_connection_string;
// Print out options
console.log('Options from enviroment vars:');
console.log('\tBatch size: ' + batchsize);
console.log('\tBase string: ' + basestring);
console.log('\tID: ' + id);
console.log('\tServer: ' + server);
console.log('\tToken: ' + token);
console.log('\tdb_connection_string' + conString);

// Setup connection to posgres database
var postgres = new pg.Client(conString);
postgres.connect();

// Define type tree for oada-cache to use with 
var tree = {
  bookmarks: {
    _type: "application/vnd.oada.bookmarks.1+json",
    _rev: 0,
    isoblue: {
      _type: "application/vnd.oada.isoblue.1+json",
      _rev: 0,
      "device-index": {
        "*": {
          _type: "application/vnd.oada.isoblue.device.1+json",
          _rev: 0,
          "*": {
            _type: "application/vnd.oada.isoblue.dataset.1+json",
            _rev: 0,
            "day-index": {
              "*": {
                _type: "application/vnd.oada.isoblue.day.1+json",
                _rev: 0,
                "hour-index": {
                  "*": {
                    _type: "application/vnd.oada.isoblue.hour.1+json",
                  },
                },
              },
            },
          },
        },
      },
    },
  },
};


// Arguments for oada-cache to use to connect to the server
var connectionArgs = {
  websocket: true,
  domain: server,
  token: token,
  cache: false,
};

// Debug print connection arguments
console.log("Connection details: ");
console.log("\twebsocket: " + connectionArgs.websocket);
console.log("\tdomain: " + connectionArgs.domain);
console.log("\ttoken: " + connectionArgs.token);
console.log("\tcache: " + connectionArgs.cache);


// Several results from promises are used out of scope
// Define globals for use out of the the promise
// TODO: This is likely bad practice and code flow
// should be chaged to fix this
var oada_conn = null;
var query_id = null;

// Keep track of repeated errors
var errcnt = 0;
var last_timestamp = null;
var timestamp_repeat_cnt = 0;

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
 

// Make query to Postgres db to ensure table is setup correctly
postgres.query('CREATE TABLE IF NOT EXISTS gps ( "id" BIGSERIAL NOT NULL, "time" timestamptz NOT NULL, "lat" double precision NOT NULL, "lng" double precision NOT NULL, "sent" boolean NOT NULL ) ')
  .then( res => {
    console.log('DB table initialization ensured');

    // connect oada-cache to server
    return oada.connect(connectionArgs)
}).then(conn => {
  console.error("Connected to OADA server.");

  // Assign connection to global for future use
  oada_conn = conn;

  // Build query
  const query = 'SELECT id, extract(epoch from time) as time, lat, lng, sent FROM gps WHERE sent = FALSE ORDER BY time DESC LIMIT $1';
  const params = [ batchsize ];
   
  // Debug Printout
  console.log('Querying database with `' + query + ', ' + params + '`');

  // Query, process, and send data in inf loop
  // The while loop does not seem to be able to handle multiple chained promises,
  // need to either modify while loop or wrap the chain up into one promise somehow?
  return PromiseWhile(() => true, () => postgres.query(query, params).then( res => {

    // If we get no data from the databse, we sent everything
    // For debugging, exit. Eventually should wait and requery
    if( res.rows[0] == undefined){
      console.log('No unsent data found in database');
      return sleep(1000);
    }

    // Debugging printout
    console.log('Query response head: ' + res.rows[0].time);
    
    var data;
    var path;

    // Process all rows of data from query
    var i;
    for(i = 0; i < res.rows.length; i++){
      query_id = res.rows[i].id;

      // Take unix string from query and convert it to 
      // YYYY-DD-HH format. Use pad method to ensure
      // '02' instead of '2'
      var date = new Date(res.rows[i].time * 1000);
      var hour = pad(date.getHours(),2);
      var datestring = date.getFullYear() + '-' + pad(date.getMonth(),2) + '-' + pad(date.getDate(),2);

      // Build path to push data to
      path = basestring + '/' + id + '/location/day-index/' + datestring + '/hour-index/' + hour;

      // Generate id to use for this set of data
      var dpid = makeid(16);

      // Data to send
      var lat = res.rows[i].lat;
      var lng = res.rows[i].lng;
      // There is a better way to generate json objects in js
      var datapoint = '\"' + dpid + '\": { \"id\": \"' + dpid + '\", \"time\": { \"value\": ' + res.rows[i].time + ' }, \"location\": { \"lat\": ' + lat +', \"lng\": ' + lng +' } }';


      // Encapsulate data in object
      var datastr = '{ \"data\": { ' + datapoint + ' } }';

      // Ensure data is proper json
      if(!validjson(datastr)){
        console.error("Warning data is not valid json!");
        console.error('Data point:' + datapoint);
      }

      // Parse string into object
      // Probabally should be an object to begin with
      data = JSON.parse(datastr);
      console.log("Making put request to path: " + path );
      console.log("Data object to put:\n" + JSON.stringify(data,null,4));
    }

    // If we try and send the same timestamp multiple times, oada cache may be in a situation where it is stuck and not 
    // reporting the error. Catch this and exit if this happens to force a cache reboot
    if(last_timestamp == res.rows[0].time){
      timestamp_repeat_cnt++;
      if(timestamp_repeat_cnt > 10){
        console.error('Cache is stuck?');
        process.exit();
      }
    }else{
      timestamp_repeat_cnt = 0;
    }

    last_timestamp = res.rows[0].time;

    // Make put request
    // TODO: make this part of promise .then chain
    oada_conn.put( {tree,path,data} )
      .then( res => {
        // Send successful
        errcnt = 0;
        console.error('Send successful:'+ res);

        const updatequery = 'UPDATE gps SET sent = TRUE where id = $1';
        const updateparams = [ query_id ];
        console.error('Querying database with `' + query + ', ' + params + '`');

        return postgres.query(updatequery, updateparams);
   
        console.error('Table updated successfully?'); 
      
    }).catch(err => {
      console.error('Put Error: ' + err);
      errcnt++;

      if(errcnt >= 10){
        console.error("10 consecutive errors Sending data or updating database. Exiting and restarting to try to clear error");
        process.exit();
      }
    });
   
    // Rest and give server time to recover
    return sleep(500);
  
  }));

}).catch(err => {
  console.error('Fatal Error: ' + err);
  console.error(err.stack);
  process.exit();
});


// Helper Methods

// Check if valid json to parse
// https://stackoverflow.com/a/20392392
function validjson (jsonString){
  try {
    var o = JSON.parse(jsonString);

    // Handle non-exception-throwing cases:
    // Neither JSON.parse(false) or JSON.parse(1234) throw errors, hence the type-checking,
    // but... JSON.parse(null) returns null, and typeof null === "object", 
    // so we must check for that, too. Thankfully, null is falsey, so this suffices:
    if (o && typeof o === "object") {
      return o;
    }
  }
  catch (e) { }

  return false;
};


// Generate random id for oada-id
// Copied from https://stackoverflow.com/a/1349426
// TODO: Use the hash of the data instead
function makeid(length) {
   var result           = '';
   var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
   var charactersLength = characters.length;
   for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}


// Pad numbers for processing dates for the oada upload path
// n is number to pad, width is how many digits to pad, and z is optional padding char
// https://stackoverflow.com/a/10073788/13225406
function pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

// Sleep - used to pause after put to not overload server as well as yielding if there
// is no data to upload
function sleep(ms){
  return new Promise((resolve, reject, onCancel) => {
    const timer = setTimeout(() =>{
      resolve();
    }, ms);
  });
}

// While loop promise
// Adapted from http://blog.victorquinn.com/javascript-promise-while-loop
function PromiseWhile(condition, action){
  const resolver = Promise.defer();
  const loop = function(){
    // Condition may either be a promise or a normal function.
    // True or Resolve -> condition satisfied.
    // False or Reject -> condition unsatisfied.
    const condition_result = condition();

    if(condition_result instanceof Promise){
      
      return new Promise((resolve2) => {
        
        condition_result.then(() =>{
          action().then(loop).catch((err) => {
            resolver.reject(err);
          });

        }).catch(() => {
          resolver.reject();
        });

      });
    }
    
    if(!condition()) {
      return resolver.resolve();
    }
    
    return action().then(loop).catch((err) => {
      resolver.reject(err);
    });
  };

  process.nextTick(loop);
  return resolver.promise;
}
