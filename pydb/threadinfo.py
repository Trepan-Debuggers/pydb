"""Routines to show Thread information
$Id: threadinfo.py,v 1.5 2007/02/10 01:56:58 rockyb Exp $"""
# -*- coding: utf-8 -*-
#   Copyright (C) 2006, 2007 Rocky Bernstein
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.

import inspect, os, sys, threading

def find_nondebug_frame(obj, f):
    """Find the first frame that isn't a debugger frame.
    Generally we want traceback information without polluting
    it with debugger information.
    """
    if obj.dbg_pydb: return f

    f = obj.is_in_dbg(f)

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
    frame as its parent. Note this frame is not part of threaddbg.
    If there is no frame (i.e. no thread debugging) then f would
    be returned."""
    return_frame=f
    while f:
        if is_in_threaddbg_dispatch(f):
            # Can't use previous return_frame
            return_frame = f.f_back
        f = f.f_back
    return return_frame

def is_in_gdb_dispatch(f):
    """Returns True if frame f is the threaddbg dispatch routine"""

    ## First check that the routine name and prefix of the filename's
    ## basename are what we expect.

    (filename, line_no, routine) = inspect.getframeinfo(f)[0:3]
    (path, basename)=os.path.split(filename)
    ## print routine, filename
    if (routine != 'trace_dispatch_gdb' or not basename.startswith('gdb.py')):
        return False

    # Next check to see that local variable breadcrumb exists and
    # has the magic dynamic value. 
    if 'breadcrumb' in f.f_locals:
        if is_in_gdb_dispatch == f.f_locals['breadcrumb']:
            return True
    return False

def is_in_gdb(f):
    """Find the first frame that isn't a debugger frame.
    Generally we want traceback information without polluting
    it with debugger information.
        """
    """Returns the most recent frame that doesn't contain a gdb_dbg
    frame as its parent. Note this frame is not part of dbg.
    If there is no frame (i.e. no thread debugging) then f would
    be returned."""
    return_frame=f
    while f:
        if is_in_gdb_dispatch(f):
            # Can't use previous return_frame
            return_frame = f.f_back
        f = f.f_back
    return return_frame

def stack_trace(obj, f):
    """A mini stack trace routine for threads."""
    f = find_nondebug_frame(obj, f)
    while f:
        is_in_threaddbg_dispatch(f)
        s = obj.format_stack_entry((f, f.f_lineno))
        obj.msg(" "*4 + s)
        f = f.f_back

# For Python before 2.5b1 and no threadframe module
def info_thread_old(obj, args, short_display=False):
    """List all currently-known thread names.

This routine is used when the version of Python is prior to 2.5 and
threadframe has not been installed."""

    obj.thread_name = threading.currentThread().getName()
    if len(args) == 2:
        if args[1].startswith('terse'):
            obj.info_thread_terse()
            return

    if len(args) > 1:
        if hasattr(obj, "traced"):
            if args[1] not in obj.traced.keys():
                obj.msg("Don't know about thread %s" % args[1])
                obj.info_thread_terse()
                return
        else:
            obj.errmsg("thread support not enabled; use --threading option")
            return

    obj.msg("Current thread is %s" % obj.thread_name)

    if len(args) == 3 and args[2].startswith('terse'):
        obj.info_thread_terse(args[2])
        return

    for t in threading.enumerate():
        obj.msg(t)
    obj.info_thread_terse()
    return

## FIXME remove common code with info_thread_new
# For Python with threadframe
def info_threadframe(obj, args, short_display=False):
    """List all currently-known thread names.

  info thread [thread-name|thread-id] [terse|verbose]

If no thread name is given, we list info for all threads. A terse
listing just gives the thread name and thread id.

If 'verbose' appended to the end of the command, then the entire
stack trace is given for each frame.

