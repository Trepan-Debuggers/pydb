# $Id: threaddbg.py,v 1.29 2006/10/25 10:50:12 rockyb Exp $

### TODO
### - Go over for robustness, 

import bdb, inspect, os, pydb, sys
import fns

import thread, threading
from gdb import Restart

def id2threadName(thread_id):
    """Turn a thread id into a thread name. Works in Python 2.5 or greater."""
    return threading.Thread.getName(threading._active[thread_id])

def is_in_threaddbg_dispatch(f):
    """Returns True if frame f is the threaddbg dispatch routine"""

    ## First check that the routine name and prefix of the filename's
    ## basename are what we expect.

    (filename, line_no, routine) = inspect.getframeinfo(f)[0:3]
    (path, basename)=os.path.split(filename)
    ## print routine, filename
    if routine != 'trace_dispatch' or not basename.startswith('threaddbg.py'):
        return False

    # Next check to see that local variable breadcrumb exists and
    # has the magic dynamic value. 
    if 'breadcrumb' in f.f_locals:
        if is_in_threaddbg_dispatch == f.f_locals['breadcrumb']:
            return True
    return False

def is_in_threaddbg(f):
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
            return_frame = f.f_back
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

        # desired_thread is a lists of threads allowed to run.
        # It is part of the mechanism used to switch threads and thus
        # We set in the "thread" command. It is cleared then in the
        # dispatcher after getting one of the desired threads. 
        # If the variable is None than any thread can run.
        self.desired_thread=None

        self.thread_id               = thread.get_ident()
        self.thread_name             = threading.currentThread().getName()
        self.curframe_thread_name    = self.thread_name
        self.nothread_do_break       = pydb.Pdb.do_break
        self.nothread_do_tbreak      = pydb.Pdb.do_tbreak
        self.nothread_trace_dispatch = bdb.Bdb.trace_dispatch
        self.nothread_quit           = pydb.Pdb.do_quit

        # List of threads that we know about and have the possibility
        # of switching to. This is Indexed by thread name and
        # the value is the thread id.
        self.traced = {}
        self.end_thread=-1  # Highest short name in use.
        if hasattr(sys, "_current_frames"):
            self.do_tracethread  = self.new_do_tracethread
            ## self.do_thread       = self.new_do_thread
            self.info_thread     = self.info_thread_new
        else:
            try:
                import threadframe
                self.do_tracethread = self.threadframe_do_tracethread
                self.info_thread    = self.info_threadframe
            except:
                self.info_thread = self.info_thread_old
        ## self.traceall()
        self.infocmds.add('thread',  self.info_thread,  2, False)

    def find_nondebug_frame(self, f):
        """Find the first frame that isn't a debugger frame.
        Generally we want traceback information without polluting
        it with debugger information.
        """
        if self.dbg_pydb: return f

        f = is_in_threaddbg(f)

        ### FIXME: would like a routine like is_in_threaddb_dispatch
        ### but works with threading instead. Decorating or subclassing
        ### threadding might do the trick.
        (filename, line_no, routine) = inspect.getframeinfo(f)[0:3]
        (path, basename)=os.path.split(filename)
        while (basename.startswith('threading.py') or
               basename.startswith('gdb.py') or
               basename.startswith('threaddbg.py') or
               basename.startswith('subcmd.py') or
               basename.startswith('pydb.py') or
               routine == 'trace_dispatch_gdb') and f.f_back:
            f = f.f_back
            (filename, line_no, routine) = \
                       inspect.getframeinfo(f)[0:3]
            (path, basename)=os.path.split(filename)
        return f

    def get_threadframe_frame(self, thread_name):
        """Return the frame having thread name that we look up
        in self.traced."""
        if thread_name not in self.traced.keys():
            return None
        import threadframe
        frames = threadframe.dict()
        thread_id = self.traced[thread_name]
        return frames[thread_id]

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

    def do_break(self, arg, temporary=0, thread_name=None):
        """b(reak) {[file:]lineno | function} [thread Thread-name] [, condition]
With a line number argument, set a break there in the current
file.  With a function name, set a break at first executable line
of that function.  Without argument, list all breaks.  If a second
argument is present, it is a string specifying an expression
which must evaluate to true before the breakpoint is honored.

The line number may be prefixed with a filename and a colon,
to specify a breakpoint in another file (probably one that
hasn't been loaded yet).  The file is searched for on sys.path;
the .py suffix may be omitted.

If a thread name is given we will stop only if the the thread has that name;
dot (.) can be used to indicate the current thread."""
        
        # Decorate non-thread break to strip out 'thread Thread-name'
        args = arg.split()
        if len(args) > 2 and args[1] == 'thread':
            thread_name = args[2]
            if thread_name == '.':
                thread_name = threading.currentThread().getName()
            del args[1:3]
            arg = ' '.join(args)
        if thread_name and thread_name not in self.traced.keys():
            self.msg("Don't know about thread %s" % thread_name)
            if not fns.get_confirmation(self,
                                        'Really set anyway (y or n)? '):
                return
        self.nothread_do_break(self, arg, temporary=temporary,
                               thread_name=thread_name)

    def do_frame(self, arg):
        """frame [Thread-Name] frame-number
Move the current frame to the specified frame number. If a
Thread-Name is given, move the current frame to that. Dot (.) can be used
to indicate the name of the current frame.

0 is the most recent frame. A negative number indicates position from
the other end.  So 'frame -1' moves when gdb dialect is in
effect moves to the oldest frame, and 'frame 0' moves to the
newest frame."""
        args = arg.split()
        if len(args) > 0:
            try:
                int(arg)
                # Must be frame command without a thread name
            except ValueError:
                thread_name = args[0]
                if thread_name == '.':
                    thread_name = threading.currentThread().getName()
                if thread_name not in self.traced.keys():
                    self.msg("Don't know about thread %s" % thread_name)
                    return
                t = self.traced[thread_name]
                if hasattr(sys, '_current_frames'):
                    threads = sys._current_frames()
                    if t in threads.keys():
                        self.curframe_thread_name = thread_name
                        frame                     = threads[t]
                else:
                    try:
                        import threadframe
                        frame = self.get_threadframe_frame(thread_name)
                        if frame is None:
                            self.msg("Can't find thread %s" % thread_name)
                            return
                    except:
                        self.msg("Frame selection not supported. Upgrade to")
                        self.msg("Python 2.5 or install threadframe.")
                        return

                newframe = self.find_nondebug_frame(frame)
                if newframe is not None:  frame = newframe
                self.stack, self.curindex = self.get_stack(frame, None)
                if len(args) == 1:
                    arg = '0'
                else:
                    arg = ' '.join(args[1:])

        self.thread_name = threading.currentThread().getName()

        pydb.Pdb.do_frame(self, arg)

    def do_quit(self, arg):
        """If all threads are blocked in the debugger, tacitly quit. If some are not, then issue a warning and prompt for quit."""
        really_quit = True
        threads = sys._current_frames()
        threading_list = threading.enumerate()
        if (len(threading_list) == 1 and
            threading_list[0].getName() == 'MainThread'):
            # We just have a main thread so that's safe to quit
            return self.nothread_quit(self, arg)
            
        for thread_obj in threading_list:
            thread_name = thread_obj.getName() 
            if not thread_name in self.traced.keys():
                self.msg("I don't know about state of %s"
                         % thread_name)
                really_quit = False
                break
            t = self.traced[thread_name]
            if t in threads.keys():
                frame = threads[t]
                if not is_in_threaddbg(frame):
                    self.msg("Thread %s is not blocked by the debugger."
                             % thread_name)
                    really_quit = False
                    break
            else:
                self.msg("Thread ID for thread %s not found. Weird."
                         % thread_name)
                really_quit = False
                break
        if not really_quit:
            really_quit = fns.get_confirmation(self,
                                               'Really quit anyway (y or n)? ',
                                               True)
        self.msg("Quit for threading not fully done yet. Try kill.")
        return
        if really_quit:
            self.nothread_quit(self, arg)

    def do_qt(self, arg):
        """Quit the current thread."""
        thread_name=threading.currentThread().getName()
        self.msg( "quitting thread %s"  % thread_name)
        del self.traced[thread_name]
        self.threading_lock.release()
        thread.exit()

    def do_tbreak(self, arg):
        """tbreak {[file:]lineno | function} [thread Thread-name] [, condition]

Set a temporary breakpoint. Arguments are like the "break" command.
Like "break" except the breakoint is only temporary,
so it will be deleted when hit.

If a thread name is given we will stop only if the the thread has that name."""
        # Decorate non-thread break to strip out 'thread Thread-name'
        args = arg.split()
        thread_name = None
        if len(args) > 2 and args[1] == 'thread':
            thread_name = args[2]
            if thread_name == '.':
                thread_name = threading.currentThread().getName()
            if thread_name not in self.traced.keys():
                self.msg("Don't know about thread %s" % thread_name)
                if not fns.get_confirmation(self,
                                            'Really set anyway (y or n)? '):
                    return
            del args[1:3]
            arg = ' '.join(args)
        self.nothread_do_tbreak(self, arg, thread_name)

    def do_tracethread(self, args):

        """Set to trace all threads. However Python 2.5 or the
threadframe module is needed for this and it appear you have neither
installed."""

        pass

    def new_do_tracethread(self, args):

        """Make sure all frames are set to be traced under the Python
2.5 regime. This would needed if we started debugging mid-way via say
set_trace and threads have already been created.  """

        threads = sys._current_frames()
        for t in threads.keys():
            frame = self.find_nondebug_frame(threads[t])
            self.set_trace(frame)

    def threadframe_do_tracethread(self, args):

        """Make sure all frames are set to be traced under the
threadframe regime. This would needed if we started debugging mid-way
via say set_trace and threads have already been created."""

        import threadframe
        frames = threadframe.dict()
        for frame in frames:
            frame = self.find_nondebug_frame(frame)
            self.set_trace(frame)

    def do_where(self, arg):
        """where [count]

Print a stack trace, with the most recent frame at the top.  With a
positive number, print at most many entries.  An arrow indicates the
'current frame', which determines the context of most commands.  'bt'
and 'T' are short command names for this."""
        # Decorate old 'where' to show current thread.
        self.print_frame_thread()
        pydb.Pdb.do_where(self, arg)
        
    # For Python before 2.5b1 and no threadframe module
    def info_thread_old(self, args, short_display=False):
        """IDs of currently known threads."""
        self.thread_name = threading.currentThread().getName()
        if len(args) == 2:
            if args[1].startswith('terse'):
                self.info_thread_terse()
                return

        if len(args) > 1:
            if args[1] not in self.traced.keys():
                self.msg("Don't know about thread %s" % args[1])
                self.info_thread_terse()
                return

        self.msg("Current thread is %s" % self.thread_name)

        if len(args) == 3 and args[2].startswith('terse'):
            self.info_thread_terse(args[2])
            return

        for t in threading.enumerate():
            self.msg(t)
        self.info_thread_terse()

    ## FIXME remove common code with info_thread_new
    # For Python with threadframe
    def info_threadframe(self, args, short_display=False):
        """info thread [thread-name] [terse|verbose]
List all currently-known thread name(s).

If no thread name is given, we list info for all threads. A terse
listing just gives the thread name and thread id.

If 'verbose' appended to the end of the command, then the entire
stack trace is given for each frame.
"""
        import threadframe
        frames = threadframe.dict()

        self.thread_name = threading.currentThread().getName()
        all_verbose = False
        if len(args) == 2:
            if args[1].startswith('verbose'):
                all_verbose = True
            elif args[1].startswith('terse'):
                self.info_thread_terse()
                return

        if len(args) > 1 and not all_verbose:
            thread_name = args[1]
            if thread_name == '.':
                thread_name = threading.currentThread().getName()
            if thread_name not in self.traced.keys():
                self.msg("Don't know about thread %s" % thread_name)
                self.info_thread_terse()
                return

            thread_id = self.traced[args[1]]
            frame     = frames[thread_id]
            frame     = self.find_nondebug_frame(frame)
            stack_trace(self, frame)
            return

        thread_id2name = {}
        for thread_name in self.traced.keys():
            if self.get_threadframe_frame(thread_name) is not None:
                thread_id2name[self.traced[thread_name]] = thread_name

        # FIXME: sort by thread name
        for thread_id in frames.keys():
            s = ''
            # Print location where thread was created and line number
            if thread_id in thread_id2name.keys():
                thread_name = thread_id2name[thread_id]
                if thread_name == self.thread_name:
                    prefix='-> '
                else:
                    prefix='   '
                s += "%s%s\n" % (prefix, thread_name)
                frame = self.find_nondebug_frame(frames[thread_id])
                s += self.format_stack_entry((frame, frame.f_lineno))
                self.msg('-' * 40)
                self.msg(s)
                frame = frame.f_back
                if all_verbose and frame:
                    stack_trace(self, frame)

    ## FIXME remove common code with info_thread_new
    # For Python on or after 2.5b1
    def info_thread_new(self, args, short_display=False):
        """info thread [thread-name] [terse|verbose]
List all currently-known thread name(s).

If no thread name is given, we list info for all threads. Unless a
terse listing, for each thread we give:

  - the class, thread name, and status as <Class(Thread-n, status)>
  - the top-most call-stack information for that thread. Generally
    the top-most calls into the debugger and dispatcher are omitted unless
    set debug-pydb is True.

    If 'verbose' appended to the end of the command, then the entire
    stack trace is given for each frame.
    If 'terse' is appended we just list the thread name and thread id.

To get the full stack trace for a specific thread pass in the thread name.
"""
        self.thread_name = threading.currentThread().getName()
        threads = sys._current_frames()

        all_verbose = False
        if len(args) == 2:
            if args[1].startswith('verbose'):
                all_verbose = True
            elif args[1].startswith('terse'):
                self.info_thread_terse()
                return

        if len(args) > 1 and not all_verbose:
            thread_name = args[1]
            if thread_name == '.':
                thread_name = threading.currentThread().getName()
            if thread_name not in self.traced.keys():
                self.msg("Don't know about thread %s" % thread_name)
                self.info_thread_terse()
                return

            for t in threads.keys():
                if t==self.traced[thread_name]:
                    frame = threads[t]
                    frame = self.find_nondebug_frame(frame)
                    stack_trace(self, frame)
                    return

        thread_key_list = threads.keys()
        thread_key_list.sort(key=id2threadName)
        for t in thread_key_list:
            frame = threads[t]
            frame = self.find_nondebug_frame(frame)

            s = ''
            # Print location where thread was created and line number
            if t in threading._active:
                thread_name = id2threadName(t)
                if thread_name == self.thread_name:
                    prefix='-> '
                else:
                    prefix='   '
                s += "%s%s" % (prefix, str(threading._active[t]))
                if all_verbose:
                    s += ": %d" % t
                s += "\n    "
            s += self.format_stack_entry((frame, frame.f_lineno))
            self.msg('-' * 40)
            self.msg(s)
            frame = frame.f_back
            if all_verbose and frame:
                stack_trace(self, frame)

    def info_thread_line(self, thread_name):
        if thread_name == self.thread_name:
            prefix='-> '
        else:
            prefix='   '

        self.msg("%s%s: %d" % (prefix, thread_name,
                               self.traced[thread_name]))

    def info_thread_terse(self, arg=None):
        if arg is not None:
            thread_name = arg
            if thread_name in self.traced_keys():
                self.info_thread_line(thread_name)
            else:
                self.msg("Don't know about thread %s" % thread_name)
            return

        # Show all threads
        thread_name_list = self.traced.keys()
        thread_name_list.sort()
        for thread_name in thread_name_list:
            self.info_thread_line(thread_name)
                
