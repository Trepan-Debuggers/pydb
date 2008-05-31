"""$Id: pydbbdb.py,v 1.45 2008/05/31 11:49:01 rockyb Exp $
Routines here have to do with the subclassing of bdb.  Defines Python
debugger Basic Debugger (Bdb) class.  This file could/should probably
get merged into bdb.py
"""
import bdb, inspect, linecache, time, types
from repr import Repr
from fns import *
## from complete import rl_complete

class Bdb(bdb.Bdb):

    # Additional levels call frames usually on the stack.
    # Perhaps should be an instance variable?
    extra_call_frames = 7  # Yes, it's really that many!

    def __init__(self):
        bdb.Bdb.__init__(self)

        self.bdb_set_trace   = bdb.Bdb.set_trace
        ## self.complete        = lambda arg: complete.rl_complete(self, arg)
        
        # Create a custom safe Repr instance and increase its maxstring.
        # The default of 30 truncates error messages too easily.
        self._repr = Repr()
        self._repr.maxstring = 100
        self._repr.maxother  = 60
        self._repr.maxset    = 10
        self._repr.maxfrozen = 10
        self._repr.array     = 10
        self._saferepr = self._repr.repr

        # A 0 value means stop on this occurrence. A positive value means to
        # skip that many more step/next's.
        self.step_ignore      = 0

        # Do we want to show/stop at def statements before they are run?
        self.deftrace         = False
        return

    def __print_call_params(self, frame):
        "Show call paramaters and values"
        self.setup(frame)

        # Does sure format_stack_entry have an 'include_location' parameter?
        fse_code = self.format_stack_entry.func_code
        fse_args = fse_code.co_varnames
        if 'include_location' in fse_args:
            self.msg(self.format_stack_entry(self.stack[-1],
                                             include_location=False))
        else:
            self.msg(self.format_stack_entry(self.stack[-1]))

    def __print_location_if_trace(self, frame, include_fntrace=True):
        if self.linetrace or (self.fntrace and include_fntrace):
            self.setup(frame)
            self.print_location(print_line=True)
            self.display.displayAny(self.curframe)
            if self.linetrace_delay:
                time.sleep(self.linetrace_delay)

    def bp_commands(self, frame):

        """Call every command that was set for the current
        active breakpoint (if there is one) Returns True if
        the normal interaction function must be called,
        False otherwise """

        # self.currentbp is set in bdb.py in bdb.break_here if
        # a breakpoint was hit

        if getattr(self,"currentbp",False) and self.currentbp in self.commands:
            currentbp = self.currentbp
            self.currentbp = 0
            lastcmd_back = self.lastcmd
            self.setup(frame, None)
            for line in self.commands[currentbp]:
                self.onecmd(line)
            self.lastcmd = lastcmd_back
            if not self.commands_silent[currentbp]:
                self.print_location(print_line=self.linetrace)
            if self.commands_doprompt[currentbp]:
                self.cmdloop()
            self.forget()
            return False
        return True

    def is_running(self):
        if self.running: return True
        self.errmsg('The program being debugged is not being run.')
        return False

    def lookupmodule(self, filename):
        """Helper function for break/clear parsing -- may be overridden.

        lookupmodule() translates (possibly incomplete) file or module name
        into an absolute file name.
        """
        if os.path.isabs(filename) and  os.path.exists(filename):
            return filename
        f = os.path.join(sys.path[0], filename)
        if  os.path.exists(f) and self.canonic(f) == self.mainpyfile:
            return f
        root, ext = os.path.splitext(filename)
        if ext == '':
            filename = filename + '.py'
        if os.path.isabs(filename):
            return filename
        for dirname in sys.path:
            while os.path.islink(dirname):
                dirname = os.readlink(dirname)
            fullname = os.path.join(dirname, filename)
            if os.path.exists(fullname):
                return fullname
        return None

    # Override Bdb methods

    def bpprint(self, bp, out=None):
        if bp.temporary:
            disp = 'del  '
        else:
            disp = 'keep '
        if bp.enabled:
            disp = disp + 'y  '
        else:
            disp = disp + 'n  '
        self.msg('%-4dbreakpoint    %s at %s:%d' %
                 (bp.number, disp, self.filename(bp.file), bp.line), out)
        if bp.cond:
            self.msg('\tstop only if %s' % (bp.cond))
        if bp.ignore:
            self.msg('\tignore next %d hits' % (bp.ignore), out)
        if (bp.hits):
            if (bp.hits > 1): ss = 's'
            else: ss = ''
            self.msg('\tbreakpoint already hit %d time%s' %
                     (bp.hits, ss), out)

    def output_break_commands(self):
        "Output a list of 'break' commands"
        # FIXME: for now we ae going to assume no breakpoints set
        # previously
        bp_no = 0 
        out = []
        for bp in bdb.Breakpoint.bpbynumber:
            if bp:
                bp_no += 1
                if bp.cond: 
                    condition = bp.cond
                else:
                    condition = ''
                out.append("break %s:%s%s" % 
                           (self.filename(bp.file), bp.line, condition))
                if not bp.enabled:
                    out.append("disable %s" % bp_no)
        return out

    def break_here(self, frame):
        """This routine is almost copy of bdb.py's routine. Alas what pdb
        calls clear gdb calls delete and gdb's clear command is different.
        I tried saving/restoring method names, but that didn't catch
        all of the places break_here was called.
        """
        filename = self.canonic(frame.f_code.co_filename)
        if not filename in self.breaks:
            return False
        lineno = frame.f_lineno
        if not lineno in self.breaks[filename]:
            # The line itself has no breakpoint, but maybe the line is the
            # first line of a function with breakpoint set by function name.
            lineno = frame.f_code.co_firstlineno
            if not lineno in self.breaks[filename]:
                return False

        # flag says ok to delete temp. bp
        (bp, flag) = bdb.effective(filename, lineno, frame)
        if bp:
            ## This is new when we have thread debugging.
            self.currentbp = bp.number
            if hasattr(bp, 'thread_name') and hasattr(self, 'thread_name') \
                   and bp.thread_name != self.thread_name:
                    return False
            if (flag and bp.temporary):
                #### ARG. All for the below name change.
                self.do_delete(str(bp.number))
            return True
        else:
            return False

    def canonic(self, filename):

        """ Overrides bdb canonic. We need to ensure the file
        we return exists! """

        if filename == "<" + filename[1:-1] + ">":
            return filename
        canonic = self.fncache.get(filename)
        if not canonic:
            lead_dir = filename.split(os.sep)[0]
            if lead_dir == os.curdir or lead_dir == os.pardir:
                # We may have invoked the program from a directory
                # other than where the program resides. filename is
                # relative to where the program resides. So make sure
                # to use that.
                canonic = os.path.abspath(os.path.join(self.main_dirname,
                                                       filename))
            else:
                canonic = os.path.abspath(filename)
            if not os.path.isfile(canonic):
                canonic = search_file(filename, self.search_path,
                                      self.main_dirname)
                # Not if this is right for utter failure.
                if not canonic: canonic = filename
            canonic = os.path.normcase(canonic)
            self.fncache[filename] = canonic
        return canonic

    def canonic_filename(self, frame):
        return self.canonic(frame.f_code.co_filename)

    def clear_break(self, filename, lineno):
        filename = self.canonic(filename)
        if not filename in self.breaks:
            self.errmsg('No breakpoint at %s:%d.'
                        % (self.filename(filename), lineno))
            return []
        if lineno not in self.breaks[filename]:
            self.errmsg('No breakpoint at %s:%d.'
                        % (self.filename(filename), lineno))
            return []
        # If there's only one bp in the list for that file,line
        # pair, then remove the breaks entry
        brkpts = []
        for bp in bdb.Breakpoint.bplist[filename, lineno][:]:
            brkpts.append(bp.number)
            bp.deleteMe()
        if not bdb.Breakpoint.bplist.has_key((filename, lineno)):
            self.breaks[filename].remove(lineno)
        if not self.breaks[filename]:
            del self.breaks[filename]
        return brkpts

    def complete(self, text, state):
        "A readline complete replacement"
        if hasattr(self, "completer"):
            if self.readline:
                line_buffer = self.readline.get_line_buffer()
                cmds        = self.all_completions(line_buffer, False)
            else:
                line_buffer = ''
                cmds        = self.all_completions(text, False)
            self.completer.namespace = dict(zip(cmds, cmds))
            args=line_buffer.split()
            if len(args) < 2:
                self.completer.namespace.update(self.curframe.f_globals.copy())
                self.completer.namespace.update(self.curframe.f_locals)
            return self.completer.complete(text, state)
        return None

    def filename(self, filename=None):
        """Return filename or the basename of that depending on the
        self.basename setting"""
        if filename is None:
            if self.mainpyfile:
                filename = self.mainpyfile
            else:
                return None
        if self.basename:
            return(os.path.basename(filename))
        return filename

    def format_stack_entry(self, frame_lineno, lprefix=': ',
                           include_location=True):
        """Format and return a stack entry gdb-style.
        Note: lprefix is not used. It is kept for compatibility.
        """
        import repr as repr_mod
        frame, lineno = frame_lineno
        filename = self.filename(self.canonic_filename(frame))

        s = ''
        if frame.f_code.co_name:
            s = frame.f_code.co_name
        else:
            s = "<lambda>"

        args, varargs, varkw, local_vars = inspect.getargvalues(frame)
        parms=inspect.formatargvalues(args, varargs, varkw, local_vars)
        if len(parms) >= self.maxargstrsize:
            parms = "%s...)" % parms[0:self.maxargstrsize]
        s += parms

        # ddd can't handle wrapped stack entries.
        # if len(s) >= 35:
        #    s += "\n    "

        if '__return__' in frame.f_locals:
            rv = frame.f_locals['__return__']
            s += '->'
            s += repr_mod.repr(rv)

        add_quotes_around_file = True
        if include_location:
            if s == '?()':
                if is_exec_stmt(frame):
                    s = 'in exec'
                    exec_str = get_exec_string(frame.f_back)
                    if exec_str != None:
                        filename = exec_str
                        add_quotes_around_file = False
                else:
                    s = 'in file'
            else:
                s += ' called from file'

            if add_quotes_around_file: filename = "'%s'" % filename
            s += " %s at line %r" % (filename, lineno)
        return s

    # The following two methods can be called by clients to use
    # a debugger to debug a statement, given as a string.

    def run(self, cmd, globals=None, locals=None):
        """A copy of bdb's run but with a local variable added so we
        can find it it a call stack and hide it when desired (which is
        probably most of the time).
        """
        breadcrumb = self.run
        if globals is None:
            import __main__
            globals = __main__.__dict__
        if locals is None:
            locals = globals
        self.reset()
        sys.settrace(self.trace_dispatch)
        if not isinstance(cmd, types.CodeType):
            cmd = cmd+'\n'
        try:
            self.running = True
            try:
                exec cmd in globals, locals
            except bdb.BdbQuit:
                pass
        finally:
            self.quitting = 1
            self.running = False
            sys.settrace(None)

    def reset(self):
        bdb.Bdb.reset(self)
        self.forget()

    def set_trace(self, frame=None):
        """Wrapper to accomodate different versions of Python"""
        if sys.version_info[0] == 2 and sys.version_info[1] >= 4:
            if frame is None:
                frame = self.curframe
            self.bdb_set_trace(self, frame)
        else:
            # older versions
            self.bdb_set_trace(self)

    def user_call(self, frame, argument_list):
        """This method is called when there is the remote possibility
        that we ever need to stop in this function.
        Note argument_list isn't used. It is kept for compatibility"""
        self.stop_reason = 'call'
        if self._wait_for_mainpyfile:
            return
        if self.stop_here(frame):
            frame_count = count_frames(frame, Bdb.extra_call_frames)
            self.msg_nocr('--%sCall level %d' % 
                          ('-' * (2*frame_count), frame_count))
            if frame_count >= 0:
                self.__print_call_params(frame)
            else:
                self.msg("")
            if self.linetrace or self.fntrace:
                self.__print_location_if_trace(frame)
                if not self.break_here(frame): return
            self.interaction(frame, None)

    def user_exception(self, frame, (exc_type, exc_value, exc_traceback)):
        """This function is called if an exception occurs,
        but only if we are to stop at or just below this level."""

        self.stop_reason = 'exception'
        # Remove any pending source lines.
        self.rcLines = []

        frame.f_locals['__exception__'] = exc_type, exc_value
        if type(exc_type) == types.StringType:
            exc_type_name = exc_type
        else: exc_type_name = exc_type.__name__
        self.msg("%s:%s" % (str(exc_type_name),
                            str(self._saferepr(exc_value))))
        self.interaction(frame, exc_traceback)

    def user_line(self, frame):
        """This function is called when we stop or break at this line.
        However it's *also* called when line OR function tracing is 
        in effect. A little bit confusing and this code needs to be 
        simplified."""
        self.stop_reason = 'line'
        if self._wait_for_mainpyfile:
            if (self.mainpyfile != self.canonic_filename(frame)
                or inspect.getlineno(frame) <= 0):
                return
            self._wait_for_mainpyfile = False

        if self.stop_here(frame) or self.linetrace or self.fntrace:
            # Don't stop if we are looking at a def for which a breakpoint
            # has not been set.
            filename = self.filename(self.canonic_filename(frame))
            line = linecache.getline(filename, inspect.getlineno(frame))
            # No don't have a breakpoint. So we are either
            # stepping or here be of line tracing.
            if self.step_ignore > 0:
                # Don't stop this time, just note a step was done in
                # step count
                self.step_ignore -= 1
                self.__print_location_if_trace(frame, False)
                return
            elif self.step_ignore < 0:
                # We are stepping only because we tracing
                self.__print_location_if_trace(frame, False)
                return
            if not self.break_here(frame):
                if is_def_stmt(line, frame) and not self.deftrace:
                    self.__print_location_if_trace(frame, False)
                    return
                elif self.fntrace:
                    # The above test is a real hack. We need to clean
                    # up this code. 
                    return
        else:
            if not self.break_here(frame) and self.step_ignore > 0:
                self.__print_location_if_trace(frame, False)
                self.step_ignore -= 1
                return
        if self.bp_commands(frame):
            self.interaction(frame, None)

    def user_return(self, frame, return_value):
        """This function is called when a return trap is set here."""
        self.stop_reason = 'return'
        frame.f_locals['__return__'] = return_value
        frame_count = count_frames(frame, Bdb.extra_call_frames)
        if frame_count >= 0:
            self.msg_nocr("--%sReturn from level %d" % ('-' * (2*frame_count), 
                          frame_count))
            if type(return_value) in [types.StringType, types.IntType, 
                                  types.FloatType,  types.BooleanType]:
                self.msg_nocr('=> %s' % repr(return_value))
            self.msg('(%s)' % repr(type(return_value)))
        self.stop_reason = 'return'
        self.__print_location_if_trace(frame, False)
        if self.returnframe != None:
            self.interaction(frame, None)

