"""Handles gdb-like subcommand processing."""
__revision="$Id: subcmd.py,v 1.9 2007/02/04 13:00:12 rockyb Exp $"
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

class Subcmd:
    """Gdb-like subcommand handling """
    def __init__(self, name, doc):
        self.name    = name
        self.doc     = doc
        self.subcmds = {}
        self.cmdlist = []

    def lookup(self, subcmd_prefix):
        """Find subcmd in self.subcmds"""
        for subcmd_name in self.subcmds.keys():
            if subcmd_name.startswith(subcmd_prefix) \
               and len(subcmd_prefix) >= self.subcmds[subcmd_name]['min']:
                return self.subcmds[subcmd_name]
        return None

    def _subcmd_helper(self, subcmd_name, obj, label=False, strip=False):
        """Show help for a single subcommand"""
        if label:
            obj.msg_nocr("%s %s --" % (self.name, subcmd_name))

        entry = self.lookup(subcmd_name)
        if entry:
            d = entry['doc']
            if strip:
                # Limit the help message to one line (delimited by '\n')
                if '\n' in d:
                    d = d[:d.find('\n')]
                # If the last character is a period, remove it.
                if d[-1] == '.': d = d[:d.find('.')]
            obj.msg(d)
            return
        obj.undefined_cmd("help", subcmd_name)

    def add(self, subcmd_name, subcmd_cb, min_len=0, in_list=True):
        """Add subcmd to the available subcommands for this object.
        It will have the supplied docstring, and subcmd_cb will be called
        when we want to run the command. min_len is the minimum length
        allowed to abbreviate the command. in_list indicates with the
        show command will be run when giving a list of all sub commands
        of this object. Some commands have long output like "show commands"
        so we might not want to show that.
        """
        self.subcmds[subcmd_name] = {
            "callback": subcmd_cb,
            "name"    : subcmd_name,
            "doc"     : subcmd_cb.__doc__,
            "in_list" : in_list,
            "min"     : min_len}

        # We keep a list of subcommands to assist command completion
        self.cmdlist.append(subcmd_name)

    def do(self, obj, subcmd_name, arg):
        """Run subcmd_name with args using obj for the environent"""
        entry=self.lookup(subcmd_name)
        if entry:
            entry['callback'](arg)
        else:
            obj.undefined_cmd(self.name, subcmd_name)

    # Note: format of help is compatible with ddd.
    def help(self, obj, *args):
        """help for subcommands."""

        subcmd_prefix = args[0]
        if not subcmd_prefix or len(subcmd_prefix) == 0:
            obj.msg(self.doc)
            obj.msg("""
List of %s subcommands:
""" % (self.name))
            for subcmd_name in self.list():
                self._subcmd_helper(subcmd_name, obj, True, True)
            return

        entry = self.lookup(subcmd_prefix)
        if entry:
            self._subcmd_helper(entry['name'], obj)
        else:
            obj.errmsg("Unknown 'help %s' subcommand %s"
                       % (self.name, subcmd_prefix))

    def list(self):
        l = self.subcmds.keys()
        l.sort()
        return l


# When invoked as main program, invoke the debugger on a script
if __name__ == '__main__':

    class FakeGdb:
        "A Mock Gdb class"
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
            """Set argument list to give program being debugged when it is started"""
            print "Not done yet"
        def set_basename(self, arg):
            "Set short filenames (the basename) in debug output"
            print "basename changed to %s" % arg

        def show_args(self, arg):
            """Show argument list to give debugged program on start"""
            print "Argument list to give program is ''"
        def show_basename(self, arg):
            "Show if we are to show short of long filenames"
            print "basename is off."
        def show_cmdtrace(self, arg):
            "Show if we are to show debugger commands"
            print "cmdtraces is on."


    gdb = FakeGdb()
    infocmd = Subcmd('info',
"""Generic command for showing things about the program being debugged. """)

    infocmd.add('args', gdb.info_args)
    infocmd.add('break', gdb.info_break)
    showcmd = Subcmd('show',
    """Generic command for showing things about the debugger.""")
    showcmd.add('args', gdb.show_args)
    showcmd.add('basename', gdb.show_basename,)
    showcmd.add('cmdtrace', gdb.show_cmdtrace)

    showcmd.help(gdb, '')
    print "-" * 20
    showcmd.help(gdb, "args")
    print "-" * 20
    showcmd.do(gdb, "args", "")
    print "-" * 20
    infocmd.help(gdb, '')
    print "-" * 20
    infocmd.help(gdb, 'basename')
    setcmd = Subcmd('set',
    """This command modifies parts of the debugger environment.
You can see these environment settings with the 'show' command.""")

    setcmd.add('args', gdb.set_args)
    setcmd.add('basename', gdb.set_basename)
    print "-" * 20
    setcmd.help(gdb, '')
    print "-" * 20
    setcmd.help(gdb, 'basename')
    print "-" * 20
    setcmd.do(gdb, 'basename', 'off')

    print showcmd.list()

