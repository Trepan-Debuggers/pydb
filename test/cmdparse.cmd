# $Id: cmdparse.cmd,v 1.1 2006/01/26 23:06:26 rockyb Exp $
# This tests the functioning of some debugger command a
# parsing and set/show processing
print "********************************"
print "***   Set/show commands     ***"
print "*******************************"
############################
print "  args and baseneme..."
############################
set args this is a test
show args
set basename on
show basename
set basename foo
show basename
set basename off
show basename
set basename 0
show basename
set basename 1
show basename
############################
print "  listsize tests..."
#############################
show listsize
set listsize 20
show listsize
set listsize abc
set listsize -20
set listsize 20 forever
#############################
print "  linetrace tests..."
#############################
set linetrace delay
set linetrace delay 2
show linetrace delay
set linetrace delay 0.5
show linetrace delay
set linetrace delay foo
show linetrace delay
set linetrace on
show linetrace
set linetrace off
show linetrace
#############################
print "  prompt, misc..."
#############################
show prompt
show foo
