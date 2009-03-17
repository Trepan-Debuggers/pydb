#!/usr/bin/env python
'Unit test for pydb.fns'
import os, sys, unittest

top_builddir = "../.."
if top_builddir[-1] != os.path.sep:
    top_builddir += os.path.sep
sys.path.insert(0, os.path.join(top_builddir, 'pydb'))
top_srcdir = "../.."
if top_srcdir[-1] != os.path.sep:
    top_srcdir += os.path.sep
sys.path.insert(0, os.path.join(top_srcdir, 'pydb'))

from fns import printf, print_argspec

class TestFns(unittest.TestCase):

    def test_fns_printf(self):
        self.assertEqual('037', printf(31, "/o"))
        self.assertEqual('00011111', printf(31, "/t"))
        self.assertEqual('!', printf(33, "/c"))
        self.assertEqual('0x21', printf(33, "/x"))
        return

    def test_fns_argspec(self):
        self.assertEqual('test_fns_argspec(self)', 
                         print_argspec(self.test_fns_argspec, 
                                              'test_fns_argspec'))
        self.assertFalse(print_argspec(None, 'invalid_fn'))
        return
    pass

if __name__ == '__main__':
    unittest.main()
