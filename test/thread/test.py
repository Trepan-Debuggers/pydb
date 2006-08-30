#!/usr/bin/env python
"""Run a bunch of threading programs with line tracing
to make sure we don't hang tracing them."""
import os
#prof2.py should work but takes a long time to run.
#tests=['t2.py', 'thread1.py', 'q.py', 'prof2.py']
tests=['t2.py', 'thread1.py', 'q.py']
for test in tests:
    print "=" * 60
    print test
    print "=" * 60
    cmd='python ../../pydb/pydb.py --threading --trace %s' % test
    os.system(cmd)
