#!/usr/bin/env python
# $Id: sigtestexample.py,v 1.3 2006/09/07 01:23:27 rockyb Exp $ 
"""Something to use to test signal handling. Basically we just need
a program that installs a signal handler.
"""
import sys
def signal_handler(num, f):
    f = open('log', 'w+')
    f.write('signal received\n')
    f.close()
    sys.exit(0)

import signal
signal.signal(signal.SIGUSR1, signal_handler)

if len(sys.argv) > 1 and sys.argv[1] == 'signal':
    import os
    os.kill(os.getpid(), signal.SIGUSR1)
else:
    reply = raw_input("Waiting in a read for signal USR1. " +
                      "Type any key to terminate now.")

