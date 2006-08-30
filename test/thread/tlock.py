#!/usr/bin/env python
import sys, pydb
import time
import thread

def myfunction(string,sleeptime,lock,*args):
    pydb.set_trace()
    while 1:
	#entering critical section
        lock.acquire() 
        print string," Now Sleeping after Lock acquired for ",sleeptime
        time.sleep(sleeptime) 
        print string," Now releasing lock and then sleeping again"
        lock.release()
	#exiting critical section
        time.sleep(sleeptime) # why?

if __name__=="__main__":

    lock=thread.allocate_lock()
    thread.start_new_thread(myfunction,("Thread No:1",1,lock))
    thread.start_new_thread(myfunction,("Thread No:2",1,lock))

    while 1:pass

