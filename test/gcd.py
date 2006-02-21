#!/usr/bin/python
"""Greatest Common Divisor

Some characterstics of this program used for testing check_args() does
not have a 'return' statement.

check_args() raises an uncaught exception when given the wrong number
of parameters.

"""
import sys,os

def check_args():
    if len(sys.argv) != 3:
        # Rather than use sys.exit let's just raise an error
        raise Exception, "Need to give two numbers"
    for i in range(2):
        try: 
            sys.argv[i+1] = int(sys.argv[i+1])
        except ValueError, msg:
            print "** Expecting an integer, got: %s" % repr(sys.argv[i])
            sys.exit(2)
    
def gcd(a,b):
    """ GCD. We assume positive numbers"""

    # Make: a <= b
    if a > b:
       (a, b) = (b, a)
       
    if a <= 0:
        return None
    if a == 1:
        return b
    return gcd(b-a, a)

check_args()

print gcd(sys.argv[1], sys.argv[2])

