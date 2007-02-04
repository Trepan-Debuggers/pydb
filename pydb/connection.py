# -*- coding: utf-8 -*-
"""Lower-level classes to support communication between separate
processes which might reside be on separate computers.

Can be used remote debugging via a socket or via a serial
communication line, or via a FIFO.

Modified from Matt Fleming's 2006 Google Summer of Code project.

$Id: connection.py,v 1.9 2007/02/04 12:50:36 rockyb Exp $"""

NotImplementedMessage = "This method must be overriden in a subclass"

### Exceptions
class ConnectionFailed(Exception): pass
class DroppedConnection(Exception): pass
class ReadError(Exception): pass
class WriteError(Exception): pass

class ConnectionInterface(object):
    """ This is an abstract class that specifies the interface a server
    connection class must implement. If a target is given, we'll
    set up a connection on that target
    """
    def connect(self, target):
        """Use this to set the target. It can also be specified
        on the initialization."""
        raise NotImplementedError, NotImplementedMessage

    def disconnect(self):
        """ This method is called to disconnect connections."""
        raise NotImplementedError, NotImplementedMessage

    def readline(self):
        """ This method reads a line of data of maximum length 'bufsize'
        from the connected debugger.
        """
        raise NotImplementedError, NotImplementedMessage

    def write(self, msg):
        """ This method is used to write to a debugger that is
        connected to this server.
        """
        raise NotImplementedError, NotImplementedMessage

# end ConnectionInterface

### This might go in a different file
# Note: serial protocol does not require the distinction between server and
# client.
class ConnectionSerial(ConnectionInterface):

    """ This connection class that allows a connection to a
    target via a serial line. 
    """

    def __init__(self):
        ConnectionInterface.__init__(self)
        self.input = None
        self.output = None

    def connect(self, device):
        """ Create our fileobject by opening the serial device for
        this connection. A serial device must be specified,
        (e.g. /dev/ttyS0, /dev/ttya, COM1, etc.).
        """
        self._dev = device
        try:
            self.input = open(self._dev, 'r')
            self.output = open(self._dev, 'w')
        except IOError,e:
            # Use e[1] for more detail about why the connection failed
            raise ConnectionFailed, e[1]

    def disconnect(self):
        """ Close the serial device. """
        if self.output is None and self.input is None:
            return
        self.output.close()
        self.input.close()

    def readline(self, bufsize=2048):
        try:
            line = self.input.readline(bufsize)
        except IOError, e:
            raise ReadError, e[1]
        return line

    def write(self, msg):
        if msg[-1] is not '\n':
            msg += '\n'
        try:
            self.output.write(msg)
            self.output.flush()
        except IOError, e:
            raise WriteError, e[1]

# end class ConnectionSerial

### This might go in a different file
import socket

class ConnectionServerTCP(ConnectionInterface):
    """This is an implementation of a server class that uses the TCP
    protocol as its means of communication.
    """
    def __init__(self):
        self.listening = False
        self._sock = self.output = self.input = None
        ConnectionInterface.__init__(self)
        
    def connect(self, addr, reuseaddr=True):
        """Set to allow a connection from a client. 'addr' specifies
        the hostname and port combination of the server.
        """
        try:
            h,p = addr.split(':')
        except ValueError:
            raise ConnectionFailed, 'Invalid address'
        self.host = h
        self.port = int(p)
        if not self.listening:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if reuseaddr:
                self._sock.setsockopt(socket.SOL_SOCKET,
                                      socket.SO_REUSEADDR, 1)
            try:
                self._sock.bind((self.host, self.port))
            except socket.error, e:
                # Use e[1] as a more detailed error message
                raise ConnectionFailed, e[1]
            self._sock.listen(1)
            self.listening = True
        self.output, addr = self._sock.accept()
        self.input = self.output

    def disconnect(self):
        if self.output is None or self._sock is None:
            return
        self.output.close()
        self._sock.close()
        self._sock = None
        self.listening = False

    def readline(self, bufsize=2048):
        try:
            line = self.input.recv(bufsize)
        except socket.error, e:
            raise ReadError, e[1]
        if not line:
            raise ReadError, 'Connection closed'
        if line[-1] != '\n': line += '\n'
        return line

    def write(self, msg):
        try:
            self.output.sendall(msg)
        except socket.error, e:
            raise WriteError, e[1]

# end ConnectionServerTCP

class ConnectionClientTCP(ConnectionInterface):
    """ A class that allows a connection to be made from a debugger
    to a server via TCP.
    """
    def __init__(self):
        """ Specify the address to connection to. """
        ConnectionInterface.__init__(self)
        self._sock = self.output = self.input = None
        self.connected = True

    def connect(self, addr):
        """Connect to the server. 'input' reads data from the
        server. 'output' writes data to the server.  Specify the
        address of the server (e.g. host:2020).  """
        try:
            h, p = addr.split(':')
        except ValueError:
            raise ConnectionFailed, 'Invalid address'
        self.host = h
        self.port = int(p)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._sock.connect((self.host, self.port))
        except socket.error, e:
            raise ConnectionFailed, e[1]
        self.connected = True

    def write(self, msg):
        try:
            self._sock.sendall(msg)
        except socket.error, e:
            raise WriteError, e[1]

    def readline(self, bufsize=2048):
        try:
            line = self._sock.recv(bufsize)
        except socket.error, e:
            raise ReadError, e[1]
        if not line:
            raise ReadError, 'Connection closed'
        return line

    def disconnect(self):
        """ Close the socket to the server. """
        # We shouldn't bail if we haven't been connected yet
        if self._sock is None:
            return
        else:
            self._sock.close()
        self._sock = None
        self.connected = False

