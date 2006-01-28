# Test of restart and linetracing 
# $Id: run.cmd,v 1.1 2006/01/28 03:11:01 rockyb Exp $
#
set basename on
set cmdtrace on
continue
######################################
### Now restart with a breakpoint
break hanoi
show args
run
continue
info args
where
######################################
### We should be at that breakpoint
### delete it and run again 
### this time changing a parameter
info break
delete 1
run 1
continue
show args
info args
####
quit