This routine uses threadframe. Better support however is available starting
with Python version 2.5."""
    obj.thread_name = threading.currentThread().getName()
    threads = sys._current_frames()

    all_verbose = False
    if len(args) == 2:
        if args[1].startswith('verbose'):
            all_verbose = True
        elif args[1].startswith('terse'):
            obj.info_thread_terse()
            return

    if len(args) > 1 and not all_verbose:
        thread_name = args[1]
        if thread_name == '.':
            thread_name = threading.currentThread().getName()
        try:
            thread_id = int(thread_name)
            if thread_id not in threads.keys():
                obj.msg("Don't know about thread number %s" % thread_name)
                obj.info_thread_terse()
                return
        except ValueError:
            if thread_name not in obj.traced.keys():
                obj.msg("Don't know about thread %s" % thread_name)
                obj.info_thread_terse()
                return
            thread_id = obj.traced[thread_name]

        frame = threads[thread_id]
        frame = find_nondebug_frame(obj, frame)
        stack_trace(obj, frame)
        return

    thread_id2name = {}
    if hasattr(obj, "traced"):
        for thread_name in obj.traced.keys():
            if obj.get_threadframe_frame(thread_name) is not None:
                thread_id2name[obj.traced[thread_name]] = thread_name

    # Show info about *all* threads
    # FIXME: sort by thread name
    for thread_id in threads.keys():
        s = ''
        # Print location where thread was created and line number
        if thread_id in thread_id2name.keys():
            thread_name = thread_id2name[thread_id]
            if thread_name == obj.thread_name:
                prefix='-> '
            else:
                prefix='   '
            s += "%s%s" % (prefix, thread_name)
            if all_verbose:
                s += ": %d" % thread_id
        else:
            s += "    thread id: %d" % thread_id

        s += "\n    "
        frame = find_nondebug_frame(obj, threads[thread_id])
        s += obj.format_stack_entry((frame, frame.f_lineno))
        obj.msg('-' * 40)
        obj.msg(s)
        frame = frame.f_back
        if all_verbose and frame:
            stack_trace(obj, frame)
    return False

## FIXME remove common code with info_thread_new
# For Python on or after 2.5b1
def info_thread_new(obj, args, short_display=False):
    """List all currently-known thread names.

  info thread [thread-name|thread-number] [terse|verbose]

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

This is the Python 2.5 version of this routine."""

    obj.thread_name = threading.currentThread().getName()
    threads = sys._current_frames()

    all_verbose = False
    if len(args) == 2:
        if args[1].startswith('verbose'):
            all_verbose = True
        elif args[1].startswith('terse'):
            obj.info_thread_terse()
            return

    if len(args) > 1 and not all_verbose:
        thread_name = args[1]
        if thread_name == '.':
            thread_name = threading.currentThread().getName()
        try:
            thread_id = int(thread_name)
            if thread_id not in threads.keys():
                obj.msg("Don't know about thread number %s" % thread_name)
                obj.info_thread_terse()
                return
        except ValueError:
            if (not hasattr(obj, "traced")
                or thread_name not in obj.traced.keys()):
                obj.msg("Don't know about thread %s" % thread_name)
                obj.info_thread_terse()
                return
            thread_id = obj.traced[thread_name]

        frame = threads[thread_id]
        frame = find_nondebug_frame(obj, frame)
        stack_trace(obj, frame)
        return

    # Show info about *all* threads
    thread_key_list = threads.keys()
    thread_key_list.sort(key=id2threadName)
    for thread_id in thread_key_list:
        frame = threads[thread_id]
        frame = find_nondebug_frame(obj, frame)

        s = ''
        # Print location where thread was created and line number
        if thread_id in threading._active:
            thread_name = id2threadName(thread_id)
            if thread_name == obj.thread_name:
                prefix='-> '
            else:
                prefix='   '
            s += "%s%s" % (prefix, str(threading._active[thread_id]))
            if all_verbose:
                s += ": %d" % thread_id
        else:
            s += "    thread id: %d" % thread_id
        s += "\n    "
        s += obj.format_stack_entry((frame, frame.f_lineno))
        obj.msg('-' * 40)
        obj.msg(s)
        frame = frame.f_back
        if all_verbose and frame:
            stack_trace(obj, frame)
    return False

def info_thread_line(obj, thread_name):
    prefix='   '
    if not hasattr(obj, "thread_name"):
        obj.msg("%s%s" % (prefix, thread_name))
        return

    if thread_name == obj.thread_name:
        prefix='-> '

    obj.msg("%s%s: %d" % (prefix, thread_name,
                           obj.traced[thread_name]))
    return

def info_thread_missing(obj):
    """Show information about threads we might not know about"""
    if not hasattr(obj, "traced"): return
    if (hasattr(sys, "_current_frames") and 
        len(obj.traced) != len(sys._current_frames())):
        frames = sys._current_frames()
        thread_ids = frames.keys()
        obj.msg("Untraced/unknown threads:")
        for thread_id in thread_ids:
            if thread_id not in obj.traced.values():
                obj.msg("\t%d" % thread_id)
    return

def info_thread_terse(obj, arg=None):
    if arg is not None:
        thread_name = arg
        if thread_name in obj.traced_keys():
            obj.info_thread_line(thread_name)
        else:
            obj.msg("Don't know about thread name %s" % thread_name)
        return

    # Show all threads
    thread_name_list = obj.traced.keys()
    thread_name_list.sort()
    for thread_name in thread_name_list:
        obj.info_thread_line(thread_name)
    obj.info_thread_missing()
    return False
                
