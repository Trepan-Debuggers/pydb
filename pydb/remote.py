"""$Id: remote.py,v 1.1 2008/05/29 02:50:50 rockyb Exp $
Contains all code for remote/out-of-process connections."""

from gdb import Gdb

class RemoteWrapper(Gdb):
    
    """An abstract wrapper class that provides common functionality
    for an object that wishes to use remote communication. Classes
    should inherit from this class if they wish to build an object
    capable of remote communication.
    """
    def __init__(self, pydb_object):
        Gdb.__init__(self)
        self.pydb = pydb_object
        self.connection = None
        self.use_rawinput = False
        self.running = True

    def do_restart(self, arg):
        """ Extend Gdb.do_restart to signal to any clients connected on
        a debugger's connection that this debugger is going to be restarted.
        All state is lost, and a new copy of the debugger is used.
        """
        # We don't proceed with the restart until the action has been
        # ACK'd by any connected clients
        if self.connection != None:
            self.msg('restart_now\n(Pydb)')
            line = ""
            while not 'ACK:restart_now' in line:
                line = self.connection.readline()
            self.do_rquit(None)
        else:
            self.msg("Re exec'ing\n\t%s" % self._sys_argv)
        import os
        os.execvp(self._sys_argv[0], self._sys_argv)

    def do_rquit(self, arg):
        """ Quit a remote debugging session. The program being executed
        is aborted.
        """
        if self.target == 'local':
            self.errmsg('Connected locally; cannot remotely quit')
            return
        self._rebind_output(self.orig_stdout)
        self._rebind_input(self.orig_stdin)
        self._disconnect()
        self.target = 'local'
        import sys
        sys.settrace(None)
        self.do_quit(None)

class RemoteWrapperServer(RemoteWrapper):
    def __init__(self, pydb_object):
        RemoteWrapper.__init__(self, pydb_object)

    def do_pydbserver(self, args):
        """ Allow a debugger to connect to this session.
The first argument is the type or protocol that is used for this connection
(which can be the name of a class that is avaible either in the current
working directory or in Python's PYTHONPATH environtment variable).
The next argument is protocol specific arguments (e.g. hostname and
port number for a TCP connection, or a serial device for a serial line
connection). The next argument is the filename of the script that is
being debugged. The rest of the arguments are passed as arguments to the
script file and are optional. For more information on the arguments for a
particular protocol, type `help pydbserver ' followed by the protocol name.
The syntax for this command is,

`pydbserver ConnectionClass comm scriptfile [args ...]'

"""
        try:
            target, comm = args.split(' ')
        except ValueError:
            self.errmsg('Invalid arguments')
            return
        if 'remote' in self.target:
            self.errmsg('Already connected remotely')
            return
        if self.connection: self.connection.disconnect()
        from connection import ConnectionServerFactory, ConnectionFailed
        self.connection = ConnectionServerFactory.create(target)
        if self.connection is None:
            self.errmsg('Unknown protocol')
            return
        try:
            self.msg('Listening on: %s' % comm)
            self.connection.connect(comm)
        except ConnectionFailed, err:
            self.errmsg("Failed to connect to %s: (%s)" % (comm, err))
            return
        self.pydbserver_addr = comm
        self.target = 'remote-pydbserver'
        self._rebind_input(self.connection)
        self._rebind_output(self.connection)

    def do_rdetach(self, arg):
        """ The rdetach command is performed on the pydbserver, it cleans
        things up when the client has detached from this process.
        Control returns to the file being debugged and execution of that
        file continues.
        """
        self._rebind_input(self.orig_stdin)
        self._rebind_output(self.orig_stdout)

        self.cmdqueue.append('continue')  # Continue execution

class RemoteWrapperClient(RemoteWrapper):
    
    """This is a wrapper class that provides remote capability to an
    instance of gdb.Gdb.
    """
    def __init__(self, pydb_object):
        RemoteWrapper.__init__(self, pydb_object)
        self.target_addr = ''

    def do_target(self, args):
        """ Connect to a target machine or process.
The first argument is the type or protocol of the target machine
(which can be the name of a class that is available either in the current
working directory or in Python's PYTHONPATH environment variable).
Remaining arguments are interpreted by the target protocol.  For more
information on the arguments for a particular protocol, type
`help target ' followed by the protocol name.

List of target subcommands:

target serial device-name -- Use a remote computer via a serial line
target tcp hostname:port -- Use a remote computer via a socket connection
"""
        if not args:
            args = self.target_addr
        try:
            target, addr = args.split(' ')
        except ValueError:
            self.errmsg('Invalid arguments')
            return False
        # If addr is ':PORT' fill in 'localhost' as the hostname
        if addr[0] == ':':
            addr = 'localhost'+addr[:]
        if 'remote' in self.target:
            self.errmsg('Already connected to a remote machine.')
            return False
        if self.connection: self.connection.disconnect()
        from connection import ConnectionClientFactory, ConnectionFailed
        self.connection = ConnectionClientFactory.create(target)
        try:
            self.connection.connect(addr)
        except ConnectionFailed, err:
            self.errmsg("Failed to connect to %s: (%s)" % (addr, err))
            return False
        # This interpreter no longer interprets commands but sends
        # them straight across this object's connection to a server.
        # XXX: In the remote_onecmd method we use the local_prompt string
        # to find where the end of the message from the server is. We
        # really need a way to get the prompt from the server for checking
        # in remote_onecmd, because it may be different to this client's.
        self.local_prompt = self.prompt
        self.prompt = ""
        self.target_addr = target + " " + addr
        line = self.connection.readline()
        if line == '':
            self.errmsg('Connection closed unexpectedly')
            self.do_quit(None)
        while '(Pydb)' not in line:
            line = self.connection.readline()
        self.msg_nocr(line)
        self.onecmd = self.remote_onecmd
        self.target = 'remote-client'
        return True
