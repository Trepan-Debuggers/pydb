# 
# Test of breakpoint handling
# $Id: brkpt2.cmd,v 1.1 2006/02/21 15:30:37 rockyb Exp $
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
cont
clear
info break
###############################################################
### Test Delete: invalid/valid number.
###############################################################
delete 1
break 11
info break
delete 4
quit
