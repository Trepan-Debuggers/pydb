#!/usr/bin/python
#$Id: python-version.py,v 1.1 2006/01/11 04:10:32 rockyb Exp $
"""Print the python version number as three space-delimited numbers, e.g.
2 4 2
"""
import sys
print "%d.%d.%d" % sys.version_info[0:3]
sys.exit(0)
