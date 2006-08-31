# $Id: threaddbg.py,v 1.3 2006/08/31 02:52:00 rockyb Exp $

### TODO
### - set break on specific threads
### - Go over for robustness, 
### - threadframe tolerance
### More complicated:
### - Setting curframe to threads to get/set variables there?

import bdb, gdb, inspect, os, pydb, sys
from fns import *

import thread, threading

def is_in_threaddbg_dispatch(f):
    """Returns True if frame f is the threaddbg dispatch routine"""
    ## We check on the routine name and filename
    (filename, line_no, routine) = inspect.getframeinfo(f)[0:3]
    (path, basename)=os.path.split(filename)
    if routine != 'trace_dispatch' or not basename.startswith('threaddbg.py'):
        return False

    # One last check to see that local variable breadcrumb exists and
    # has the magic dynamic value. 
    if 'breadcrumb' in f.f_locals:
        if is_in_threaddbg_dispatch == f.f_locals['breadcrumb']:
            return True
    return False

## FINISH
def find_nondebug_frame(f):
    """Find the first frame that isn't a debugger frame.
    Generally we want traceback information without polluting
    it with debugger information.
        """
    """Returns the most recent frame that doesn't contain a threaddbg
    frame as its parent. Note this frame is not part of threaddg.
    If there is no frame (i.e. no thread debugging) then f would
    be returned."""
    return_frame=f
    while f:
        if is_in_threaddbg_dispatch(f):
            # Can't use previous return_frame
            return_frame = f.back
        f = f.f_back
    return return_frame

def stack_trace(obj, f):
    """A mini stack trace routine for threads."""
    f = obj.find_nondebug_frame(f)
    while f:
        is_in_threaddbg_dispatch(f)
        s = obj.format_stack_entry((f, f.f_lineno))
        obj.msg(" "*4 + s)
        f = f.f_back

