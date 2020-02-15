__all__ = ["isoblue"]

cfgpath = '/opt/isoblue/isoblue.cfg'
import configparser
# Get global debug level
config = configparser.RawConfigParser()
filesread = config.read(cfgpath)
# Verify config read correctyly
if filesread[0] != cfgpath:
    print('Could not read config file')
    exit(-1)