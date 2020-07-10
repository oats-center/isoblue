#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([isoblue-software], [1.0], [wang701@purdue.edu])
#AC_CONFIG_SRCDIR([can_watchdog/can_watchdog.c])
#AC_CONFIG_HEADERS([config.h])
AM_INIT_AUTOMAKE([subdir-objects])

# Checks for programs.
AC_PROG_CC

# Checks for libraries.
AC_CHECK_LIB([avro], [avro_value_copy], [], AC_MSG_ERROR([libavro not found! Not so lucky today.]))
AC_CHECK_LIB([pthread], [pthread_attr_destroy], [], AC_MSG_ERROR([libpthread not found! Not so lucky today.]))
AC_CHECK_LIB([rdkafka], [rd_kafka_topic_new], [], AC_MSG_ERROR([librdkafka not found! Not so lucky today.]))
AC_CHECK_LIB([rt], [aio_cancel], [], AC_MSG_ERROR([librt not found! Not so lucky today.]))

# Checks for header files.
AC_CHECK_HEADERS([stdio.h stdlib.h string.h sys/ioctl.h sys/socket.h sys/time.h unistd.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_CHECK_HEADER_STDBOOL
AC_TYPE_UINT8_T

# Checks for library functions.
AC_FUNC_MALLOC
AC_CHECK_FUNCS([gettimeofday memset socket])

AC_CONFIG_FILES([Makefile kafka_can_log/Makefile])
AC_OUTPUT
