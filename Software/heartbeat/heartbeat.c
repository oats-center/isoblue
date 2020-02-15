/*
 * Heartbeat Message Kafka Producer
 *
 * Author: Yang Wang <wang701@purdue.edu>
 *
 * Copyright (C) 2018 Purdue University
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <stdbool.h>
#include <errno.h>

#include <sys/time.h>
#include <time.h>
#include <sqlite3.h>
#include "ini.c"

/* misc shell commands for checking cell strength and setting led values 
 * TODO: Reimplement with new LP board
 * */
/*static char *ns_cmd = "qmicli -p -d /dev/cdc-wdm0 --nas-get-signal-strength | \
  head -n 3 | tail -n 1 | sed \"s/^.*'\\([-0-9]*\\) dBm'[^']*$/\\1/\"";
*/
sqlite3 *db;
char* id;

/* Config file struct and callback */
static char *configloc = "/opt/isoblue/isoblue.cfg";

/* Struct to contain config */
typedef struct
{
  int hbinterval;
  const char* dbpath;
  const char* id;
  const char* baseuri;
  int debuglevel;
} configuration;

// Global config after it is read
configuration config;

/* Oarse configuration file */
static int handler(void* user, const char* section, const char* name, const char* value){
  configuration* pconfig = (configuration*)user;

  #define MATCH(s, n) strcmp(section, s) == 0 && strcmp(name, n) == 0
  if (MATCH("ISOBlue", "hbinterval")) {
    pconfig->hbinterval = atoi(value);
  } else if (MATCH("ISOBlue", "dbpath")) {
    pconfig->dbpath = strdup(value);
  } else if (MATCH("ISOBlue", "id")) {
    pconfig->id = strdup(value);
  } else if (MATCH("REST", "baseuri")){
    pconfig->baseuri = strdup(value);
  } else if(MATCH("ISOBlue", "debuglevel")){
    pconfig->debuglevel = atoi(value);
  } else {
    /* unknown section/name */
    /* There are many options used by other programs, so ignore non-matches */
    //return 0;
  }
  return 1;
}

/* Debug printing method */
/* `lvl` specifies the desired debug printing level.
 * If 'debuglvl' in the config file is the same or higher than lvl, then we will print (log) the statement */
void dbgprintf(int lvl, const char *fmt, ...){
  if(lvl <= config.debuglevel){
    /* Build format string, use snprintf blank buffer trick */
    int sizetoprint = snprintf(0, 0,"DEBUG %d: %s", lvl, fmt);
    char * dbgfmt = malloc(sizeof(char) * sizetoprint + 1);
    snprintf(dbgfmt, sizetoprint + 1,"DEBUG %d: %s", lvl, fmt);
    
    va_list argptr;
    va_start(argptr, fmt);
    vfprintf(stderr, dbgfmt, argptr);
    va_end(argptr);
    free(dbgfmt);
  }
}


