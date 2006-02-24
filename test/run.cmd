# Test of restart and linetracing 
# $Id: run.cmd,v 1.4 2006/02/24 09:44:33 rockyb Exp $
#
set basename on
set cmdtrace on
info program
continue
######################################
### Now restart with a breakpoint
######################################
break hanoi
show args
run
continue
info args
info program
where
where 2
######################################
### We should be at that breakpoint
### delete it and run again 
### this time changing a parameter
######################################
info break
delete 1
run 1
continue
show args
info args
####
quit


