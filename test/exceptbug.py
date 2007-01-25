from __future__ import with_statement
import threading

def f():
    l = threading.Lock()
    with l:
        print "hello"
        raise Exception("error")
        print "world"

try:
    f()
except:
   import pydb
   pydb.pm()