#end ConnectionClientTCP

### This might go in a different file
import os

class ConnectionFIFO(ConnectionInterface):
    """A class for communicating akin to a named pipe. Since I haven't
    been able to figure out how to make os.mkfifo work, we'll use two
    files instead. Each process reads on one and writes on the
    other. The read of one is attached to the write of the other and
    vice versa.
    """

    def __init__(self, is_server):
        """is_server is a boolean which is used to ensure that the
        read FIFO of one process is attachd tothe write FIFO of the
        other. We arbitrarily call one the 'server' and one the
        'client'.
        """
        ConnectionInterface.__init__(self)
        ## FIXME check to see if is_server is boolean? 
        self.is_server = is_server
        self.inp = self.mode = self.filename = None
        
    def connect(self, filename, mode=0644):
        """Set up FIFOs for read and write connections based on the
        filename parameter passed. If no filename parameter is given,
        use the filename specified on instance creation.

        If there is a problem creating the FIFO we will return a
        ConnectionFailed exception."""

        self.filename  = filename
        self.fname_in  = self.infile()
        self.fname_out = self.outfile()
        self.open_outfile()

        self.mode = mode
        if self.is_server:
            # Wait for a connection from a client
            import time
            while not os.path.exists(self.fname_in):
                time.sleep(0.5)
        try:
            self.inp = open(self.fname_in, 'r')
        except IOError, e:
            raise ConnectionFailed, "%s: %s:" % (self.fname_out, e[1])
        
    def disconnect(self):
        """Close input and output files and remove from the filesystem
        the output file."""
        if not self.inp or not self.outp:
            return
        self.outp.close()
        outfile = self.outfile()
        if outfile is not None and os.path.exists(outfile):
            os.unlink(outfile)
        self.inp.close()
        self.inp = self.outp = None

    def infile(self):
        """Return the input FIFO name for the object"""
        if self.is_server:
            return self.filename + ".in"
        else:
            return self.filename + ".out"
        
    def open_outfile(self):
        """Return the output FIFO name for the object"""
        try:
            self.outp = open(self.fname_out, 'w')
        except IOError, e:
            raise ConnectionFailed, e[1]

    def outfile(self):
        """Return the output FIFO name for the object"""
        if self.is_server:
            return self.filename + ".out"
        else:
            return self.filename + ".in"
        
    def readline(self):
        try:
            line = self.inp.readline()
        except IOError, e:
            raise ReadError, e[1]
        if not line:
            raise ReadError, 'Connection closed'
        return line

    def write(self, msg):
        if msg[-1] != '\n': msg += '\n'
        try:
            self.outp.write(msg)
            self.outp.flush()
        except IOError, e:
            raise WriteError, e[1]
        
# end ConnectionFIFO

def import_hook(target):
    cls = target[target.rfind('.')+1:]
    target = target[:target.rfind('.')]
    try:
        pkg = __import__(target, globals(), locals(), [])
    except ImportError:
        return None
    return getattr(pkg, cls)
 
class ConnectionClientFactory:

    """A factory class that provides a connection for use with a client
    for example, with a target function.
    """
    # @staticmethod  # Works only on Python 2.4 and up
    def create(target):
        if target.lower() == 'tcp':
            return ConnectionClientTCP()
        elif target.lower() == 'serial':
            return ConnectionSerial()
        elif target.lower() == 'fifo':
            return ConnectionFIFO(is_server=True)
        else:
            return import_hook(target)
    create = staticmethod(create)   # Works on all Python versions

class ConnectionServerFactory:

    """A factory class that provides a connection to be used with
    a pdbserver.
    """
    # @staticmethod  # Works only on Python 2.4 and up
    def create(target):
        if target.lower() == 'tcp':
            return ConnectionServerTCP()
        elif target.lower() == 'serial':
            return ConnectionSerial()
        elif target.lower() == 'fifo':
            return ConnectionFIFO(is_server=True)
        else:
            return import_hook(target)
    create = staticmethod(create)   # Works on all Python versions

# When invoked as main program, do some basic tests 
if __name__=='__main__':
    # FIFO test
    import thread
    
    fname='test_file'
    server = ConnectionFIFO(is_server=True)
    client = ConnectionFIFO(is_server=False)
    thread.start_new_thread(server.connect, (fname,))
    client.connect(filename=fname)
    line = 'this is a test\n'
    client.write(line)
    ### FIXME
    import time
    time.sleep(0.05)

    l2 = server.readline()
    assert l2 == line
    line = 'Another test\n'
    server.write(line)
    l2 = client.readline()
    assert l2 == line
    client.disconnect()
    server.disconnect()

    # TCP test
    port = 8000
    while True:
        addr   = '127.0.0.1:%d' % port
        server = ConnectionServerTCP()
        try:
            thread.start_new_thread(server.connect, (addr,))
            print "port: %d" % port
            break
        except IOError, e:
            if e[0] == 'Address already in use':
                if port < 8010:
                    port += 1
                    print "port: %d" % port
                    continue
            import sys
            sys.exit(0)
            
    client = ConnectionClientTCP()
    client.disconnect()
    server.disconnect()
