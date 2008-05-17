"""set subcommands, except those that need some sort of text substitution.
(Those are in gdb.py.in.)
"""
__revision__ = "$Id: set.py,v 1.23 2008/05/17 10:08:33 rockyb Exp $"
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

import inspect, os, re, sighandler, sys

class SubcmdSet:

    """Handle set subcommands. This class isn't usuable in of itself,
    but is expected to be called with something that subclasses it and
    adds other methods and instance variables like msg and
    _program_sys_argv."""

    def __open_log(self, filename):
        open_mode = ('w', 'a')[self.logging_overwrite]
        try:
            self.logging_fileobj = open(filename, open_mode)
            self.logging_file = filename
        except:
            self.errmsg("Error in opening %s" % filename)
        return

    ######## Note: the docstrings of methods here get used in
    ######## help output.

    def set_annotate(self, args):
        """Set annotation level
0 == normal;     1 == fullname (for use when running under emacs)
2 == output annotated suitably for use by programs that control GDB.
"""
        try:
            self.annotate = self.get_int(args[1])
        except ValueError:
            pass
        return

    def set_args(self, args):
        """Set argument list to give program being debugged when it is started.
Follow this command with any number of args, to be passed to the program."""
        argv_start = self._program_sys_argv[0:1]
        if len(args):
            self._program_sys_argv = args[0:]
        else:
            self._program_sys_argv = []
            self._program_sys_argv[:0] = argv_start
        return

    def set_autoeval(self, args):
        """Evaluate every unrecognized command."""
        try:
            self.autoeval = self.get_onoff(args[1])
        except ValueError:
            pass
        return

    def set_basename(self, args):
        """Set short filenames (the basename) in debug output"""
        try:
            self.basename = self.get_onoff(args[1])
        except ValueError:
            pass
        return

    def set_cmdtrace(self, args):
        """Set to show lines read from the debugger command file"""
        try:
            self.cmdtrace = self.get_onoff(args[1])
        except ValueError:
            pass
        return

    def set_dbg_pydb(self, args):
        """Set whether we allow tracing the debugger.

This is used for debugging pydb and getting access to some of its
object variables.
"""
        try:
            self.dbg_pydb = self.get_onoff(args[1])
            if self.dbg_pydb:
                frame = inspect.currentframe()
                self.stack, self.curindex = self.get_stack(frame, None)
                self.curframe = self.stack[self.curindex][0]

        except ValueError:
            pass
        return

    def set_debug_signal(self, args):
        """Set the signal sent to a process to trigger debugging."""
        if len(args) <= 1:
            self.errmsg('Need a signal name or number')
        signame = args[1]
        try:
            signum  = int(signame)
            signame = sighandler.lookup_signame(signum) 
            if signame is None:
                self.errmsg('Invalid signal number: %d' % signum)
                return
        except:
            signum = sighandler.lookup_signum(signame)
            if signum is not None:
                # Canonicalize name
                signame = sighandler.lookup_signame(signum)
            else:
                self.errmsg('Invalid signal name: %s' % signame)
                return
        self.debug_signal = signame
        self.do_handle("%s noprint nostop pass" % signame)
        ## FIXME assign signal handler here.
        self.msg('debug-signal set to: %s' % self.debug_signal)
        return False

    def set_deftrace(self, args):
        """Set to def's (method creation) before they are run"""
        try:
            self.deftrace = self.get_onoff(args[1])
        except ValueError:
            pass
        return

    def set_flush(self, args):
        """Set whether we flush output after each write."""
        try:
            self.flush = self.get_onoff(args[1])
        except ValueError:
            pass
        return

    def set_fntrace(self, args):
        """Set function execution tracing"""
        try:
            self.fntrace = self.get_onoff(args[1])
        except ValueError:
            pass
        return

    def set_history(self, args):
        """Generic command for setting command history parameters.

set history filename - set location to save history
set history save [on|off] - specify whether or not ot save history
set history size n - set number of commands to save in history
        """
        if args[1] == 'filename':
            if len(args) < 3:
                self.errmsg("Argument required (filename to set it to).")
                return
            self.histfile = args[2]
        elif args[1] == 'save':
            self.hist_save = ( (len(args) >=3 and self.get_onoff(args[2]))
                               or True )
        elif args[1] == 'size':
            try:
                size = self.get_int(args[2], cmdname="set history size")
                self.set_history_length(size)
            except ValueError:
                return
        else:
            self.undefined_cmd("set history", args[0])
    def set_interactive(self, args):
        """Set whether we are interactive"""
        try:
            self.noninteractive = not self.get_onoff(args[1])
        except ValueError:
            pass
        return

    def set_linetrace(self, args):
        """Set line execution tracing and delay on tracing"""
        if args[1] == 'delay':
            try:
                delay = float(args[2])
                self.linetrace_delay = delay
            except IndexError:
                self.errmsg("Need a 3rd floating-point number")
            except ValueError:
                self.errmsg(("3rd argument %s is not a floating-point "
                             + "number") % str(args[2]) )
        else:
            try:
                self.linetrace = self.get_onoff(args[1])
            except ValueError:
                pass
        return

    def set_listsize(self, args):
        """Set number of source lines the debugger will list by default."""
        try:
            self.listsize = self.get_int(args[1])
        except ValueError:
            pass
        return

    def set_logging(self, args):
        """Set logging options"""
        if len(args):
            try:
                old_logging  = self.logging
                self.logging = self.get_onoff(args[1], default=None,
                                              print_error=False)
                if old_logging and not self.logging \
                       and self.logging_fileobj is not None:
                    self.logging_fileobj.close()
                if not old_logging and self.logging \
                       and not self.logging_fileobj:
                    self.__open_log(self.logging_file)
                return
            except ValueError:
                try:
                    if args[1] == 'file':
                        if len(args) > 2: self.__open_log(args[2])
                    elif args[1] == 'overwrite':
                        self.logging_overwrite = self.get_onoff(args[2],
                                                                default=True,
                                                                print_error=True
								)
                    elif args[1] == 'redirect':
                        self.logging_redirect = self.get_onoff(args[2],
                                                               default=True,
                                                               print_error=True)
                    else:
                        self.undefined_cmd("set logging", args[1])
                except (IndexError, ValueError):
                    return
        else:
            self.msg("""Usage: set logging on
set logging off
set logging file FILENAME
set logging overwrite [on|off]
set logging redirect [on|off]""")
        return


    def set_maxargsize(self, args):
        """Set maximum size to use in showing argument parameters"""
        try:
            self.maxargstrsize = self.get_int(args[1])
        except ValueError:
            pass
        return

    def set_prompt(self, args):
        """Set debugger's prompt"""
        # Use the original prompt so we keep spaces and punctuation
        # just skip over the work prompt.
        re_prompt = re.compile(r'\s*prompt\s(.*)$')
        mo = re_prompt.search(args)
        if mo:
            self.prompt = mo.group(1)
        else:
            self.errmsg("Something went wrong trying to find the prompt")
        return

    def set_sigcheck(self, args):
        """Set signal handler checking/adjusting.

Turning this on causes the debugger to check after every statement
whether a signal handler has changed from one of those that is to be
handled by the debugger. Because this may add a bit of overhead to the
running of the debugged program, by default it is set off. However if
you want to ensure that the debugger takes control when a particular
signal is encountered you should set this on."""

        try:
            sigcheck = self.get_onoff(args[1])
            if sigcheck != self.sigcheck:
                if sigcheck:
                    # Turn on signal checking/adjusting
                    self.sigmgr.check_and_adjust_sighandlers()
                    self.break_anywhere = self.break_anywhere_gdb
                    self.set_continue   = self.set_continue_gdb
                    self.trace_dispatch = self.trace_dispatch_gdb
                else:
                    # Turn off signal checking/adjusting
                    self.break_anywhere = self.break_anywhere_old
                    self.set_continue   = self.set_continue_old
                    self.trace_dispatch = self.trace_dispatch_old
            self.sigcheck = sigcheck
        except ValueError:
            pass
        return

    def set_target_address(self, args):
        """Set the address of a target."""
        self.target_addr = "".join(["%s " % a for a in args[1:]])
        self.target_addr = self.target_addr.strip()
        self.msg('target address set to %s' % self.target_addr)
        return

    def set_warnoptions(self, args):

        """Set the Python warning options that are in effect when a
program is started or restarted. On the command line, these are the -W
options, e.g. -Werror, or -We::Deprecation. However options should not
contain leading -W's and should be separated with white space only,
e.g. don't use commas.

Examples:
  set warn error e::Deprecation
  set warnoptions
"""

        sys.warnoptions = args[1:]
        self.show_warnoptions(args)
        return

    def set_width(self, args):
        """Set number of characters the debugger thinks are in a line.
We also change OS environment variable COLUMNS."""
        try:
            self.width = self.get_int(args[1])
            os.environ['COLUMNS'] = args[1]
        except ValueError:
            pass
        return

