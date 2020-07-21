/*
 * Raw CAN Frame Kafka Producer
 *
 * Author: Yang Wang <wang701@purdue.edu>
 *
 * Copyright (C) 2020 Purdue University
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

#define KAFKA_CAN_LOG_VER	"kafka_can_log - Raw CAN Frame Kafka Producer"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <errno.h>
#include <stdbool.h>
#include <argp.h>

#include <net/if.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/time.h>

#include <linux/can.h>
#include <linux/can/raw.h>

#include <avro.h>
#include <librdkafka/rdkafka.h>

#include "isobus.h"

const char RAW_CAN_SCHEMA[] =
"{\"type\":\"record\",\
  \"name\":\"rawcan\",\
  \"fields\":[\
	{\"name\": \"timestamp\", \"type\": \"double\"},\
	{\"name\": \"is_error_frame\", \"type\": \"boolean\"},\
	{\"name\": \"is_extended_frame\", \"type\": \"boolean\"},\
	{\"name\": \"arbitration_id\", \"type\": \"int\"},\
	{\"name\": \"dlc\", \"type\": \"int\"},\
	{\"name\": \"payload\", \"type\": \"bytes\"},\
	{\"name\": \"is_remote_frame\", \"type\": \"boolean\"}]}";

/* CAN socket */
int s;

/* argp goodies */
#ifdef BUILD_NUM
const char *argp_program_version = KAFKA_CAN_LOG_VER "\n" BUILD_NUM;
#else
const char *argp_program_version = KAFKA_CAN_LOG_VER;
#endif
const char *argp_program_bug_address = "<bugs@isoblue.org>";
static char args_doc[] = "IFACE TOPIC";
static char doc[] = "Logs CAN frames and produces to Kafka broker";
static struct argp_option options[] = {
	{NULL, 0, NULL, 0, "About", -1},
	{NULL, 0, NULL, 0, "Configuration", 0},
	{"iface", 'i', "<iface>", 0, "CAN interface name", 0},
	{"topic", 't', "<topic-name>", 0, "Local Kafka topic name", 0},
	{ 0 }
};

struct arguments {
	char *iface;
	char *topic_name;
};

static error_t parse_opt(int key, char *arg, struct argp_state *state)
{
	struct arguments *arguments = state->input;
	error_t ret = 0;

	switch(key) {
		case 'i':
			arguments->iface = arg;
			break;

		case 't':
			arguments->topic_name = arg;
			break;

		case ARGP_KEY_END:
			if (arguments->iface == NULL || arguments->topic_name == NULL) {
				argp_usage(state);
				ret = EINVAL;
			}
			break;

		default:
			return ARGP_ERR_UNKNOWN;
	}

	return errno = ret;
}

static struct argp argp = {
	options,
	parse_opt,
	args_doc,
	doc,
	NULL,
	NULL
};

/* Print function for debugging */
void print_frame(FILE *fd, char interface[], long sec, long usec,
		struct can_frame *cf) {
	int i;

	/* Output CAN frame */
	fprintf(fd, "<0x%08x> [%u]", cf->can_id, cf->can_dlc);
	for(i = 0; i < cf->can_dlc; i++) {
		fprintf(fd, " %02x", cf->data[i]);
	}
	/* Output timestamp and CAN interface */
	fprintf(fd, "\t%ld.%06ld\t%s\r\n", sec, usec, interface);

	/* Flush output after each frame */
	fflush(fd);
}

