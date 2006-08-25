"""$Id: pydbcmd.py,v 1.29 2006/08/25 12:33:41 rockyb Exp $
A Python debugger command class.

Routines here have to do with parsing or processing commands, but are
not the commands themselves which are in gdb.py.in.  Generally (but
not always) they are not specific to pydb. They are sort of more
oriented towards any gdb-like debugger. Also routines that need to be
changed from cmd are here.  """

import cmd, linecache, sys, types
from fns import *

# Interaction prompt line will separate file and call info from code
# text using value of line_prefix string.  A newline and arrow may
# be to your liking.  You can set it once pydb is imported using the
# command "pydb.line_prefix = '\n% '".
# line_prefix = ': '    # Use this to get the old situation back
line_prefix = '\n-> '   # Probably a better default

class Cmd(cmd.Cmd):

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
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
                    "__file__" : self.mainpyfile,
                    "__builtins__" : __builtins__
                    }
        locals_ = globals_

        statement = 'execfile( "%s")' % filename
        self.running = True
        self.run(statement, globals=globals_, locals=locals_)

    def default(self, line):
        """Method called on an input line when the command prefix is
        not recognized. In particular we ignore # comments and execute
        Python commands which might optionally start with $"""

        if line[:1] == '#': return
        if line[:1] == '$': line = line[1:]
        if self.curframe:
            local_vars = self.curframe.f_locals
            global_vars = self.curframe.f_globals
        else:
            local_vars = None
            # FIXME: should probably have place where the
            # user can store variables inside the debug session.
            # The setup for this should be elsewhere. Possibly
            # in interaction.
            global_vars = None
        try:
            code = compile(line + '\n', '"%s"' % line, 'single')
            exec code in global_vars, local_vars
        except:
            t, v = sys.exc_info()[:2]
            if type(t) == types.StringType:
                exc_type_name = t
            else: exc_type_name = t.__name__
            self.errmsg('%s: %s' % (str(exc_type_name), str(v)))

    ### This comes from cmd.py with self.stdout.write replaced by self.msg
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
            help_dict = {}
            for name in names:
                if name[:5] == 'help_':
                    help_dict[name[5:]]=1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd=name[3:]
                    if cmd in help_dict:
                        cmds_doc.append(cmd)
                        del help_dict[cmd]
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)
            self.msg("%s\n" % str(self.doc_leader))
            self.print_topics(self.doc_header,   cmds_doc,   15,80)
            self.print_topics(self.misc_header,  help_dict.keys(),15,80)
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
            except ValueError:
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
                                    % (min, default))
                    # Really should use something custom? 
                    raise ZeroDivisionError
                    
            except ValueError:
                if cmdname:
                    self.errmsg(('%s command: Expecting a positive integer, '
                                 + "got: %s") % (cmdname, str(arg)))
                else:
                    self.errmsg(('Expecting a positive integer, '
                                 + "got: %s") % str(arg))
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

    def errmsg(self, msg, prefix="*** "):
        """Common routine for reporting debugger error messages.
           Derived classed may want to override this to capture output.
           """
        self.msg_nocr("%s%s\n" %(prefix, msg))

    def handle_command_def(self,line):        
        """ Handles one command line during command list
        definition. """
        cmd, arg, line = self.parseline(line)
        if cmd == 'silent':
            self.commands_silent[self.commands_bnum] = True
            return # continue to handle other cmd def in the cmd list
        elif cmd == 'end':
            self.cmdqueue = []
            return 1 # end of cmd list
        cmdlist = self.commands[self.commands_bnum]
        if (arg):
            cmdlist.append(cmd+' '+arg)
        else:
            cmdlist.append(cmd)
        # Determine if we must stop
        try:
            func = getattr(self, 'do_' + cmd)
        except AttributeError:
            func = self.default
        if func.func_name in self.commands_resuming :
            # one of the resuming commands. 
            self.commands_doprompt[self.commands_bnum] = False
            self.cmdqueue = []
            return 1
        return

    def msg(self, msg, out=None):
        """Common routine for reporting messages.
           Derived classed may want to override this to capture output.
           """
        self.msg_nocr("%s\n" % msg, out)

    def msg_nocr(self, msg, out=None):
        """Common routine for reporting messages (no carriage return).
           Derived classed may want to override this to capture output.
           """
        do_print = True
        if self.logging:
            if self.logging_fileobj is not None:
                print >> self.logging_fileobj, msg,
            do_print = not self.logging_redirect
        if do_print:
            if out is None:
                out = self.stdout
            print >> out, msg,

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

    def print_location(self, print_line=False):
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

    def onecmd(self, line):

        """Interpret the argument as though it had been typed
        in response to the prompt.
        
        Checks whether this line is typed in the normal
        prompt or in a breakpoint command list definition """

        if not self.commands_defining:
            return cmd.Cmd.onecmd(self, line)
        else:
            return self.handle_command_def(line)

    def undefined_cmd(self, cmd, subcmd):
        """Error message when subcommand asked for but doesn't exist"""
        self.errmsg("Undefined %s command \"%s\"." % (cmd, subcmd))
