# Test of restart and linetracing 
# $Id: run.cmd,v 1.5 2006/09/26 19:16:53 rockyb Exp $
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


