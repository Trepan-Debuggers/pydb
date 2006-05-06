"""$Id: pydbbdb.py,v 1.7 2006/05/06 02:22:34 rockyb Exp $
A Python debugger Basic Debugger (bdb) class.

Routines here have to do with the subclassing of bdb.
"""
import bdb, inspect, time, types
from repr import Repr
from fns import *

class Bdb(bdb.Bdb):

    def __init__(self):
        bdb.Bdb.__init__(self)

        # A 0 value means stop on this occurance. A positive value means to
        # skip that many more step/next's.
        self.step_ignore = 0

        # Create a custom safe Repr instance and increase its maxstring.
        # The default of 30 truncates error messages too easily.
        self._repr = Repr()
        self._repr.maxstring = 200
        self._saferepr = self._repr.repr

    def __print_location_if_linetrace(self, frame):
        if self.linetrace:
            self.setup(frame)
            self.print_location(print_line=True)
            if self.linetrace_delay:
                time.sleep(self.linetrace_delay)

    def is_running(self):
        if self.running: return True
        self.msg('The program being debugged is not being run.')
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

    def bpprint(self, bp):
        if bp.temporary:
            disp = 'del  '
        else:
            disp = 'keep '
        if bp.enabled:
            disp = disp + 'y  '
        else:
            disp = disp + 'n  '
        self.msg('%-4dbreakpoint    %s at %s:%d' %
                 (bp.number, disp, self.filename(bp.file), bp.line))
        if bp.cond:
            self.msg('\tstop only if %s' % (bp.cond))
        if bp.ignore:
            self.msg('\tignore next %d hits' % (bp.ignore))
        if (bp.hits):
            if (bp.hits > 1): ss = 's'
            else: ss = ''
            self.msg('\tbreakpoint already hit %d time%s' %
                     (bp.hits, ss))

    def canonic_filename(self, frame):
        return self.canonic(frame.f_code.co_filename)

    def clear_break(self, filename, lineno):
        filename = self.canonic(filename)
        if not filename in self.breaks:
            self.errmsg('No breakpoint at %s:%d.'
                        % (self.filename(filename), lineno))
            return ()
        if lineno not in self.breaks[filename]:
            self.errmsg('No breakpoint at %s:%d.'
                        % (self.filename(filename), lineno))
            return()
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

    def filename(self, filename=None):
        if filename is None:
            filename = self.file
        """Return filename or the basename of that depending on the
        self.basename setting"""
        if self.basename:
            return(os.path.basename(filename))
        return filename

    def format_stack_entry(self, frame_lineno):
        """Format and return a stack entry gdb-style. """
        import linecache, repr
        frame, lineno = frame_lineno
        filename = self.filename(self.canonic_filename(frame))

        s = ''
        if frame.f_code.co_name:
            s = frame.f_code.co_name
        else:
            s = "<lambda>"

        args, varargs, varkw, locals = inspect.getargvalues(frame)
        parms=inspect.formatargvalues(args, varargs, varkw, locals)
        if len(parms) >= self.maxargstrsize:
            parms = "%s...)" % parms[0:self.maxargstrsize]
        s += parms

        # ddd can't handle wrapped stack entries.
        # if len(s) >= 35:
        #    s += "\n    "

        if '__return__' in frame.f_locals:
            rv = frame.f_locals['__return__']
            s += '->'
            s += repr.repr(rv)

        add_quotes_around_file = True
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

    def reset(self):
        bdb.Bdb.reset(self)
        self.forget()

    def user_call(self, frame, argument_list):
        """This method is called when there is the remote possibility
        that we ever need to stop in this function."""
        self.stop_reason = 'call'
        if self._wait_for_mainpyfile:
            return
        if self.stop_here(frame):
            self.msg('--Call--')
            if self.linetrace:
                self.__print_location_if_linetrace(frame)
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
        """This function is called when we stop or break at this line."""
        # print "+++ user_line here"
        self.stop_reason = 'line'
        if self._wait_for_mainpyfile:
            if (self.mainpyfile != self.canonic_filename(frame)
                or inspect.getlineno(frame) <= 0):
                return
            self._wait_for_mainpyfile = False

        if self.stop_here(frame) or self.linetrace:
            # Don't stop if we are looking at a def for which a breakpoint
            # has not been set.
            import linecache
            filename = self.filename(self.canonic_filename(frame))
            line = linecache.getline(filename, inspect.getlineno(frame))
            # No don't have a breakpoint. So we are either
            # stepping or here be of line tracing.
            if self.step_ignore > 0:
                # Don't stop this time, just note a step was done in
                # step count
                self.step_ignore -= 1
                self.__print_location_if_linetrace(frame)
                return
            elif self.step_ignore < 0:
                # We are stepping only because we tracing
                self.__print_location_if_linetrace(frame)
                return
            if not self.break_here(frame):
                if is_def_stmt(line, frame):
                    self.__print_location_if_linetrace(frame)
                    return
        else:
            if not self.break_here(frame) and self.step_ignore > 0:
                self.__print_location_if_linetrace(frame)
                self.step_ignore -= 1
                return
        self.interaction(frame, None)

    def user_return(self, frame, return_value):
        """This function is called when a return trap is set here."""
        self.stop_reason = 'return'
        frame.f_locals['__return__'] = return_value
        self.msg('--Return--')
        self.stop_reason = 'return'
        self.__print_location_if_linetrace(frame)
        if self.returnframe != None:
            self.interaction(frame, None)

