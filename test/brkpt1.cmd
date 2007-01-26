# 
# Test of breakpoint handling
# $Id: brkpt1.cmd,v 1.7 2007/01/26 13:14:35 rockyb Exp $
#
set base on
set trace-commands on
###############################################################
# Test the breakpoint by line number
###############################################################
info break
break 30
info break
###############################################################
### Test enable/disable...
###############################################################
enable
enable 1
info break
enable foo
disable 1
disable
info break
################################################################
### Try setting breakpoints outside of the file range...
###############################################################
break 0
break 1
break 99
# 
# list breakpoints
L
###############################################################
### *** Test using file:line format on break...
###############################################################
break hanoi.py:22
break ./hanoi.py:22
break ./hanoi.py:0
break ./dbg-test1.sh:1955
info break
#### Try deleting breakpoints...
delete 10
delete 1
clear 22
info break
break 22
###############################################################
### *** Test breakpoints with conditions...
###############################################################
condition 1 x==0
### FIXME: there is no condition 2!
### condition 2 y > 25
condition 2+2 y > 25
info break
### FIXME: there still is no condition 2
### condition 2
condition 4
info break
condition x==1
condition bad
condition 30 y==1
condition 0 y==1
###############################################################
### *** Test breakpoints by function name
###############################################################
break hanoi
clear hanoi
q
