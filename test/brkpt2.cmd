# 
# Test of breakpoint handling
# $Id: brkpt2.cmd,v 1.10 2008/11/24 21:24:28 rockyb Exp $
#
set basename on
set trace-commands on
###############################################################
### Clear nonexist break; 
###############################################################
clear
###############################################################
### Multiple breakpoints on a line and clearing all
###############################################################
break 28
break gcd.py:28
info break
clear 28
###############################################################
### Clear by current line number
###############################################################
break 28
continue
clear
info break
###############################################################
### Test Delete: invalid/valid number.
###############################################################
delete 1
break 11
info break
delete 4
tbreak 31
continue
info break
###############################################################
### Test Continue with a line number
###############################################################
c 35
info break
where 2
###############################################################
### Test frame command
###############################################################
frame 
frame abs(-1*2)
frame -3
frame -2
frame 0
###############################################################
### Test ignore
###############################################################
ignore 0 1
ignore 4 -1
## FIXME: need a real ignore test, not just invalid cases
quit
