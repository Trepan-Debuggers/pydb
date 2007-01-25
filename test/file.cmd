# 
# Test of the 'file' command
# $Id: file.cmd,v 1.4 2007/01/25 10:19:15 rockyb Exp $
#
set trace-commands on
file hanoi.py
info line
where 2
step 1+1
where 2
quit