/* Timer handler */
void timer_handler(int signum) {
  /* timeval struct */
  struct timeval tp;
  double timestamp;

  /* Heartbeat message variables */
  int cell_ns = -80;
  int wifi_ns = -70; //TODO: get real wifi rssi
  int ret;

  bool netled = false;
  bool statled = false;
  int ledval = 0;

  /* File pointer for running commands */
  FILE *fn;

  /* Get UNIX timestamp */
  gettimeofday(&tp, NULL);
  timestamp = tp.tv_sec + tp.tv_usec / 1000000.0;

  /* Check if ISOBlue has Internet */
  bool online = false;
  ret = system("wget -q --spider http://google.com");
  if (ret == -1) {
    perror("system");
    exit(EXIT_FAILURE);
  }else if (ret == 0){
    online = true;
  }

  dbgprintf(2, "Network status check returned `%d`, (%d)\n",ret, WEXITSTATUS(ret));

  /* Get the network strength from command */
  /*fn = popen(ns_cmd, "r");
  if (fn != NULL) {
    fscanf(fn, "%d", &cell_ns);
  } else {
    perror("popen");
    exit(EXIT_FAILURE);
  }

  //Close the subprocess
  if (pclose(fn) < 0) {
    perror("pclose");
    exit(EXIT_FAILURE);
  }*/
  cell_ns = -100;

  dbgprintf(1, "%f: cell network strength is %d\n", timestamp, cell_ns);

  if (cell_ns < -100) {
    dbgprintf(0, "%f: Network strength %d dBm doesn't make sense! Something WRONG!\n",
      timestamp, cell_ns);
  }

  /* Check if LED4 is lit green */
  statled = true;
  /*fn = popen(led4_cmd, "r");
  if (fn != NULL) {
    fflush(stdout);
    fscanf(fn, "%d", &ledval);
    dbgprintf(1, "led4val: %d\n", ledval);
    if (ledval == 255) {
      statled = true;
    } else {
      statled = false;
    }
    dbgprintf(1, "statled: %d\n", statled);
  } else {
    perror("popen");
    exit(EXIT_FAILURE);
  }

  // Close the subprocess
  if (pclose(fn) < 0) {
    perror("pclose");
    exit(EXIT_FAILURE);
  }*/

  netled = online;
  /* Create JSON String to store in db */
  
  dbgprintf(2, "LED Status light setting successful\n");

  dbgprintf(2, "Querying database for backlog\n");

  /* Query size of backlog to report in hearbeat */
  char * sql = "SELECT COUNT(sent) from sendqueue where sent == 0";
  char * zErrMsg = 0;
  /* Avoid exec function to avoid having to use a callback, which would get messy */
  sqlite3_stmt * stmt;
  sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
  int rc = sqlite3_step(stmt);
  int unsentrows = -1;
  if( rc == SQLITE_ROW){
    unsentrows = sqlite3_column_int(stmt, 0);
    dbgprintf(1, "Number of rows unsent: %d\n", unsentrows);
  }else{
    dbgprintf(1, "Could not query sql backlog\n");
    dbgprintf(1, "SQL Error: %d\n", rc);
  }
  sqlite3_finalize(stmt);

  dbgprintf(2, "Creating SQL String\n");
  /*Get day and time indicies for use when building URI*/
  time_t now;
  time(&now);
  struct tm *utctime = gmtime(&now);
  int hour = utctime->tm_hour;
  int year = utctime->tm_year + 1900;
  int month = utctime->tm_mon + 1;
  int day = utctime->tm_mday;

  /* snprint returns the number of bytes it could not write. We can leverage this to find the size
   * of a string needed by giving it a null buffer to write to */
  sql = 0;
  int sizetoprint = snprintf(0, 0, "INSERT INTO sendqueue(time, topic, data, sent) " \
    "VALUES (%d, \"%s/%s/heartbeat/day-index/%d-%02d-%02d/hour-index/%02d\", \'\"%.0f\":{\"timestamp\":%f,\"cell_ns\":%d,\"wifi_ns\":%d,\"backlog\":%d,\"netled\":%d,\"statled\":%d}\', 0)",\
    (int)timestamp, config.baseuri, config.id, year, month, day, hour, timestamp, timestamp, cell_ns, wifi_ns, unsentrows, netled, statled);

  dbgprintf(2, "Query string will be %d bytes long\n", sizetoprint);
  
  /* Plus 1 to include '\0' */
  sql = (char *) malloc(sizeof(char) * sizetoprint + 1);

  dbgprintf(2, "Query Malloc successful\n");

  /* Create actual sql string now that we have allocated the proper amount of memory */
  snprintf(sql, sizetoprint + 1, "INSERT INTO sendqueue(time, topic, data, sent) " \
    "VALUES (%d, \"%s/%s/heartbeat/day-index/%d-%02d-%02d/hour-index/%02d\", \'\"%.0f\":{\"timestamp\":%f,\"cell_ns\":%d,\"wifi_ns\":%d,\"backlog\":%d,\"netled\":%d,\"statled\":%d}\', 0)",\
    (int)timestamp, config.baseuri, config.id, year, month, day, hour, timestamp, timestamp, cell_ns, wifi_ns, unsentrows, netled, statled);


  dbgprintf(1, "SQL String: `%s`\n\tSQL string build successful, executing query\n",sql);
  dbgprintf(2, "Netled: %d | statled: %d\n", netled, statled);

  zErrMsg = 0;
  rc = 0;
  /* Ececute SQL string built above */
  rc = sqlite3_exec(db, sql, NULL, NULL, &zErrMsg);

  /* If DB is locked or busy, try 8 more times, every 100ms. If it is still busy, give up and move on 
   * Otherwise, report the error and move on */
  if( rc != SQLITE_OK ){
    if( rc == SQLITE_BUSY ) {
	int retries = 8;
    	dbgprintf(1, "SQL Error: %d \"%s\", retrying db write %d more times\n", rc, zErrMsg, retries);
	int i = 0;
	while( rc != SQLITE_OK && i < retries ){
          usleep(100);
	  zErrMsg = 0;
          rc = sqlite3_exec(db, sql, NULL, NULL, &zErrMsg);
	  dbgprintf(1, "SQL retry #%d return value: %d \"%s\"\n", i + 1, rc, zErrMsg);
	  i++;
	}
	if( rc != SQLITE_OK ){
	  dbgprintf(1, "After %d tries, could not insert hb data in db. Skipping\n", i + 1);
	}
    }else if (rc == SQLITE_LOCKED ){
	int retries = 8;
    	dbgprintf(1, "SQL Error: %d \"%s\", retrying db write %d more times\n", rc, zErrMsg, retries);
	int i = 0;
	while( rc != SQLITE_OK && i < retries ){
	  usleep(100);
          zErrMsg = 0;
          rc = sqlite3_exec(db, sql, NULL, NULL, &zErrMsg);
	  dbgprintf(1, "SQL retry #%d return value: %d \"%s\"\n", i + 1, rc, zErrMsg);
	  i++;
	}
	if( rc != SQLITE_OK ){
	  dbgprintf(1, "After %d tries, could not insert hb data in db. Skipping\n", i + 1);
	}
    }else {
	 dbgprintf(1, "SQL error: %d \"%s\"\n", rc, zErrMsg);
    }
    sqlite3_free(zErrMsg);
  }else{
    dbgprintf(1, "SQL Query execution successful\n");
  }

  free(sql); /* This could be optimized to use the same buffer over and over instead of reallocating it */

}

