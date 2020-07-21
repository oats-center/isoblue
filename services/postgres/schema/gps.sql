DROP TABLE IF EXISTS "gps";
DROP SEQUENCE IF EXISTS gps_id_seq;
CREATE SEQUENCE gps_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1;

CREATE TABLE "public"."gps" (
    "id" bigint DEFAULT nextval('gps_id_seq') NOT NULL,
    "time" timestamptz NOT NULL,
    "lat" double precision NOT NULL,
    "lng" double precision NOT NULL,
    "sent" boolean NOT NULL
) WITH (oids = false);
