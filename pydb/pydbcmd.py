"""$Id: pydbcmd.py,v 1.3 2006/02/24 22:07:10 rockyb Exp $
A Python debugger command class.

Routines here have to do with parsing or processing commands,
generally (but not always) the are not specific to pydb. They are sort
of more oriented towards any gdb-like debugger. Also routines that need to
be changed from cmd are here.
"""
import cmd, sys, types

class Cmd(cmd.Cmd):

    def __init__(self):
        cmd.Cmd.__init__(self)
        self._user_requested_quit = False
        self.aliases              = {}
        self.cmdtrace             = False
        self.nohelp               = 'Undefined command: \"%s\". Try \"help\".'
        self.prompt               = '(Pydb) '
        self.rcLines              = []

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

    def get_onoff(self, arg, default=None):
        """Return True if arg is 'on' or 1 and False arg is an 'off' or 0
        Any other value is an error"""
        if not arg:
            if default is None:
                self.errmsg("Expecting 'on', 1, 'off', or 0. Got nothing.")
                raise ValueError
            return default
        if arg == '1' or arg == 'on': return True
        if arg == '0' or arg =='off': return False
        
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

    # Note: format of help is compatible with ddd.
    def help_subcommand(self, cmd, doc, subcmds, help_prog, args):
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

    def errmsg(self, msg):
        """Common routine for reporting debugger error messages.
           Derived classed may want to override this to capture output.
           """
        print "*** %s" % msg

    def msg(self, msg):
        """Common routine for reporting messages.
           Derived classed may want to override this to capture output.
           """
        print "%s" % msg

    def msg_nocr(self, msg):
        """Common routine for reporting messages (no carriage return).
           Derived classed may want to override this to capture output.
           """
        print "%s" % msg,

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
