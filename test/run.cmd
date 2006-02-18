# Test of restart and linetracing 
# $Id: run.cmd,v 1.2 2006/02/18 02:12:36 rockyb Exp $
#
set basename on
set cmdtrace on
info program
continue
######################################
### Now restart with a breakpoint
break hanoi
show args
run
continue
info args
info program
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


