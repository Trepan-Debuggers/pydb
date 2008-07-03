# $Id: save.cmd,v 1.3 2008/07/03 09:23:07 rockyb Exp $
# Test of running "save" command
#
set basename on
set autoeval on
set trace-commands on
save foo bar
save foo bar baz
save break ./savefile.txt
p len(open('./savefile.txt').readlines())
source ./savefile.txt
break 17
save break ./savefile.txt
source ./savefile.txt
p open('./savefile.txt').readlines()
save settings ./savefile.txt
source -v ./savefile.txt
p len(open('./savefile.txt').readlines())
save all ./savefile.txt
source ./savefile.txt
quit

