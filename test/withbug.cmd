# Test of running "info local" inside a "with" statement
# $Id: withbug.cmd,v 1.1 2007/11/01 02:31:10 rockyb Exp $
#
set basename on
set trace-commands on
continue 17
info local
quit
