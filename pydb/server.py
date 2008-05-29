"""$Id
Debugger Server code
"""
from gdb import Gdb
import sys
import connection

old_handler = None
server_addr = None

def setup_server(sig=None, protocol=None, addr=None):
    """Gather the parameters to set up a debugging server.
    This routine should be imported and called near the top of the
    program file.

    When signal "sig" is received, which by default is SIGUSR1,
    invoke_server() is called and passed the parameters used to setup
    this server.

    Protocol "protocol" is used for communication.

    If "addr" is specified clients can connect to this server
    at that address.
    """
    import signal
    if not sig:
        sig = signal.SIGUSR1

    global old_handler
    old_handler = signal.signal(sig, invoke_server)

    if protocol != None:
        proto = protocol
    else:
        proto = 'connection.ConnectionFIFO'

    global server_addr
    if addr != None:
        server_addr = proto + " " + addr 
    else:
        tmp = gettmpdir() + os.path.pathsep + str(os.getpid()) + "pydb"
        server_addr = proto + " " + tmp

def invoke_server(signum, frame):
    """This function sets up a signal handler, which when it
    traps a signal, starts a debugging server suitable for other
    debugging clients to connect to.
    """
    p = Gdb()
    p._sys_argv = list(sys.argv)
    
    from remote import RemoteWrapperServer
    p = RemoteWrapperServer(p)
    p.do_pydbserver(server_addr)

    p.set_trace(frame)
    
    import signal
    signal.signal(signum, old_handler)
