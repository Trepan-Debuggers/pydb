# Test of restart and linetracing 
# $Id: run2.cmd,v 1.3 2007/01/25 10:19:15 rockyb Exp $
#
set basename on
set trace-commands on
info program
continue
info program
######################################
### Program munges sys.argv
### see if we can rerun it okay
######################################
set interactive on
run 3 5
######################################
### Break of a fn name and
### Try a return where there is none
### either because not in subroutine
### or no "return" statement
######################################
set interactive off
break check_args
return
continue
return
######################################
### rerun wrong number of parameters
### that causes and exception
### and use "info program" to check
### termination
######################################
set interactive on
info program
run 5 10
continue
break gcd
continue
info program
set linetrace on
set interactive off
return
where
quit
