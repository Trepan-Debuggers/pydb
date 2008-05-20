# $Id: save.cmd,v 1.1 2008/05/20 18:24:57 rockyb Exp $
# Test of running "save" command
#
set basename on
set autoeval on
set trace-commands on
save break ./savefile.txt
p len(open('./savefile.txt').readlines())
source ./savefile.txt
break 17
save break ./savefile.txt
source ./savefile.txt
p open('./savefile.txt').readlines()
save settings ./savefile.txt
source ./savefile.txt
p len(open('./savefile.txt').readlines())
save all ./savefile.txt
source ./savefile.txt
quit

