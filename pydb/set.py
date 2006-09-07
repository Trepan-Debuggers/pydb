"""$Id: set.py,v 1.7 2006/09/07 01:23:26 rockyb Exp $
set subcommands, except those that need some sort of text substitution.
(Those are in gdb.py.in.)
"""

import inspect, re

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

    ######## Note: the docstrings of methods here get used in
    ######## help output.

    def set_args(self, args):
        """Set argument list to give program being debugged when it is started.
Follow this command with any number of args, to be passed to the program."""
        argv_start = self._program_sys_argv[0:1]
        if len(args):
            self._program_sys_argv = args[0:]
        else:
            self._program_sys_argv = []
            self._program_sys_argv[:0] = argv_start

    def set_basename(self, args):
        """Set short filenames (the basename) in debug output"""
        try:
            self.basename = self.get_onoff(args[1])
        except ValueError:
            pass

    def set_cmdtrace(self, args):
        """Set to show lines read from the debugger command file"""
        try:
            self.cmdtrace = self.get_onoff(args[1])
        except ValueError:
            pass

    def set_debug_signal(self, args):
        """Set the signal sent to a process to trigger debugging."""
        try:
            exec 'from signal import %s' % args[1]
        except ImportError:
            self.errmsg('Invalid signal')
            return
        self.debug_signal = args[1]
        self.msg('debug-signal set to: %s' % self.debug_signal)

    def set_history(self, args):
        """Generic command for setting command history parameters."""
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

    def set_linetrace(self, args):
        """Set line execution tracing and delay on tracing"""
        if args[1]=='delay':
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

    def set_listsize(self, args):
        """Set number of source lines the debugger will list by default."""
        try:
            self.listsize = self.get_int(args[1])
        except ValueError:
            pass

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
                    if args[1] == 'overwrite':
                        self.logging_overwrite = self.get_onoff(args[2],
                                                                default=True,
                                                                print_error=True)
                    elif args[1] == 'redirect':
                        self.logging_redirect = self.get_onoff(args[2],
                                                               default=True,
                                                               print_error=True)
                    elif args[1] == 'file':
                        if len(args) > 2: self.__open_log(args[2])
                    else:
                        self.undefined_cmd("set logging", args[1])
                except ValueError:
                    return
        else:
            self.msg("""Usage: set logging on
set logging off
set logging file FILENAME
set logging overwrite [on|off]
set logging redirect [on|off]""")


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

    def set_systrace(self, args):
        """Set whether we allow tracing the debugger."""
        try:
            self.systrace = self.get_onoff(args[1])
            if self.systrace:
                frame = inspect.currentframe()
                self.stack, self.curindex = self.get_stack(frame, None)
                self.curframe = self.stack[self.curindex][0]

        except ValueError:
            pass

    def set_target_address(self, args):
        """Set the address of a target."""
        self.target_addr = "".join(["%s " % a for a in args[1:]])
        self.target_addr = self.target_addr.strip()
        self.msg('target address set to %s' % self.target_addr)

