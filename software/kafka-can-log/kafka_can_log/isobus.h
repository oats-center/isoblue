/*
 * linux/can/isobus.h
 *
 * Definitions for ISOBUS CAN sockets
 *
 * Authors: Alex Layton <alex@layton.in>
 *          Urs Thuermann   <urs.thuermann@volkswagen.de>
 *          Oliver Hartkopp <oliver.hartkopp@volkswagen.de>
 * Copyright (c) 2002-2007 Volkswagen Group Electronic Research
 * All rights reserved.
 *
 */

#ifndef _ISOBUS_H_
#define _ISOBUS_H_

typedef __u32 pgn_t;

#define ISOBUS_PGN_MASK	0x03FFFFLU
#define ISOBUS_PGN1_MASK	0x03FF00LU
#define ISOBUS_ADDR_MASK	0xFFU

/* Transport Protocol */
#define ISOBUS_MAX_DLEN	1785
#define ISOBUS_MAX_PACKETS	255;

/* Network Management */
#define ISOBUS_NULL_ADDR	254U
#define ISOBUS_GLOBAL_ADDR	255U
#define ISOBUS_ANY_ADDR	ISOBUS_GLOBAL_ADDR
#define ISOBUS_PGN_REQUEST	59904LU
#define ISOBUS_PGN_ADDR_CLAIMED	60928LU
#define ISOBUS_PGN_COMMANDED_ADDR	65240LU

#define ISOBUS_MIN_SC_ADDR	128U
#define ISOBUS_MAX_SC_ADDR	247U

/* Macros for going between CAN IDs and PDU/PGN fields */
#define ISOBUS_PRI_POS	26
#define ISOBUS_PRI_MASK	0x07U
#define ISOBUS_PGN_POS	8
#define ISOBUS_PGN_MASK	0x03FFFFLU
#define ISOBUS_PGN1_MASK	0x03FF00LU
#define ISOBUS_PS_POS	8
#define ISOBUS_PS_MASK	0xFFU
#define ISOBUS_PF_POS	16
#define ISOBUS_PF_MASK	0xFFU
#define ISOBUS_SA_POS	0
#define ISOBUS_SA_MASK	0xFFU
#define ISOBUS_DP_POS	24
#define ISOBUS_DP_MASK	0x01U
#define ISOBUS_EDP_POS	25
#define ISOBUS_EDP_MASK	0x01U
#define CANID(pri, pgn, da, sa)	( \
		CAN_EFF_FLAG | \
		((pri & ISOBUS_PRI_MASK) << ISOBUS_PRI_POS) | \
		((pgn & ISOBUS_PGN_MASK) << ISOBUS_PGN_POS) | \
		((da & ISOBUS_PS_MASK) << ISOBUS_PS_POS) | \
		((sa & ISOBUS_SA_MASK) << ISOBUS_SA_POS) )
#define ID_FIELD(id, field)	\
	((id >> ISOBUS_ ## field ## _POS) & ISOBUS_ ## field ## _MASK)
#define PGN_FIELD(pgn, field)	ID_FIELD(pgn << ISOBUS_PGN_POS, field)
#define ISOBUS_MIN_PDU2	240
#define ID_PDU_FMT(id) (ID_FIELD(id, PF) < ISOBUS_MIN_PDU2 ? 1 : 2)
#define PGN_PDU_FMT(pgn)	ID_PDU_FMT(pgn << ISOBUS_PGN_POS)

/* Stuff for NAME fields */
#define ISOBUS_NAME_ID_MASK	0x00000000001FFFFFLU
#define ISOBUS_NAME_ID_POS	0
#define ISOBUS_NAME_MAN_MASK	0x00000000FFE00000LU
#define ISOBUS_NAME_MAN_POS	21
#define ISOBUS_NAME_ECU_MASK	0x0000000700000000LU
#define ISOBUS_NAME_ECU_POS	32
#define ISOBUS_NAME_FINST_MASK	0x000000F800000000LU
#define ISOBUS_NAME_FINST_POS	35
#define ISOBUS_NAME_FUNC_MASK	0x0000FF0000000000LU
#define ISOBUS_NAME_FUNC_POS	40
#define ISOBUS_NAME_CLASS_MASK	0x00FE000000000000LU
#define ISOBUS_NAME_CLASS_POS	49
#define ISOBUS_NAME_CINST_MASK	0x0F00000000000000LU
#define ISOBUS_NAME_CINST_POS	56
#define ISOBUS_NAME_IG_MASK	0x7000000000000000LU
#define ISOBUS_NAME_IG_POS	60

/* Timeouts etc. (100's on ns) */
#define ISOBUS_ADDR_CLAIM_TIMEOUT	2500L
#define ISOBUS_RTXD_MULTIPLIER	6L

/* Priority stuff */
#define MIN_PRI	0
#define MAX_PRI	7
#define ISOBUS_PRIO(p)	\
	(MAX_PRI - ((p < MIN_PRI ? MIN_PRI : p) > MAX_PRI ? MAX_PRI : p) + MIN_PRI)
#define SK_PRIO(p)	(MAX_PRI - p + MIN_PRI)

#endif /* _ISOBUS_H_ */

