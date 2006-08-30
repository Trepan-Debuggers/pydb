#!/usr/bin/env python

#Let us profile code which uses threads
import thread
import time
from threading import Thread

class MyThread(Thread):

    def __init__(self,bignum):

        Thread.__init__(self)
        self.bignum=bignum
    
    def run(self):

        for l in range(5):
            for k in range(self.bignum):
                res=0
                for i in range(self.bignum):
                    res+=1


def myadd_nothread(bignum):

    for l in range(5):
        for k in range(bignum):
            res=0
            for i in range(bignum):
                res+=1

    for l in range(5):
        for k in range(bignum):
            res=0
            for i in range(bignum):
                res+=1

def thread_test(bignum):
    #We create 2 Thread objects  for the 2 threads.
    thr1=MyThread(bignum)
    thr2=MyThread(bignum)

    thr1.start()
    thr2.start()

    thr1.join()
    thr2.join()
    

def test():

    bignum=20

    #Let us test the threading part

    import sys
    sys.setcheckinterval(1000)

    
    starttime=time.time()
    thread_test(bignum)
    stoptime=time.time()

    print "Running 2 threads took %.3f seconds" % (stoptime-starttime)
    
    #Now run without Threads.
    starttime=time.time()
    myadd_nothread(bignum)
    stoptime=time.time()

    print "Running Without Threads took %.3f seconds" % (stoptime-starttime)


if __name__=="__main__":

    test()
