import string
import socket
import random
import configparser
import sys

# Debug printing controloled by gloabl debug value in cfg file 
def printdebug(lvl=2, *args, **kwargs):
    debuglevel = 100
    if lvl <= debuglevel:
        print('DEBUG ' + str(lvl) + ': ', *args, file=sys.stderr, **kwargs)

# Check for internet. Pings cloudflare's DNS server
def internet(host="1.1.1.1", port=80, timeout=3):
    """
    Host: 1.1.1.1 (one.one.one.one: Cloudflare DNS server)
    OpenPort: 80/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        printdebug(2, ex)
        return False

# Generate Random string. Used for UUIDs when pushing OADA Data
def id_generator(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))