class threadDbg(pydb.Pdb):
    """A class to extend the Pdb class to add thread debugging.
    The notable extensions are gdb-like:
        info thread - what threads are out there
        thread - switch thread
    """
    def __init__(self, completekey='tab', stdin=None, stdout=None):

        pydb.Pdb.__init__(self, completekey, stdin, stdout)
        self.add_hook()
        self.stack = self.curframe = self.botframe = None

        # desired_thread is the thread we want to switch to after issuing
        # a "thread <thread-name>" command.
        self.desired_thread=None

        self.systrace = False
        #self.systrace = True

        self.nothread_trace_dispatch = bdb.Bdb.trace_dispatch

        # List of threads that we know about and have the possibility
        # of switching to. This is Indexed by thread name and
        # the value is the thread id.
        self.traced = {}
        self.end_thread=-1  # Highest short name in use.
        if hasattr(sys, "_current_frames"):
            self.info_thread = self.info_thread_new
            self.do_thread   = self.new_do_thread
        #elif -- FIXME check for threadframe
        else:
            self.info_thread = self.info_thread_old
        self.infocmds.add('thread',  self.info_thread,  2, False)
        self.setcmds.add ('systrace', self.set_systrace)
        self.showcmds.add('systrace', self.show_systrace)

    def find_nondebug_frame(self, f):
        """Find the first frame that isn't a debugger frame.
        Generally we want traceback information without polluting
        it with debugger information.
        """
        if self.systrace: return f

        return_frame=f
        while f:
            if is_in_threaddbg_dispatch(f) :
                # Can't use previous return_frame
                return_frame = f.f_back
            f = f.f_back

        f = return_frame
        ### FIXME: would like a routine like is_in_threaddb_dispatch
        ### but works with threading instead. Decorating or subclassing
        ### threadding might do the trick.
        (filename, line_no, routine) = inspect.getframeinfo(f)[0:3]
        (path, basename)=os.path.split(filename)
        while basename.startswith('threading.py') and f.f_back:
            f = f.f_back
            (filename, line_no, routine) = \
                       inspect.getframeinfo(f)[0:3]
            (path, basename)=os.path.split(filename)
        return f

    def add_hook(self):
        """Set new threads to be traced. This is it's own routine
        rather than in __init__ so we can turn on/and off at will.
        """

        # threading_lock makes sure there is only one thread
        # running at a time. Later on we may want to relax this
        # condition. 
        self.threading_lock=threading.Lock()

        # threading_cond is used to indicate a particular thread
        # should get control. It's conceivable that this could be
        # combined with threading_lock but so far it seems more
        # complicated (if not error prone) that way.
        
        self.threading_cond=threading.Condition(threading.Lock())
        self.threading_imported=True
        self.running=True
        threading.settrace(self.trace_dispatch)

    def do_qt(self, arg):
        """Quit the current thread."""
        thread_name=threading.currentThread().getName()
        self.msg( "quitting thread %s"  % thread_name)
        del self.traced[thread_name]
        self.threading_lock.release()
        thread.exit()

    def new_do_thread(self, arg):
        """Use this command to switch between threads.
        The new thread ID must be currently known.

        If not thread name is given we'll give information about
        the current thread. (That is this is the same as "info thread".
        """
        if not arg:
            self.info_thread(args=arg, short_display=True)
            return

        if arg in self.traced.keys():
            cur_thread  = threading.currentThread()
            thread_name = cur_thread.getName()
            if arg == thread_name:
                self.msg("We are that thread. No switch done.")
            else:
                threads = sys._current_frames()
                t = self.traced[arg]
                if t in threads.keys():
                    frame = threads[t]
                    (filename, line_no, routine) = \
                               inspect.getframeinfo(frame)[0:3]
                    (path, basename)=os.path.split(filename)
                    ### FIXME: make into a routine and merge with
                    #### other FIXME.
                    if basename.startswith('threaddbg.py'):
                        self.msg("switching to %s" % arg)
                        self.desired_thread = arg
                        return True
                    else:
                        self.msg("Thread must be blocked in the debugger "
                                 + "to switch to it.")
                else:
                    self.msg("Can't find %s in list of active threads" %
                             arg)
        else:
            self.msg("Don't know about thread %s" % arg)
            self.info_thread(args=arg, short_display=True)
            self.msg(str(self.traced))

    # For Python before 2.5b1
    def info_thread_old(self, args, short_display=False):
        """IDs of currently known threads."""
        self.msg("Current thread is %s" %
                 threading.currentThread().getName())
        if short_display: return
        for t in threading.enumerate():
            self.msg(t)
        for thread_id in self.traced.keys():
            if self.traced[thread_id]: 
                self.msg("%s: %ld" % (str(thread_id),
                                      self.traced[thread_id]))

    # For Python on or after 2.5b1
    def info_thread_new(self, args, short_display=False):
        """IDs of currently known threads.

If no thread name is given, we list info for all threads. For exach thread
we give:
  - the class, thread name, and status as <Class(Thread-n, status)>
  - the top-most call-stack information for that thread. Generally
    the top-most calls into the debugger and dispatcher are omitted unless
    set systrace is True. If 'verbose' appended to the end of the command,
    then the entire stack trace is given for each frame.

To get the full stack trace for a specific thread pass in the thread name.
"""
        threads = sys._current_frames()

        all_verbose = len(args) == 2 and args[1].startswith('verbose')
        if len(args) > 1 and not all_verbose:
            if args[1] not in self.traced.keys():
                self.msg("Don't know about thread %s" % args[1])
                self.msg(str(self.traced))
                return
            thread_name = args[1]
            for t in threads.keys():
                if t==self.traced[thread_name]:
                    f = threads[t]
                    f = self.find_nondebug_frame(f)
                    stack_trace(self, f)
                    return

        self.msg("Current thread is %s" %
                 threading.currentThread().getName())

        if short_display: return

        for t in threads.keys():
            f = threads[t]
            f = self.find_nondebug_frame(f)

            # Print location where thread was created and line number
            s = str(threading._active[t]) + "\n    "
            s += self.format_stack_entry((f, f.f_lineno))
            self.msg(s)
            f = f.f_back
            if all_verbose:
                stack_trace(self, f)

    def print_location(self, print_line=False):
        """ Add thread name to Pdb print_location"""
        self.msg("thread %s" % threading.currentThread().getName())
        pydb.Pdb.print_location(self, print_line)

    def remove_hook(self):
        if self.threading_imported:
            threading.settrace(None)
            thread_id = thread.get_ident()
            if thread_id in self.traced.keys():
                del self.traced[thread_id]
        
    def trace_dispatch(self, frame, event, arg):
        """Called from Python when some event-like stepping or returning
        occurs
        """

        # The below variable will be used to scan down frames to determine
        # if trace_dispatch has been called. We key on the variable
        # name, method name, type of variable and even the value.

        # Note this is the first statement of this method.
        breadcrumb = is_in_threaddbg_dispatch

        # There's some locking interaction between this code and
        # threading code which can cause a deadlock.  So avoid the
        # problem rather than try to cope with it - don't trace
        # into threading.

        # FIXME the below code is not clean or reliable.

        (filename, line_no, routine) = inspect.getframeinfo(frame)[0:3]
        (path, basename)=os.path.split(filename)
        if basename.startswith('threading.py'):
            return self.trace_dispatch

        thread_name = threading.currentThread().getName()

        # This is not right either. It is a lame attempt to get around
        # hanging threading.joins()

        if self._user_requested_quit:
            self.remove_hook()
            if len(self.traced.keys())==1:
                thread.exit()
            return self.trace_dispatch

        # Record in my own table a list of thread names
        if not thread_name in self.traced.keys():
            self.traced[thread_name] = thread.get_ident()

        have_single_entry_lock = False

        while not self._user_requested_quit: 
            # See if there was a request to switch to a specific thread
            while self.desired_thread not in (None,
                                              threading.currentThread().getName()):
                self.threading_cond.acquire()
                self.threading_cond.wait()
                self.threading_cond.release()

            # One at a time, please.
            self.threading_lock.acquire()
            have_single_entry_lock = True
            if self.desired_thread in (None,
                                       threading.currentThread().getName()):
                break

            if self._user_requested_quit: break
            self.threading_lock.release()

        if self.desired_thread != None:
            # We are switching from another thread
            # If a breakpoint isn't set at the current
            # location, we should set up a temporary
            # breakpoint.
            if not self.stop_here(self.setup(frame)):
                arg = str(inspect.getlineno(frame))
                self.do_tbreak(arg)
            self.desired_thread = None

        if self._user_requested_quit:
            thread_name = threading.currentThread().getName()
            self.msg("%s (id %lu) is quitting." %
                     (thread_name, thread.get_ident()))
            if have_single_entry_lock:
                self.threading_lock.release()
            thread.exit()
            return

        if self.linetrace:
            # self.msg("thread %s event %s" % (thread_name, event))
            self.setup(frame)
            self.print_location()
        else:
            try:
                self.nothread_trace_dispatch(self, frame, event, arg)
            except bdb.BdbQuit:
                self.msg("Requesting exit from %s (id %lu)" %
                         (threading.currentThread().getName(),
                          thread.get_ident()))
                self._user_requested_quit = True
                self.threading_lock.release()
                thread.exit()
                return

        self.threading_lock.release()
        return self.trace_dispatch

    def _runscript(self, filename):
        # Start with fresh empty copy of globals and locals and tell the script
        # that it's being run as __main__ to avoid scripts being able to access
        # the tpdb.py namespace.
        mainpyfile = self.canonic(filename)
        globals_ = {"__name__"     : "__main__",
                    "__file__"     : mainpyfile,
                    "__builtins__" : __builtins__,
                    }

        ### FIXME Add other stuff from pydbcmd's _runscript
        locals_ = globals_
        statement = 'execfile( "%s")' % filename
        self.run(statement, globals=globals_, locals=locals_)

    def set_systrace(self, args):
        """Set whether tracebacks inlcude debugger and threading routines"""
        try:
            self.systrace = self.get_onoff(args[1])
        except ValueError:
            pass

    def show_systrace(self, args):
        """Showt whether tracebacks inlcude debugger and threading routines"""
        self.msg("Systrace is %s." % show_onoff(self.systrace))