int main(int argc, char *argv[]) {


  /* Load and print config file */
  if (ini_parse(configloc, handler, &config) < 0) {
    printf("Can't load config file %s'\n", configloc);
    return EXIT_FAILURE;
  }
  dbgprintf(1, "DEBUG mode enabled\n");

  dbgprintf(1, "Config file parsing results:\n");
  dbgprintf(1, "hbinterval: %d\n", config.hbinterval);
  dbgprintf(1, "dbpath: %s\n", config.dbpath);
  dbgprintf(1, "id: %s\n", config.id);
  dbgprintf(1, "baseuri: %s\n", config.baseuri);
  dbgprintf(1, "debuglevel: %d\n", config.debuglevel);

  /* Timer stuff variables */
  struct sigaction sa;
  struct itimerval timer;


  /* Open/Create SQLite DB and table if needed */
  int rc = sqlite3_open(config.dbpath, &db);

  if( rc ){
    dbgprintf(1, "Cannot open sqldb: %s\n", sqlite3_errmsg(db));
    /* TODO: contine operating LEDs without writing to the DB in a 'Limp mode'? */
    return EXIT_FAILURE;
  }

  /* Create SQL statement */
  char * sql = "CREATE TABLE IF NOT EXISTS sendqueue("  \
    "id INTEGER PRIMARY KEY,"  \
    "time               INTEGER,"  \
    "topic              TEXT,"  \
    "data               TEXT,"  \
    "sent               INTEGER);" \
    "PRAGMA journal_mode=WAL";
  
  /* Execute SQL statement */
  char* zErrMsg = 0;
  rc = sqlite3_exec(db, sql, NULL, NULL, &zErrMsg);
  
  if( rc != SQLITE_OK ){
    fprintf(stderr, "SQL error: %s\n", zErrMsg);
    sqlite3_free(zErrMsg);
    return EXIT_FAILURE;
  }


  /* Install timer_handler as the signal handler for SIGALRM. */
  memset(&sa, 0, sizeof(sa));
  sa.sa_handler = &timer_handler;
  sigaction(SIGALRM, &sa, NULL);

  /* Configure the timer to expire after 5 secs... */
  timer.it_value.tv_sec = 5;
  timer.it_value.tv_usec = 0;
  /* ... and every 10 secs after that. */
  timer.it_interval.tv_sec = config.hbinterval;
  timer.it_interval.tv_usec = 0;

  /* Start a real timer. It counts down whenever this process is
   * executing. */
  setitimer(ITIMER_REAL, &timer, NULL);

  while (1) {
    sleep(1);
  }
  return EXIT_SUCCESS;
}
