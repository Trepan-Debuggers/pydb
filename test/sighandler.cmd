info signal hup
info handle SIGHUP
handle SIGINT
handle SIGINT stop pass noprint
info handle SIGINT
handle SIGINT print
info handle SIGINT
handle SIGINT nopass noprint nostop
info signal SIGINT
# try changing fatal signal handlers (which are unchangable)
handle SIGKILL stop
info handle KILL
handle SIGSTOP print
info signal sigstop
info signal INT
quit
