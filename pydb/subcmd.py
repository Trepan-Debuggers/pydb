"""$Id: subcmd.py,v 1.1 2006/07/22 22:39:18 rockyb Exp $
Handles gdb-like subcommand processing.
"""

class Subcmd:
    """Gdb-like subcommand handling """
    def __init__(self, name, doc):
        self.name=name
        self.doc=doc
        self.subcmds={}

    def lookup(self, subcmd_prefix):
        """Find subcmd in self.subcmds"""
        for subcmd_name in self.subcmds.keys():
            if subcmd_name.startswith(subcmd_prefix) \
               and len(subcmd_prefix) >= self.subcmds[subcmd_name]['min']:
                return self.subcmds[subcmd_name]
        return None

    def _subcmd_helper(self, subcmd_name, obj, label=False):
        """Show help for a single subcommand"""
        if label:
            obj.msg_nocr("%s %s --" % (self.name, subcmd_name))

        entry=self.lookup(subcmd_name)
        if entry:
            obj.msg(entry['doc'])
            return
        obj.undefined_cmd("help", subcmd_name)

    def add(self, subcmd_name, subcmd_cb, min_len=0, in_list=True):
        """Add subcmd to the available subcommands for this object.
        It will have the supplied docstring, and subcmd_cb will be called
        when we want to run the command. min_len is the minimum length
        allowed to abbreviate the command. in_list indicates with the
        show command will be run when giving a list of all sub commands
        of this object. Some commands have long output like "show history"
        so we might not want to show that.
        """
        self.subcmds[subcmd_name] = {
            "callback": subcmd_cb,
            "name"    : subcmd_name,
            "doc"     : getattr(subcmd_cb, "__doc__"),
            "in_list" : in_list,
            "min"     : min_len}

    def do(self, obj, subcmd_name, arg):
        """Run subcmd_name with args using obj for the environent"""
        entry=self.lookup(subcmd_name)
        if entry:
            entry['callback'](arg)
        else:
            obj.undefined_cmd(self.name, subcmd_name)

    # Note: format of help is compatible with ddd.
    def help(self, obj, *args):
        """help for subcommands"""

        subcmd_prefix=args[0]
        if not subcmd_prefix or len(subcmd_prefix) == 0:
            obj.msg(self.doc)
            obj.msg("""
List of %s subcommands:
""" % (self.name))
            for subcmd_name in self.list():
                self._subcmd_helper(subcmd_name, obj, True)
            return

        entry=self.lookup(subcmd_prefix)
        if entry:
            self._subcmd_helper(entry['name'], obj)
        else:
            obj.errmsg("Unknown 'help %s' subcommand %s"
                       % (self.name, subcmd_prefix))

    def list(self):
        l=self.subcmds.keys()
        l.sort()
        return l


# When invoked as main program, invoke the debugger on a script
if __name__=='__main__':

    class FakeGdb:
        def msg_nocr(self, msg): print msg,
        def msg(self, msg): print msg
        def errmsg(self, msg): print msg

        def info_args(self, arg):
          "Print the arguments of the current function."
          print "a=1, b=2"
        def info_break(self, arg):
            "Without argument, list info about all breakpoints"
            print "no breakpoints"
        def set_args(self, arg):
            "Set argument list to give program being debugged when it is started"
            print "Not done yet"
        def set_basename(self, arg):
            "Set short filenames (the basename) in debug output"
            print "basename changed to %s" % arg

        def show_args(self, arg):
            "Show argument list to give debugged program on start"
            print "Argument list to give program is ''"
        def show_basename(self, arg):
            "Show if we are to show short of long filenames"
            print "basename is off."
        def show_cmdtrace(self, arg):
            "Show if we are to show debugger commands"
            print "cmdtraces is on."
    

    gdb=FakeGdb()
    info=Subcmd('info',
                """Generic command for showing things about the program being debugged.
             """)

    info.add('args', gdb.info_args)
    info.add('break', gdb.info_break)
    show=Subcmd('show',
                """Generic command for showing things about the debugger.""")
    show.add('args', gdb.show_args)
    show.add('basename', gdb.show_basename,)
    show.add('cmdtrace', gdb.show_cmdtrace)

    show.help(gdb, '')
    print "-" * 20
    show.help(gdb, "args")
    print "-" * 20
    show.do(gdb, "args", "")
    print "-" * 20
    info.help(gdb, '')
    print "-" * 20
    info.help(gdb, 'basename')
    set=Subcmd('set',
             """This command modifies parts of the debugger environment.
You can see these environment settings with the 'show' command.""")

    set.add('args', gdb.set_args)
    set.add('basename', gdb.set_basename)
    print "-" * 20
    set.help(gdb, '')
    print "-" * 20
    set.help(gdb, 'basename')
    print "-" * 20
    set.do(gdb, 'basename', 'off')

    print show.list()
    
