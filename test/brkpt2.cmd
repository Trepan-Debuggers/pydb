# 
# Test of breakpoint handling
# $Id: brkpt2.cmd,v 1.4 2006/09/29 04:05:26 rockyb Exp $
#
set basename on
set cmdtrace on
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
quit
