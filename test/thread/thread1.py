#!/usr/bin/env python
import threading,Queue,time,sys,traceback

class easy_pool:
    def __init__(self,func):
        self.Qin  = Queue.Queue() 
        self.Qout = Queue.Queue()
        self.Qerr = Queue.Queue()
        self.Pool = []   
        self.Func=func
    def process_queue(self):
        flag='ok'
        while flag !='stop':
            flag,item=self.Qin.get() #will wait here!
            if flag=='ok':
                try:
                    self.Qout.put(self.Func(item))
                except:
                    self.Qerr.put(self.err_msg())
    def start_threads(self,num_threads=5):
        for i in range(num_threads):
             thread = threading.Thread(target=self.process_queue)
             thread.start()
             self.Pool.append(thread)
    def put(self,data,flag='ok'):
        self.Qin.put([flag,data]) 

    def get(self): return self.Qout.get() #will wait here!

    def get_errors(self):
        try:
            while 1:
                yield self.Qerr.get_nowait()
        except Queue.Empty:
            pass
    
    def get_all(self):
        try:
            while 1:
                yield self.Qout.get_nowait()
        except Queue.Empty:
            pass
        
    def stop_threads(self):
        for i in range(len(self.Pool)):
            self.Qin.put(('stop',None))
        while self.Pool:
            time.sleep(0.1)
            for index,the_thread in enumerate(self.Pool):
                if the_thread.isAlive():
                    continue
                else:
                    del self.Pool[index]
                break
    def run_all(self,asap=None,num_threads=10):
        if asap:
            self.start_threads(num_threads)
            #do nothing until 1st one arrives
            #assumes you'll get enough data for the threads not to hang
            yield self.get()
            
            while self.Qin.qsize():
                for i in self.get_all():
                    yield i
                    time.sleep(60)
            self.stop_threads()
            for i in self.get_all():
                yield i            
        else:            
            self.start_threads(num_threads)
            self.stop_threads()
            for i in self.get_all():
                yield i
    def err_msg(self):
        trace= sys.exc_info()[2]
        try:
            exc_value=str(sys.exc_value)
        except:
            exc_value=''
        return str(traceback.format_tb(trace)),str(sys.exc_type),exc_value
    def qinfo(self):
        return 'in',self.Qin.qsize(),'out',self.Qout.qsize()

def work1(item):
    time.sleep(1)
    return 'hi '+item

t=easy_pool(work1)
for i in ('a','b','c','1'): t.put(i)
for i in t.run_all(): print i
for i in t.get_errors(): print 'error %d' % i

#This turns on asap and changes the threads to 25
t2=easy_pool(work1)
#add to input queue
for i in ('d','e','f'): t2.put(i)
#start 8 threads
t2.start_threads(8)
#add more to input queue, 7 will make an error
for i in ('aa','bb','cc',7,'dd','ee','ff'): t2.put(i)

#wait here until a single result arrives
print '1st result', t2.get()

#get whatever data is available, not waiting
for i in t2.get_all(): print i
for i in t2.get_errors(): print i

#decide you've done enough work and shutdown the threads
t2.stop_threads()

#now threads have stopped, get remaining available data
for i in t2.get_all(): print i
for i in t2.get_errors(): print i
