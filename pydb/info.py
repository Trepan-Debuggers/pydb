"""$Id: info.py,v 1.1 2006/07/25 09:33:05 rockyb Exp $
show subcommands, except those that need some sort of text substitution.
(Those are in gdb.py.in.)
"""
import bdb, inspect, os, pprint
class SubcmdInfo:
    def info_args(self, arg):
        """Argument variables of current stack frame."""
        if not self.curframe:
            self.msg("No stack.")
            return
        f = self.curframe
        co = f.f_code
        dict = f.f_locals
        n = co.co_argcount
        if co.co_flags & inspect.CO_VARARGS: n += 1
        if co.co_flags & inspect.CO_VARKEYWORDS: n += 1
        for i in range(n):
            name = co.co_varnames[i]
            self.msg_nocr("%s=" %  name)
            if name in dict: self.msg(dict[name])
            else: self.msg("*** undefined ***")

    def info_breakpoints(self, arg):
        """Status of user-settable breakpoints.
Without argument, list info about all breakpoints.  With an
integer argument, list info on that breakpoint.

The short command name is L."""
        if self.breaks:  # There's at least one
            self.msg("Num Type          Disp Enb    Where")
            for bp in bdb.Breakpoint.bpbynumber:
                if bp:
                    self.bpprint(bp)
        else:
            self.msg("No breakpoints.")

    def info_display(self, arg):
        """Expressions to display when program stops, with code numbers."""
        if not self.display.displayAll():
            self.msg('There are no auto-display expressions now.')

    def info_globals(self, arg):
        """Global variables of current stack frame"""
        if not self.curframe:
            self.msg("No frame selected.")
            return
        self.msg("\n".join(["%s = %s"
                            % (l, pprint.pformat(self.getval(l)))
                            for l in self.curframe.f_globals]))

    def info_line(self, arg):
        """Current line number in source file"""
        #info line identifier
        if not self.curframe:
            self.msg("No line number information available.")
            return
        if len(arg) == 2:
            # lineinfo returns (item, file, lineno) or (None,)
            answer = self.lineinfo(arg[1])
            if answer[0]:
                item, file, lineno = answer
                if not os.path.isfile(file):
                    file = search_file(file, self.search_path,
                                       self.main_dirname)
                self.msg('Line %s of "%s" <%s>' %
                         (lineno, file, item))
            return
        file=self.canonic_filename(self.curframe)
        if not os.path.isfile(file):
            file = search_file(file, self.search_path, self.main_dirname)

        self.msg('Line %d of \"%s\" at instruction %d' %
                 (inspect.getlineno(self.curframe),
                  self.filename(self.canonic_filename(self.curframe)),
                  self.curframe.f_lasti))

    def info_locals(self, arg):
        """Local variables of current stack frame"""
        if not self.curframe:
            self.msg("No frame selected.")
            return
        self.msg("\n".join(["%s = %s"
                            % (l, pprint.pformat(self.getval(l)))
                            for l in self.curframe.f_locals]))

    def info_program(self, arg):
        """Execution status of the program."""
        if not self.curframe:
            self.msg("The program being debugged is not being run.")
            return
        if self.is_running():
            self.msg('Program stopped.')
            if self.currentbp:
                self.msg('It stopped at breakpoint %d.' % self.currentbp)
            elif self.stop_reason == 'call':
                self.msg('It stopped at a call.')
            elif self.stop_reason == 'exception':
                self.msg('It stopped as a result of an exception.')
            elif self.stop_reason == 'return':
                self.msg('It stopped at a return.')
            else:
                self.msg("It stopped after stepping, next'ing or initial start.")
    def info_source(self, arg):
        """Information about the current Python file."""
        if not self.curframe:
            self.msg("No current source file.")
            return
        self.msg('Current Python file is %s' %
                 self.filename(self.canonic_filename(self.curframe)))
