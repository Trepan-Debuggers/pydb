"""$Id: pydbcmd.py,v 1.12 2006/04/08 17:55:08 rockyb Exp $
A Python debugger command class.

Routines here have to do with parsing or processing commands,
generally (but not always) the are not specific to pydb. They are sort
of more oriented towards any gdb-like debugger. Also routines that need to
be changed from cmd are here.
"""
import cmd, linecache, os, sys, types
from fns import *

# Interaction prompt line will separate file and call info from code
# text using value of line_prefix string.  A newline and arrow may
# be to your liking.  You can set it once pydb is imported using the
# command "pydb.line_prefix = '\n% '".
# line_prefix = ': '    # Use this to get the old situation back
line_prefix = '\n-> '   # Probably a better default

class Cmd(cmd.Cmd):

    def __init__(self):
        cmd.Cmd.__init__(self)
        self._user_requested_quit = False
        self.aliases              = {}
        self.cmdtrace             = False
        self.logging              = False
        self.logging_file         = "pydb.txt"
        self.logging_fileobj      = None         # file object from open()
        self.logging_overwrite    = False
        self.logging_redirect     = False
        self.nohelp               = 'Undefined command: \"%s\". Try \"help\".'
        self.prompt               = '(Pydb) '
        self.rcLines              = []

    def __open_log(self, filename):
        open_mode = ('w', 'a')[self.logging_overwrite]
        try:
            self.logging_fileobj = open(filename, open_mode)
            self.logging_file = filename
        except:
            self.errmsg("Error in opening %s" % filename)

    def _runscript(self, filename):
        # When bdb sets tracing, a number of call and line events happens
        # BEFORE debugger even reaches user's code (and the exact sequence of
        # events depends on python version). So we take special measures to
        # avoid stopping before we reach the main script (see user_line and
        # user_call for details).
        self._wait_for_mainpyfile = True
        self.mainpyfile = self.canonic(filename)

        # Start with fresh empty copy of globals and locals and tell the script
        # that it's being run as __main__ to avoid scripts being able to access
        # the pydb.py namespace.
        globals_ = {"__name__" : "__main__",
                    "__file__" : self.mainpyfile
                    }
        locals_ = globals_


        statement = 'execfile( "%s")' % filename
        self.running = True
        self.run(statement, globals=globals_, locals=locals_)

    def default(self, line):
        """Method called on an input line when the command prefix is
        not recognized. In particular we ignore # comments and execute
        Python commands which might optionally start with !"""

        if line[:1] == '#': return
        if line[:1] == '!': line = line[1:]
        locals = self.curframe.f_locals
        globals = self.curframe.f_globals
        try:
            code = compile(line + '\n', '"%s"' % line, 'single')
            exec code in globals, locals
        except:
            t, v = sys.exc_info()[:2]
            if type(t) == types.StringType:
                exc_type_name = t
            else: exc_type_name = t.__name__
            self.errmsg('%s: %s' % (str(exc_type_name), str(v)))

    ### This Comes from cmd.py 
    def do_help(self, arg):
        """Without argument, print the list of available commands.
        With a command name as argument, print help about that command
        'help *cmd*' pipes the full documentation file to the $PAGER
        'help exec gives help on the ! command"""
        if arg:
            first_arg = arg.split()[0]
            try:
                func = getattr(self, 'help_' + first_arg)
                func(arg.split()[1:])
            except AttributeError:
                try:
                    doc=getattr(self, 'do_' + first_arg).__doc__
                    if doc:
                        self.msg("%s\n" % str(doc))
                        return
                except AttributeError:
                    pass
                self.msg("%s\n" % str(self.nohelp % (first_arg,)))
                return
        else:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]]=1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd=name[3:]
                    if cmd in help:
                        cmds_doc.append(cmd)
                        del help[cmd]
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)
            self.msg("%s\n" % str(self.doc_leader))
            self.print_topics(self.doc_header,   cmds_doc,   15,80)
            self.print_topics(self.misc_header,  help.keys(),15,80)
            self.print_topics(self.undoc_header, cmds_undoc, 15,80)

    do_h = do_help

    # Can be executed earlier than 'setup' if desired
    def execRcLines(self):

        """Some commands were batched in self.rcLines.  Run as many of
        them as we can now.
        
        To be compatible with onecmd will return 1 if we are to
        continue execution and None if not -- continue debugger
        commmand loop reading.  The remaining lines will still be in
        self.rcLines.  """

        if self.rcLines:
            # Make local copy because of recursion
            rcLines = self.rcLines
            # executed only once
            for line in rcLines:
                self.rcLines = self.rcLines[1:]
                line = line[:-1]
                if self.cmdtrace: self.msg("+ %s" % line)
                if len(line) > 0 and line[0] != '#':
                    # Some commands like step, continue,
                    # return return 1 to indicate execution
                    # should be continued. The return code
                    # value is kind of sucky but at present
                    # it's too much work to fix all of the
                    # places needed. So live with it.
                    if self.onecmd(line) == 1:
                        return 1

    def get_int(self, arg, default=1, cmdname=None):
        """If arg is an int, use that otherwise take default."""
        if arg:
            try: 
                default = int(arg)
            except ValueError, msg:
                if cmdname:
                    self.errmsg('%s command: Expecting an integer, got: %s' %
                                (cmdname, str(arg)))
                else:
                    self.errmsg('Expecting an integer, got: %s' % str(arg))
                raise ValueError
        return default

    def get_onoff(self, arg, default=None, print_error=True):
        """Return True if arg is 'on' or 1 and False arg is an 'off' or 0
        Any other value is an error"""
        if not arg:
            if default is None:
                if print_error:
                    self.errmsg("Expecting 'on', 1, 'off', or 0. Got nothing.")
                raise ValueError
            return default
        if arg == '1' or arg == 'on': return True
        if arg == '0' or arg =='off': return False

        if print_error:
            self.errmsg("Expecting 'on', 1, 'off', or 0. Got: %s." % str(arg))
        raise ValueError

    def get_pos_int(self, arg, min=0, default = 1, cmdname=None):
        """If no argument use the default If arg is a positive int at
        least min, use that otherwise report an error."""
        if arg:
            try: 
                default = int(arg)
                if default < min:
                    if cmdname:
                        self.errmsg(('%s command: Expecting a positive ' +
                                     'integer at least %d, got: %d') 
                                    % (cmdname, min, default))
                    else: 
                        self.errmsg(('Expecting a positive ' +
                                     'integer at least %d, got: %d') 
                                    % (cmdname, min, default))
                    # Really should use something custom? 
                    raise ZeroDivisionError
                    
            except ValueError, msg:
                if cmdname:
                    self.errmsg(('%s command: Expecting a positive integer, '
                                 + "got: %s") % (cmdname, str(arg)))
                else:
                    self.errmsg(('Expecting a positive integer, '
                                 + "got: %s") % (cmdname, str(arg)))
                raise ValueError
            except ZeroDivisionError:
                # Turn this into a ValueError
                raise ValueError
        return default

    def getval(self, arg):
        try:
            return eval(arg, self.curframe.f_globals,
                        self.curframe.f_locals)
        except:
            t, v = sys.exc_info()[:2]
            if isinstance(t, str):
                exc_type_name = t
            else: exc_type_name = t.__name__
            self.errmsg(str("%s: %s" % (exc_type_name, arg)))
            raise

    def errmsg(self, msg):
        """Common routine for reporting debugger error messages.
           Derived classed may want to override this to capture output.
           """
        self.msg_nocr("*** %s\n" % msg)

    def msg(self, msg):
        """Common routine for reporting messages.
           Derived classed may want to override this to capture output.
           """
        self.msg_nocr("%s\n" % msg)

    def msg_nocr(self, msg):
        """Common routine for reporting messages (no carriage return).
           Derived classed may want to override this to capture output.
           """
        do_print = True
        if self.logging:
            if self.logging_fileobj is not None:
                print >> self.logging_fileobj, msg,
            do_print = not self.logging_redirect
        if do_print:                
            print msg,

    def precmd(self, line):
        """Method executed just before the command line line is
        interpreted, but after the input prompt is generated and
        issued.

        Handle alias expansion and ';;' separator."""
        if not line.strip():
            return line
        args = line.split()
        while args[0] in self.aliases:
            line = self.aliases[args[0]]
            ii = 1
            for tmpArg in args[1:]:
                line = line.replace("%" + str(ii),
                                      tmpArg)
                ii = ii + 1
            line = line.replace("%*", ' '.join(args[1:]))
            args = line.split()
        # split into ';;' separated commands
        # unless it's an alias command
        if args[0] != 'alias':
            marker = line.find(';;')
            if marker >= 0:
                # queue up everything after marker
                next = line[marker+2:].lstrip()
                self.cmdqueue.append(next)
                line = line[:marker].rstrip()
        return line

    def print_location(self, prompt_prefix=line_prefix, print_line=False):
        """Show where we are. GUI's and front-end interfaces often
        use this to update displays. So it is helpful to make sure
        we give at least some place that's located in a file.      
        """
        i_stack = self.curindex
        while i_stack >= 0:
            frame_lineno = self.stack[i_stack]
            i_stack -= 1
            frame, lineno = frame_lineno
            filename = self.filename(self.canonic_filename(frame))
            self.msg_nocr('(%s:%s):' % (filename, lineno))
            fn_name = frame.f_code.co_name
            if fn_name and fn_name != '?':
                self.msg(" %s" % frame.f_code.co_name)
            else:
                self.msg("")

            if print_line:
                self.msg_nocr('+ %s' % linecache.getline(filename, lineno))

            # If we are stopped at an "exec" or print the next outer
            # location for that front-ends tracking source execution.
            if not is_exec_stmt(frame):
                break

    def set_args(self, args):
        argv_start = self._program_sys_argv[0:1]
        if len(args):
            self._program_sys_argv = args[0:]
        else:
            self._program_sys_argv = []
            self._program_sys_argv[:0] = argv_start
            
    def set_basename(self, args):
        try:
            self.basename = self.get_onoff(args[1])
        except ValueError:
            pass

    def set_cmdtrace(self, args):
        try:
            self.cmdtrace = self.get_onoff(args[1])
        except ValueError:
            pass

    def set_history(self, args):            
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

    def set_linetrace(self, args):
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
        try:
            self.listsize = self.get_int(args[1])
        except ValueError:
            pass

    def set_logging(self, args):
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
        # Use the original prompt so we keep spaces and punctuation
        # just skip over the work prompt.
        re_prompt = re.compile(r'\s*prompt\s(.*)$')
        mo = re_prompt.search(arg)
        if mo:
            self.prompt = mo.group(1)
        else:
            self.errmsg("Something went wrong trying to find the prompt")

    def show_logging(self, args):
        """This text odd as it is, is what gdb reports for 'show logging'."""
        if len(args) > 1 and args[1]:
            if args[1] == 'file':
                self.msg('The current logfile is "%s".' %
                         self.logging_file)
            elif args[1] == 'overwrite':
                self.msg('Whether logging overwrites or appends to the'
                         + ' log file is %s.'
                         % show_onoff(self.logging_overwrite))
            elif args[1] == 'redirect':
                self.msg('The logging output mode is %s.' %
                         show_onoff(self.logging_redirect))
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

    # Note: format of help is compatible with ddd.
    def subcommand_help(self, cmd, doc, subcmds, help_prog, args):
        """Generic command for showing things about the program being debugged."""
        if len(args) == 0:
            self.msg(doc)
            self.msg("""
List of %s subcommands:
""" % (cmd))
            for subcmd in subcmds:
                help_prog(subcmd, True)
            return
        if len(args) == 1:
            subcmd = args[0]
            if subcmd in subcmds:
                help_prog(subcmd)
            else:
                self.errmsg("Unknown 'help %s' subcommand %s" % (cmd, subcmd))
        else:
            self.errmsg("Can only handle 'help %s', or 'help %s *subcmd*'"
                        % (cmd, cmd))

    def undefined_cmd(self, cmd, subcmd):
        """Error message when subcommand asked for but doesn't exist"""
        self.errmsg("Undefined %s command \"%s\"." % (cmd, subcmd))