##     def new_do_thread(self, arg):
##         """thread [thread-name1 [thread-name2]..]

## Use this command to specifiy a set of threads which you
## want to switch to. The new thread name must be currently known by the
## debugger.

## If no thread name is given, we'll give information about
## the current thread. (That is this is the same as "info thread terse"."""
##         args = arg.split()
##         if len(args) == 0:
##             self.info_thread(args=arg, short_display=True)
##             return

##         retval = False
##         for thread_name in args:
##             if thread_name in self.traced.keys():
##                 cur_thread  = threading.currentThread()
##                 threads = sys._current_frames()
##                 t = self.traced[thread_name]
##                 if t in threads.keys():
##                     frame = threads[t]
##                     if is_in_threaddbg(frame):
##                         if len(args) == 1:
##                             if thread_name == cur_thread.getName():
##                                 self.msg("We are thread %s. No switch done."
##                                          % thread_name)
##                                 continue
##                             self.msg("Switching to %s" % thread_name)
##                         else:
##                             self.msg(("Adding %s to list of switchable " +
##                                       "threads") % thread_name)

##                         if self.desired_thread:
##                             self.desired_thread.append(thread_name)
##                         else:
##                             self.desired_thread = [thread_name]
##                         retval = True
##                     else:
##                         self.msg("Thread %s is not currently blocked in the"
##                                  + "debugger.")
##                 else:
##                     self.msg("Can't find %s in list of active threads" %
##                              thread_name)
##             else:
##                 self.msg("Don't know about thread %s" % thread_name)

