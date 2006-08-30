#!/usr/bin/env python
""" This is a script that is being used to debug whilst trying to get
the thread debugging features working.
"""

import threading

def foo():
    for n in range(2):
        print n
        print "I am thread %s loop count %d" % \
              (threading.currentThread().getName(), n)

class MyThread(threading.Thread):
    def run(self):
        foo()

def func():
    for i in range(2):
        t = MyThread()
        t.start()
    t.join()

if __name__ == '__main__':
    func()

