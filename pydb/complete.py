"""Command Completion routines"""
# -*- coding: utf-8 -*-
#   Copyright (C) 2007 Rocky Bernstein
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
import pydbcmd

def all_completions(obj, arg, add_left_context=True):
    """Return a list of command names that can start with the
    supplied command prefix."""
    if not arg:
        args=[]
        cmd_prefix=''
    else:
        args = arg.split()
        cmd_prefix=args[0]
            
    if len(args) > 1:
        # Subcommand completion
        complete_cmds = pydbcmd.Cmd.complete(obj, cmd_prefix, 0)
        if complete_cmds is not None and args[0] in complete_cmds:
            return complete_subcommand(obj, args, args[1], add_left_context)
        return None

    # command completion for initial word
    l=[]
    i=0
    while True:
        text=pydbcmd.Cmd.complete(obj, cmd_prefix, i)
        if text is None: break
        l.append(text)
        i += 1

    seen = {}
    completions=[]
    completions = list_completions(l, cmd_prefix, seen, completions)


    # Add in command completion of global and local variables
    fr=obj.curframe
    if fr:
        list_completions(fr.f_globals.keys() + fr.f_globals.keys(),
                        cmd_prefix, seen, completions)
    completions.sort()
    return completions

def complete_subcommand(obj, subcmd, prefix, add_left_context=True):
    """Print a list of completions for subcmd that start with text.
       We get the list of completions from obj._*subcmd*_cmds.
       If no completion we return the empty list.
       """
    completions = []
    subcmd_name = "%scmds" % subcmd[0]
    if add_left_context:
        left_context="%s " % subcmd[0]
    else:
        left_context=""
    seen={}
    if hasattr(obj, subcmd_name):
        subcmd_obj = getattr(obj, subcmd_name)
        if hasattr(subcmd_obj, "cmdlist"):
            completions = list_completions(l=subcmd_obj.cmdlist,
                                           prefix=prefix,
                                           seen=seen,
                                           completions=completions,
                                           left_context=left_context)
    if subcmd[0] in obj.first_can_be_obj:
        fr=obj.curframe
        if fr:
            l = fr.f_globals.keys() + fr.f_globals.keys()
            completions=list_completions(l=l,
                                         prefix=prefix,
                                         seen=seen,
                                         completions=completions,
                                         left_context=left_context)

    # help command should include all debugger commands.
    # FIXME: generalize
    if subcmd[0] == 'help':
        help_completions = all_completions(obj, prefix, False)
        if add_left_context:
            obj.do_where("")
            help_completions = map(lambda cmd: "help " + cmd,
                                   help_completions)
        completions += help_completions
        
    return completions

def list_completions(l, prefix, seen, completions, left_context=''):
    """Given a list l, add to completions those which start with prefix.
    We omit any that are in the dictionary of boolean values, 'seen'. To
    that we add those values in l that we've added. completions is returned.
    left_context is the prepended to each completion string.
    """
    for name in l:
        if name.startswith(prefix):
            if name not in seen.keys():
                completions.append("%s%s" % (left_context, name))
                seen[name]=True
    return completions

# When invoked as main program, some little tests
if __name__=='__main__':
    c=[]; seen={}
    l=["a", "an", "another", "also", "boy"]
    assert list_completions(l, "a",  seen, c) == ['a', 'an', 'another', 'also']
    assert list_completions(l, "b", seen, c) == [
        'a', 'an', 'another', 'also', 'boy']
    c=[]; seen={}
    assert list_completions(l, "a",  seen, c, "foo ") == [
        'foo a', 'foo an', 'foo another', 'foo also']
    c=[]; seen={}
    assert list_completions(l, "an", seen, c) == ['an', 'another']
    c=[]; seen={}
    assert list_completions(l, "b",  seen, c) == ['boy']
    c=[]; seen={}
    assert list_completions(l, "be", seen, c) == []
    c=[]; seen={}
    assert list_completions(l, "o",  seen, c, "foo") == []
    import pydb
    dbg = pydb.Pdb()
    dbg.curframe = None
    assert all_completions(dbg, "s") == [
        's', 'set', 'shell', 'show', 'signal', 'source', 'step']        
    assert all_completions(dbg, "set l") == [
        'set linetrace', 'set listsize', 'set logging']
    assert all_completions(dbg, "set l", False) == [
        'linetrace', 'listsize', 'logging']
    assert all_completions(dbg, "help s") == [
        's', 'set', 'shell', 'show', 'signal', 'source', 'step']
