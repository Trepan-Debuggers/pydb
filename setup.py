#!/usr/bin/env python
#
# Copyright (C) 2006 Rocky Bernstein <rocky@panix.com>
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice
# appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND NOMINUM DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL NOMINUM BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from optparse import OptionParser
import sys, os

def do_cmd(cmd):
    """Run a command and possibly print it out first.
If the command fails, we die!"""
    global opts
    if opts.verbose: print cmd
    exit_status = os.system(cmd)
    if exit_status != 0: sys.exit(exit_status)

print """Note: we don't do python-style install yet.
But as a service we'll try to transfer your call, but don't expect too much."""

optparser = OptionParser()
optparser.add_option("--prefix", "", dest="prefix", action="store", 
                help="--prefix option to pass to configure", 
                metavar='[prefix directory]')

optparser.add_option("--install-scripts", "", dest="bindir",
                     action="store",
                     help="--bindir opton to pass to configure", 
                     metavar='[executable directory in PATH]')

optparser.add_option("--verbose", "-v", dest="verbose",
                     action="store_true", default=False,
                     help="lame attempt at verbosity ")

(opts, args) = optparser.parse_args()

do_install = do_build = False
for arg in args:
    if arg=='install':
        do_build=True
        do_install=True
    if arg=='build':
        do_build=True

## Okay, now time to configure, make, make install
configure_cmd='./configure '
if opts.prefix != None: config_opts += "--prefix %s" % opts.prefix
if opts.bindir != None: config_opts += "--bindir %s" % opts.bindir

do_cmd(configure_cmd)

if do_build: do_cmd("make")
if do_install: do_cmd("make install")   

sys.exit(0)

### Maybe someday we'll do this:

if False:
    from distutils.core import setup

    setup(
        name = "pydb",
        version = "0.1",
        description = "Improved Python Debugger",
        long_description = \
        """pydb is a slightly improved debugger Python. The command set
        more closely follows gdb's command set.
        
        The small additions include a 'restart', a 'frame' command and
        stepping skips over def statements.
        """,
        
        author = "Rocky Bernstein",
        author_email = "rocky@panix.com",
        license = "BSD-like",
        url = "http://bashdb.sourceforge.net/pydb",
        packages = ['pydb']
        )
### 

    
