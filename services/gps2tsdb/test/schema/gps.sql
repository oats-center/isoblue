CREATE EXTENSION IF NOT EXISTS timescaledb;

DROP TABLE IF EXISTS "gps";
CREATE TABLE "public"."gps" (
    "time" timestamptz NOT NULL,
    "lat" double precision NOT NULL,
    "lng" double precision NOT NULL
);
SELECT create_hypertable('gps', 'time');
