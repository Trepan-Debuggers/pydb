"""show subcommands, except those that need some sort of text substitution.
(Those are in gdb.py.in.)
"""
__revision = "$Id: show.py,v 1.15 2007/05/23 09:25:43 rockyb Exp $"
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
import fns, sys

class SubcmdShow:

    """Handle set subcommands. This class isn't usuable in of itself,
    but is expected to be called with something that subclasses it and
    adds other methods and instance variables like msg and
    _program_sys_argv."""

    ######## Note: the docstrings of methods here get used in
    ######## help output.

    def show_args(self, args):
        """Show argument list to give debugged program when it is started.
Follow this command with any number of args, to be passed to the program."""
        self.msg("Argument list to give program being debugged " +
                 "when it is started is ")
        self.msg('"%s".' % " ".join(self._program_sys_argv[1:]))

    def show_basename(self, args):
        """Show if we are to show short of long filenames"""
        self.msg("basename is %s." % fns.show_onoff(self.basename))

    def show_cmdtrace(self, args):
        "Show if we are to show debugger commands before running"
        self.msg("cmdtrace is %s." % fns.show_onoff(self.cmdtrace))

    def show_dbg_pydb(self, args):
        """Show whether tracebacks include debugger routines"""
        self.msg("Dbg_pydb is %s." % fns.show_onoff(self.dbg_pydb))

    def show_debug_signal(self, arg):
        """Show the signal currently used for triggering debugging
        of an already running process.
        """
        if not self.debug_signal:
            self.msg('debug-signal not set.')
            return
        self.msg('debug-signal is %s' % self.debug_signal)

    def show_directories(self, args):
        """Current search path for finding source files.
$cwd in search path means the current working directory.
$cdir in the path means the compilation directory of the source file."""
        self.msg("Source directories searched:\n\t%s." % str(self.search_path))

    def show_flush(self, args):
        """Show whether we flush output after each write."""
        self.msg('Flushing output is "%s".' %
                 fns.show_onoff(self.flush))

    def show_fntrace(self, args):
        "Show the line function status. Can also add 'delay'"
        self.msg("function tracing is %s." % fns.show_onoff(self.fntrace))

    def show_interactive(self, args):
        """Show whether we are interactive"""
        self.msg("interactive is %s." %
                 fns.show_onoff(not self.noninteractive))

    def show_linetrace(self, args):
        "Show the line tracing status. Can also add 'delay'"
        self.msg("line tracing is %s." % fns.show_onoff(self.linetrace))

    def show_listsize(self, args):
        """Show number of source lines the debugger will list by default."""
        self.msg("Number of lines to show in listing is %s."
                 %  self.listsize)

    def show_logging(self, args):
        "Show logging options"
        if len(args) > 1 and args[1]:
            if args[1] == 'file':
                self.msg('The current logfile is "%s".' %
                         self.logging_file)
            elif args[1] == 'overwrite':
                self.msg('Whether logging overwrites or appends to the'
                         + ' log file is %s.'
                         % fns.show_onoff(self.logging_overwrite))
            elif args[1] == 'redirect':
                self.msg('The logging output mode is %s.' %
                         fns.show_onoff(self.logging_redirect))
            else:
                self.undefined_cmd("show logging", args[1])
        else:
            self.msg('Future logs will be written to %s.' % self.logging_file)
            if self.logging_overwrite:
                self.msg('Logs will overwrite the log file.')
            else:
                self.msg('Logs will be appended to the log file.')
            if self.logging_redirect:
                self.msg("Output will be sent only to the log file.")
            else:
                self.msg("Output will be logged and displayed.")

    def show_maxargsize(self, args):
        """Show number maximum number of characters in argument list."""
        self.msg("Maximum number of characters in an argument list is %s"
                 %  self.maxargstrsize)

    def show_sigcheck(self, args):
        """Show status of signal checking/adjusting.
See also set sigcheck."""
        self.msg("sigcheck is %s." % fns.show_onoff(self.sigcheck))

    def show_target_address(self, arg):

        """Show connection parameters used in remote debugging.

This command doesn't make sense if you are not debugging a remote
program. See also 'set target-address' and 'attach'."""

        if self.target == 'local':
            self.msg("Debugging is local. No target address.")
        else:
            self.msg('target-address is %s.' % self.target_addr.__repr__())

    def show_warnoptions(self, args):
        """Show Python warning options to be used in running programs."""
        if len(sys.warnoptions):
            self.msg('Warning options used in running a Python program:')
            self.msg("\t -W%s" % ', -W'.join(sys.warnoptions))
        else:
            self.msg('No warning options have been set.')

    def show_width(self, args):
        """Show number of characters gdb thinks are in a line."""
        self.msg("Number of lines to show in listing is %s."
                 %  self.width)

