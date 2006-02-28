#!/usr/bin/python -t
# $Id: test2.py,v 1.3 2006/02/28 19:46:11 rockyb Exp $ -*- Python -*-
"Unit test for Extended Python debugger "
import difflib, os, pprint, time, sys, unittest

top_builddir = "../"
if top_builddir[-1] != os.path.sep:
    top_builddir += os.path.sep
sys.path.insert(0, os.path.join(top_builddir, 'pydb'))
top_srcdir = ".."
if top_srcdir[-1] != os.path.sep:
    top_srcdir += os.path.sep
sys.path.insert(0, os.path.join(top_srcdir, 'pydb'))

import pydb                

builddir     = "."
if builddir[-1] != os.path.sep:
    builddir += os.path.sep

top_builddir = "../"
if top_builddir[-1] != os.path.sep:
    top_builddir += os.path.sep

srcdir = "."
if srcdir[-1] != os.path.sep:
    srcdir += os.path.sep

pydir        = os.path.join(top_builddir, "pydb")
pydb_short   = "pydb.py"
pydb_path    = os.path.join(pydir, pydb_short)

def raise_error():
    raise FloatingPointError

class PdbTests(unittest.TestCase):

    ## Don't use assertTrue to be compatible with older version of
    ## unittest
    
    def test_postmortem(self):
        """Test post-mortem processing"""
        try:
            raise_error()
        except FloatingPointError:
            t = sys.exc_info()[2]
            outfile    = 'test2.out'
            rightfile  = os.path.join(srcdir, 'test2.right')
            errfile    = 'test2.err'
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = open(outfile, 'w')
            sys.stderr = open(errfile, 'w')
            pydb.post_mortem(t=t, opts=None,
                             cmdfile=os.path.join(srcdir, 'pm.cmd'))
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            fromfile  = rightfile
            fromdate  = time.ctime(os.stat(fromfile).st_mtime)
            fromlines = open(fromfile, 'U').readlines()
            tofile    = outfile
            todate    = time.ctime(os.stat(tofile).st_mtime)
            tolines   = open(tofile, 'U').readlines()
            
            diff = list(difflib.unified_diff(fromlines, tolines, fromfile,
                                             tofile, fromdate, todate))
            
            if len(diff) == 0:
                os.unlink(outfile)
                os.unlink(errfile)
            for line in diff:
                print line,
            self.assertEqual(0, len(diff), "post-mortem test")
            return 

        
if __name__ == "__main__":
    unittest.main()