/* Add received CAN frame's data to a record */
void add_raw_can_frame(avro_schema_t *raw_can, struct can_frame *cf,
	double timestamp) {
	uint8_t is_extended_frame = ((cf->can_id & CAN_EFF_FLAG) > 0);

	avro_datum_t ts_datum = avro_double(timestamp);
	avro_datum_t rf_datum = avro_boolean((cf->can_id & CAN_RTR_FLAG) > 0);
	avro_datum_t ie_datum = avro_boolean((cf->can_id & CAN_ERR_FLAG) > 0);
	avro_datum_t ei_datum = avro_boolean(is_extended_frame);

	avro_datum_t aid_datum;

	if (is_extended_frame) {
		aid_datum = avro_int32(cf->can_id & CAN_EFF_MASK);
	} else {
		aid_datum = avro_int32(cf->can_id & CAN_SFF_MASK);
	}

	avro_datum_t dlc_datum = avro_int32(cf->can_dlc);
	avro_datum_t pl_datum = avro_bytes((const char *)cf->data, 8);

	if (avro_record_set(*raw_can, "timestamp", ts_datum)
		|| avro_record_set(*raw_can, "is_remote_frame", rf_datum)
		|| avro_record_set(*raw_can, "is_error_frame", ie_datum)
		|| avro_record_set(*raw_can, "is_extended_frame", ei_datum)
		|| avro_record_set(*raw_can, "dlc", dlc_datum)
		|| avro_record_set(*raw_can, "payload", pl_datum)
		|| avro_record_set(*raw_can, "arbitration_id", aid_datum)) {
		fprintf(stderr, "Unable to set record\n");
		exit(EXIT_FAILURE);
	}

	/* Decrement all our references to prevent memory from leaking */
	avro_datum_decref(ts_datum);
	avro_datum_decref(rf_datum);
	avro_datum_decref(ie_datum);
	avro_datum_decref(ei_datum);
	avro_datum_decref(aid_datum);
	avro_datum_decref(dlc_datum);
	avro_datum_decref(pl_datum);
}

/* Determine the PGN of a CAN frame */
static pgn_t get_pgn(struct can_frame *cf)
{
	pgn_t pgn;

	/* PDU1 format */
	if(ID_PDU_FMT(cf->can_id) == 1) {
		pgn = (cf->can_id >> ISOBUS_PGN_POS) & ISOBUS_PGN1_MASK;
	}
	/* PDU2 format */
	else {
		pgn = (cf->can_id >> ISOBUS_PGN_POS) & ISOBUS_PGN_MASK;
	}

	return pgn;
}

