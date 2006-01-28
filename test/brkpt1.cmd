# 
# Test of breakpoint handling
# $Id: brkpt1.cmd,v 1.1 2006/01/28 01:38:06 rockyb Exp $
#
# Test the simplest of breakpoints
set basename on
set cmdtrace on
info break
break 29
info break
###############################################################
### Test enable/disable...
enable
enable 1
info break
enable foo
disable 1
disable
info break
################################################################
### Try setting breakpoints outside of the file range...
break 0
break 1
break 99
# 
# list breakpoints
L
#### Try deleting breakpoints...
delete 10
delete 1
###############################################################
### *** Test using file:line format on break...
break hanoi.py:22
break ./hanoi.py:22
break ./hanoi.py:0
break ./dbg-test1.sh:1955
info break
###############################################################
### *** Test breakpoints with conditions...
condition 1 x==0
condition 2 y > 25
info break
condition 2
info break
condition x==1
condition bad
condition 30 y==1
quit