##         if not retval:
##             self.msg("Here are the threads I know about:")
##             self.info_thread(args=[thread_name], short_display=True)
##             self.msg(str(self.traced))
##             return False
##         else:
##             # Here's where we arrange to switch threads
##             self.threading_cond.acquire()
##             self.threading_cond.notify()
##             self.threading_cond.release()
##         return retval

    def print_frame_thread(self):
        """Print the thread name and current frame thread name to Pdb's
        print_location, if it is different from the thread name."""
        thread_name = threading.currentThread().getName()
        if self.curframe_thread_name != thread_name:
            self.msg("Frame thread is %s, Current thread is %s" %
                     (self.curframe_thread_name, thread_name))
        else:
            self.msg("Current thread is %s" % thread_name)

    def print_location(self, print_line=False):
        """Add thread name and current frame thread name to Pdb's
        print_location, if it is different from the thread name."""
        # Decorator pattern
        self.print_frame_thread()
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

        # FIXME: the below code is not clean or reliable.
        #        Make more like is_in_threaddbg
        (filename, line_no, routine) = inspect.getframeinfo(frame)[0:3]
        (path, basename)=os.path.split(filename)
        if basename.startswith('threading.py'):
            return self.trace_dispatch

        # Note: until locking is done below we should not update and
        # save self.thread_name and self.thread_id but use
        # threading.currentThread().getname and thread.get_ident() instead.

        last_thread_id   = self.thread_id

        # Record in my own table a list of thread names
        if not threading.currentThread().getName() in self.traced.keys():
            self.traced[threading.currentThread().getName()] = \
                                                             thread.get_ident()

        have_single_entry_lock = False

        while not self._user_requested_quit: 
            # See if there was a request to switch to a specific thread
            while self.desired_thread is not None \
                  and self.thread_name not in self.desired_thread:
                self.threading_cond.acquire()
                self.threading_cond.wait()
                self.threading_cond.release()

            # One at a time, please.
            self.threading_lock.acquire()
            have_single_entry_lock = True
            if self.desired_thread is None \
              or threading.currentThread().getName() in self.desired_thread:
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
            self.msg("%s (id %lu) is quitting." %
                     (threading.currentThread().getName(), thread.get_ident()))
            if have_single_entry_lock:
                self.threading_lock.release()
            thread.exit()
            return

        # Because of locks above there should not be any chance
        # that the following assignments will change during the course
        # of debugger command loop.
        self.curframe_thread_name = self.thread_name = \
                                    threading.currentThread().getName()
        self.thread_id   = thread.get_ident()

        if self.linetrace:
            # self.msg("thread %s event %s" % (thread_name, event))
            self.setup(frame)
            self.print_location()
        else:
            while True:
                try:
                    if self.stepping and last_thread_id != thread.get_ident():
                        botframe = self.botframe
                        self.botframe = frame
                        #print "Thread switch %s %d %d" % (self.thread_name,
                        #                                  last_thread_id,
                        #                                  self.thread_id)
                    self.nothread_trace_dispatch(self, frame, event, arg)
                    break
                except Restart:
                    sys.argv = list(self._program_sys_argv)
                    self.msg("'run' command not implemented for thread " +
                             "debugging. Try 'restart'.")
                    # self.msg("Should Restart %s with arguments:\n\t%s"
                    #         % (self.filename(sys.argv[0]),
                    #            " ".join(self._program_sys_argv[1:])))
                except bdb.BdbQuit:
                    self.msg("Requesting exit from %s (id %lu)" %
                             (threading.currentThread().getName(),
                              thread.get_ident()))
                    self._user_requested_quit = True
                    self.desired_thread = None
                    self.threading_cond.acquire()
                    self.threading_cond.notify()
                    self.threading_cond.release()
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

        locals_ = globals_
        statement = 'execfile( "%s")' % filename
        self.running = True
        self.run(statement, globals=globals_, locals=locals_)