int main(int argc, char *argv[]) {
#if DEBUG
	/* fd for logging */
	FILE *fd;
	fd = stdout;
#endif

	/* Handle options */
	struct arguments arguments = {
		NULL,
		NULL,
	};

	if (argp_parse(&argp, argc, argv, 0, 0, &arguments)) {
		perror("argp");
		return EXIT_FAILURE;
	}

	/* Buffers for building up the message key */
	char key[100];
	char pgn_str[10];

	/* CAN stuff variables */
	struct sockaddr_can addr;
	struct ifreq ifr;
	can_err_mask_t err_mask;

	/* Avro stuff variables */
	/* One CAN frame is 25 bytes at most when serialized with Avro */
	/* Doubled the buffer size to be safe */
	char buf[50];
	avro_writer_t writer;
	avro_schema_t raw_can_schema;
	avro_datum_t raw_can;

	/* Kafka variables */
	rd_kafka_t *rk;
	rd_kafka_topic_t *rkt;
	rd_kafka_conf_t *conf;
	rd_kafka_topic_conf_t *topic_conf;
	char *brokers = "localhost:9092";
	char errstr[512];
	int partition = RD_KAFKA_PARTITION_UA;

	/* Create CAN socket */
	if ((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) {
		perror("socket");
		return EXIT_FAILURE;
	}

	/* Get the interface ID from arguments */
	strcpy(ifr.ifr_name, arguments.iface);
	ioctl(s, SIOCGIFINDEX, &ifr);

	/* Listen on the CAN interface */
	addr.can_family  = AF_CAN;
	addr.can_ifindex = ifr.ifr_ifindex;

	if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
		perror("bind");
		return EXIT_FAILURE;
	}

	/* Receive all error frames */
	err_mask = CAN_ERR_MASK;
	setsockopt(s, SOL_CAN_RAW, CAN_RAW_ERR_FILTER, &err_mask, sizeof(err_mask));

	/* Timestamp frames */
	const int val = 1;
	setsockopt(s, SOL_SOCKET, SO_TIMESTAMP, &val, sizeof(val));

	/* Buffer received CAN frames */
	struct can_frame cf;
	struct msghdr msg = { 0 };
	struct iovec iov = { 0 };
	char ctrlmsg[CMSG_SPACE(sizeof(struct timeval))];

	/* Construct msghdr to use to recevie messages from socket */
	msg.msg_name = &addr;
	msg.msg_namelen = sizeof(addr);
	msg.msg_control = ctrlmsg;
	msg.msg_controllen = sizeof(ctrlmsg);
	msg.msg_iov = &iov;
	msg.msg_iovlen = 1;
	iov.iov_base = &cf;
	iov.iov_len = sizeof(cf);

	/* Kafka conf */
	conf = rd_kafka_conf_new();
	rd_kafka_conf_set(conf, "batch.num.messages", "20000", errstr,
    sizeof(errstr));
	rd_kafka_conf_set(conf, "queue.buffering.max.messages", "1000000", errstr,
    sizeof(errstr));
	rd_kafka_conf_set(conf, "queue.buffering.max.ms", "1", errstr,
    sizeof(errstr));
	rd_kafka_conf_set(conf, "log.connection.close", "false", errstr,
    sizeof(errstr));

	/* Kafka topic conf */
	topic_conf = rd_kafka_topic_conf_new();
	rd_kafka_topic_conf_set(topic_conf, "request.required.acks", "0", errstr,
    sizeof(errstr));

	/* Create Kafka producer */
	if (!(rk = rd_kafka_new(RD_KAFKA_PRODUCER, conf, errstr, sizeof(errstr)))) {
		fprintf(stderr, "%% Failed to create new producer: %s\n", errstr);
		return EXIT_FAILURE;
	}

	if (rd_kafka_brokers_add(rk, brokers) == 0) {
		fprintf(stderr, "%% No valid brokers specified\n");
		return EXIT_FAILURE;
	}

	/* Create new Kafka topic */
	rkt = rd_kafka_topic_new(rk, arguments.topic_name, topic_conf);
	topic_conf = NULL;

	/* Initialize the schema structure from JSON */
	if (avro_schema_from_json_literal(RAW_CAN_SCHEMA, &raw_can_schema)) {
		fprintf(stderr, "Unable to parse raw can schema\n");
		return EXIT_FAILURE;
	}

	/* Create avro writer */
	writer = avro_writer_memory(buf, sizeof(buf));

	/* Create avro record based on the schema */
	raw_can = avro_record(raw_can_schema);

	while (1) {
		double timestamp;
#if DEBUG
		long sec;
		long usec;
#endif

		/* Print received CAN frames */
		if (recvmsg(s, &msg, 0) <= 0) {
			if (errno != EINTR) {
				perror("recvmsg");
			}
			continue;
		}

		/* Find approximate receive time */
		struct cmsghdr *cmsg;
		for (cmsg = CMSG_FIRSTHDR(&msg); cmsg != NULL;
				cmsg = CMSG_NXTHDR(&msg, cmsg)) {
			if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SO_TIMESTAMP) {
				struct timeval *tv = (struct timeval *) CMSG_DATA(cmsg);
				timestamp = tv->tv_sec + tv->tv_usec / 1000000.0;
#if DEBUG
				sec = tv->tv_sec;
				usec = tv->tv_usec;
#endif
				break;
			}
		}

#if DEBUG
		/* Find name of receive interface */
		ifr.ifr_ifindex = addr.can_ifindex;
		ioctl(s, SIOCGIFNAME, &ifr);
#endif

		pgn_t pgn = get_pgn(&cf);
		sprintf(pgn_str, "%u", pgn);

		/* Create the key */
		strcpy(key, ifr.ifr_name);
		strcat(key, ":");
		strcat(key, pgn_str);

#if DEBUG
		printf("The message key: %s\n", key);
		print_frame(fd, ifr.ifr_name, sec, usec, &cf);
#endif

		/* Add the raw_can_frame datum */
		add_raw_can_frame(&raw_can, &cf, timestamp);

		/* Write to avro writer */
		if (avro_write_data(writer, raw_can_schema, raw_can)) {
			fprintf(stderr, "unable to write raw_can datum to memory ahahahahah\n");
			exit(EXIT_FAILURE);
		}

		/* Produce the CAN frame to Kafka */
		if (rd_kafka_produce(rkt, partition, RD_KAFKA_MSG_F_COPY,
				buf, avro_writer_tell(writer), key, strlen(key), NULL) == -1) {
			fprintf(stderr, "%% Failed to produce to topic %s "
							"partition %i: %s\n",
							rd_kafka_topic_name(rkt), partition,
							rd_kafka_err2str(rd_kafka_last_error()));
			rd_kafka_poll(rk, 0);
		}

		rd_kafka_poll(rk, 0);

		avro_writer_reset(writer);

		/* Reset the key buffer */
		memset(&key[0], 0, sizeof(key));
	}

	avro_datum_decref(raw_can);
	avro_schema_decref(raw_can_schema);
	avro_writer_free(writer);
	rd_kafka_topic_destroy(rkt);
	rd_kafka_destroy(rk);

	return EXIT_SUCCESS;
}
