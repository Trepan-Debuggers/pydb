"""A Python debugger command class.

Routines here have to do with parsing or processing commands, but are
not the commands themselves which are in gdb.py.in.  Generally (but
not always) they are not specific to pydb. They are sort of more
oriented towards any gdb-like debugger. Also routines that need to be
changed from cmd are here.

$Id: pydbcmd.py,v 1.57 2009/03/18 10:12:54 rockyb Exp $"""

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
        self.flush                = False        # flush after each write
        self.logging              = False
        self.logging_file         = "pydb.txt"
        self.logging_fileobj      = None         # file object from open()
        self.logging_overwrite    = False
        self.logging_redirect     = False
        self.nohelp               = 'Undefined command or invalid expression \"%s\".\nType \"help\" for a list of debugger commands.'
        self.prompt               = '(Pydb) '
        self.rcLines              = []
        return

    def get_cmds(self):
        '''Return a list of command names. These are the methods
        that start do_'''
        names = self.get_names()  # A list of all methods
        names.sort()
        # There can be duplicates if routines overridden. Weed these out.
        prevname = ''; cmds = []
        for name in names:
            if name[:3] == 'do_':
                if name == prevname:
                    continue
                prevname = name
                cmds.append(name[3:])
                pass
            pass
        return cmds

    def print_source_line(self, lineno, line):
        """Print out a source line of text , e.g. the second
        line in:
            (/tmp.py:2):  <module>
            2 import sys,os
            (Pydb)

        We define this method
        specifically so it can be customized for such applications
        like ipython."""

        # We don't use the filename normally. ipython and other applications
        # however might.
        self.msg_nocr('%d %s' % (lineno, line))
        return



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
        self.run(statement)
        return

    def default(self, line):
        """Method called on an input line when the command prefix is
        not recognized. In particular we ignore # comments and execute
        Python commands which might optionally start with $"""

        if line[:1] == '#': return
        if line[:1] == '$': line = line[1:]
        if not self.autoeval: 
            self.errmsg("""Undefined command: "%s".  Try "help".""" % line)
            return
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
            save_stdout = sys.stdout
            save_stdin = sys.stdin
            try:
                sys.stdin = self.stdin
                sys.stdout = self.stdout
                exec code in global_vars, local_vars
            finally:
                sys.stdout = save_stdout
                sys.stdin = save_stdin
                pass
        except:
            t, v = sys.exc_info()[:2]
            if type(t) == types.StringType:
                exc_type_name = t
            else: exc_type_name = t.__name__
            self.errmsg('%s: %s' % (str(exc_type_name), str(v)))

    ### This comes from cmd.py with self.stdout.write replaced by self.msg.
    ### Also we extend to given help on an object name. The 
    ### Docstring has been updated to reflect all of this.
    def do_help(self, arg):
        """help [command [subcommand]|expression]

Without argument, print the list of available debugger commands.

When an argument is given, it is first checked to see if it is command
name. 'help exec' gives help on the ! command.

With the argument is an expression or object name, you get the same
help that you would get inside a Python shell running the built-in
help() command.

If the environment variable $PAGER is defined, the file is
piped through that command.  You'll notice this only for long help
output.

Some commands like 'info', 'set', and 'show' can accept an
additional subcommand to give help just about that particular
subcommand. For example 'help info line' give help about the
'info line' command.

See also 'examine' an 'whatis'.
        """

        # It does not make much sense to repeat the last help
        # command. Also, given that 'help' uses PAGER, the you may
        # enter an extra CR which would rerun the (long) help command.
        self.lastcmd='' 

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
                    # If we have an object run site helper on that
                    try:
                        if not self.curframe:
                            # ?? Should we have set up a dummy globals
                            # to have persistence?
                            value = eval(arg, None, None)
                        else:
                            value = eval(arg, self.curframe.f_globals,
                                         self.curframe.f_locals)
                        from site import _Helper
                        h=_Helper()
                        h.__call__(value)
                    except:
                       self.msg("%s\n" % str(self.nohelp % (first_arg,)))
                       return
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
            self.print_topics(self.doc_header,   cmds_doc,   15,
                              self.width)
            self.print_topics(self.misc_header,  help_dict.keys(),15,
                              self.width)
            self.print_topics(self.undoc_header, cmds_undoc, 15,
                              self.width)

    do_h = do_help

    # Can be executed earlier than 'setup' if desired
    def execRcLines(self, verbose=False):

        """Some commands were batched in self.rcLines.  Run as many of
        them as we can now.
        
        To be compatible with onecmd will return 1 if we are to
        continue execution and None if not -- continue debugger
        commmand loop reading.  The remaining lines will still be in
        self.rcLines."""

        if self.rcLines:
            # Make local copy because of recursion
            rcLines = self.rcLines
            # executed only once
            for line in rcLines:
                self.rcLines = self.rcLines[1:]
                line = line[:-1]
                if verbose: self.msg('+' + line)
                if len(line) > 0:
                    # Some commands like step, continue,
                    # return return 1 to indicate execution
                    # should be continued. The return code
                    # value is kind of sucky but at present
                    # it's too much work to fix all of the
                    # places needed. So live with it.
                    if self.onecmd(line) == 1: return 1

    def get_an_int(self, arg, errmsg=None, min_value=None, max_value=None):
        """Another get_int() routine, this one simpler and less stylized
        than get_int(). We eval arg return it as an integer value or
        None if there was an error in parsing this.
        """
        ret_value = None
        if arg:
            try:
                # eval() is used so we will allow arithmetic expressions,
                # variables etc.
                ret_value = int(eval(arg)) 
            except (SyntaxError, NameError, ValueError):
                if errmsg:
                    self.errmsg(errmsg)
                else:
                    self.errmsg('Expecting an integer, got: %s.' % str(arg))
                return None

        if min_value and ret_value < min_value:
            self.errmsg('Expecting integer value to be at least %d, got: %d.' %
                        (min_value, ret_value))
            return None
        elif max_value and ret_value > max_value:
            self.errmsg('Expecting integer value to be at most %d, got: %d.' %
                        (max_value, ret_value))
            return None
        return ret_value

    def get_int(self, arg, default=1, cmdname=None):
        """If arg is an int, use that otherwise take default."""
        if arg:
            try:
                # eval() is used so we will allow arithmetic expressions,
                # variables etc.
                default = int(eval(arg)) 
            except (SyntaxError, NameError, ValueError):
                if cmdname:
                    self.errmsg('%s command: Expecting an integer, got: %s.' %
                                (cmdname, str(arg)))
                else:
                    self.errmsg('Expecting an integer, got: %s.' % str(arg))
                raise ValueError
        return default

    def get_onoff(self, arg, default=None, print_error=True):
        """Return True if arg is 'on' or 1 and False arg is 'off' or 0.
        Any other value is raises ValueError."""
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

    def get_pos_int(self, arg, min_value=0, default=1, cmdname=None):
        """If no argument use the default If arg is a positive int at
        least min_value, use that otherwise report an error."""
        if arg:
            try: 
                # eval() is used so we will allow arithmetic expressions,
                # variables etc.
                default = int(eval(arg))
                if default < min_value:
                    if cmdname:
                        self.errmsg(('%s command: Expecting a positive ' +
                                     'integer at least %d, got: %d.') 
                                    % (cmdname, min_value, default))
                    else: 
                        self.errmsg(('Expecting a positive ' +
                                     'integer at least %d, got: %d')
                                    % (min_value, default))
                    # Really should use something custom? 
                    raise ZeroDivisionError
                    
            except (SyntaxError, NameError, ValueError):
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
                if self.flush: self.logging_fileobj.flush()
            do_print = not self.logging_redirect
        if do_print:
            if out is None:
                out = self.stdout
            print >> out, msg,
            if self.flush: out.flush()

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

        # Evaluation routines like "exec" don't show useful location
        # info. In these cases, we will use the position before that in
        # the stack.  Hence the looping below which in practices loops
        # once and sometimes twice.
        while i_stack >= 0:
            frame_lineno = self.stack[i_stack]
            i_stack -= 1
            frame, lineno = frame_lineno

            # Next check to see that local variable breadcrumb exists and
            # has the magic dynamic value. 
            # If so, it's us and we don't normally show this.a
            if 'breadcrumb' in frame.f_locals:
                if self.run == frame.f_locals['breadcrumb']:
                    break
            
            filename = self.filename(self.canonic_filename(frame))

            self.msg_nocr('(%s:%s):' % (filename, lineno))
            fn_name = frame.f_code.co_name
            if fn_name and fn_name != '?':
                self.msg(" %s" % frame.f_code.co_name)
            else:
                self.msg("")

            if print_line:
                self.msg_nocr('+ ')
                pass
            if '__loader__' in self.curframe.f_globals:
                l = self.curframe.f_globals['__loader__']
                print l
                pass
            if 2 == linecache.getline.func_code.co_argcount:
                line = linecache.getline(filename, lineno)
            else:
                line = linecache.getline(filename, lineno, 
                                         self.curframe.f_globals)
                pass
            if line and len(line.strip()) != 0:
                self.print_source_line(lineno, line)
                pass

            if '<string>' != filename:
                break
            pass
        return

    def onecmd(self, line):

        """Interpret the argument as though it had been typed
        in response to the prompt.
        
        Checks whether this line is typed in the normal
        prompt or in a breakpoint command list definition """

        if not self.commands_defining:
            if self.cmdtrace: self.msg("+%s" % line)
            return cmd.Cmd.onecmd(self, line)
        else:
            return self.handle_command_def(line)

    def undefined_cmd(self, cmd, subcmd):
        """Error message when subcommand asked for but doesn't exist"""
        self.errmsg("Undefined %s command \"%s\"." % (cmd, subcmd))

    #### From SoC project. Look over.
    def _disconnect(self):
        """ Disconnect a connection. """
        if self.connection:
            self.connection.disconnect()
            self._rebind_output(self.orig_stdout)
            self._rebind_input(self.orig_stdin)
            self.connection = None
            if hasattr(self, 'local_prompt') and self.local_prompt is not None:
                self.prompt      = self.local_prompt
                self.local_prompt = None
                self.onecmd = lambda x: pydb.Pdb.onecmd(self, x)
        self.target = 'local'

    def _rebind_input(self, new_input):
        self.stdin = new_input

    def _rebind_output(self, new_output):
        self.stdout.flush()
        self.stdout = new_output
        if not hasattr(self.stdout, 'flush'):
            self.stdout.flush = lambda: None

    def remote_onecmd(self, line):
        """ All commands in 'line' are sent across this object's connection
        instance variable.
        """
        if not line:
            # Execute the previous command
            line = self.lastcmd
        # This is the simplest way I could think of to do this without
        # breaking any of the inherited code from pydb/pdb. If we're a
        # remote client, always call 'rquit' (remote quit) when connected to
        # a pdbserver. This executes extra code to allow the client and server
        # to quit cleanly.
        if 'quit'.startswith(line):
            line = 'rquit'
            self.connection.write(line)
            # Reset the onecmd method
            self.onecmd = pydb.Pdb.onecmd
            self.do_rquit(None)
            return
        if 'detach'.startswith(line):
            self.connection.write('rdetach')
            self.do_detach(None)
        self.connection.write(line)
        ret = self.connection.readline()
        if ret == '':
            self.errmsg('Connection closed unexpectedly')
            self.onecmd = lambda x: pydb.Pdb.onecmd(self, x)
            self.do_rquit(None)
        # The output from the command that we've just sent to the server
        # is returned along with the prompt of that server. So we keep reading
        # until we find our prompt.
        i = 1
        while ret.find('(Pydb)') != -1:
            if i == 100:
                # We're probably _never_ going to get that data and that
                # connection is probably dead.
                self.errmsg('Connection died unexpectedly')
                self.onecmd = pydb.Pdb.onecmd
                self.do_rquit(None)
            else:
                ret += self.connection.readline()
                i += 1

        # Some 'special' actions must be taken depending on the data returned
        if 'restart_now' in ret:
            self.connection.write('ACK:restart_now')
            self.errmsg('Pdbserver restarting..')
            # We've acknowledged a restart, which means that a new pdbserver
            # process is started, so we have to connect all over again.
            self._disconnect()
            import time
            time.sleep(3.0)
            if not self.do_target(self.target_addr):
                # We cannot trust these variables below to be in a
                # stable state. i.e. if the pdbserver doesn't come back up.
                self.onecmd = lambda x: pydb.Pdb.onecmd(self, x)
                return
        self.msg_nocr(ret)
        self.lastcmd = line
        return
    pass

if __name__ == '__main__':
    class TestCmd(Cmd):
        def do_a(self): return
        def do_b(self): return
        def do_a(self): return
        pass
    testcmd = TestCmd()
    print testcmd.get_cmds()
    pass
