"""$Id: connection.py,v 1.1 2006/09/08 15:54:24 rockyb Exp $
Lower-level classes to support out-of-process (or out of computer)
communication.

Can be used remote debugging via a socket or via a serial
communication line, or via a FIFO.

From Matt Fleming's 2006 Google Summer of Code project.
"""

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

### This might go in a different file
import os
class ConnectionServerFIFO(ConnectionInterface):
    """ This class implements a named pipe for communication between
    a pdbserver and client.
    """
    def __init__(self):
        ConnectionInterface.__init__(self)
        self.input = self.output = self._filename = self._mode = None

    def connect(self, name, mode=0644):
        self._filename = name
        self._file_in = self._filename+'0'
        self._file_out = self._filename+'1'
        self._mode = mode
        try:
            os.mkfifo(self._file_in, self._mode)
            os.mkfifo(self._file_out, self._mode)
        except OSError, e:
            raise ConnectionFailed, e[1]
        self.input = open(self._file_in, 'r')
        self.output = open(self._file_out, 'w')

    def disconnect(self):
        """ Disconnect from the named pipe. """
        if not self.input or not self.output:
            return
        self.output.close()
        self.input.close()
        self.input = self.output = None
        os.unlink(self._file_in)
        os.unlink(self._file_out)


    def readline(self):
        """ Read a line from the named pipe. """
        try:
            # Using readline allows the data to be read quicker, don't
            # know why.
            line = self.input.readline()
        except IOError, e:
            raise ReadError, e[1]
        if not line:
            raise ReadError, 'Connection closed'
        return line

    def write(self, msg):
        if msg[-1] != '\n': msg += '\n'
        try:
            self.output.write(msg)
            self.output.flush()
        except IOError, e:
            raise WriteError, e[1]

class ConnectionClientFIFO(ConnectionInterface):
    """ This class is the client class for accessing a named pipe
    used for communication between client and pdbserver.
    """
    def __init__(self):
        ConnectionInterface.__init__(self)
        self.input = self.output = self._filename = self._mode = None
        
    def connect(self, name, mode=0644):
        self._filename = name
        self._file_in = self._filename+'1'
        self._file_out = self._filename+'0'
        self._mode = mode
        try:
            self.output = open(self._file_out, 'w')
            self.input = open(self._file_in, 'r')
        except IOError, e:
            raise ConnectionFailed, e[1]
        
    def disconnect(self):
        if not self.input or not self.output:
            return
        self.output.close()
        self.input.close()
        self.input = self.output = None

    def readline(self):
        try:
            line = self.input.readline()
        except IOError, e:
            raise ReadError, e[1]
        if not line:
            raise ReadError, 'Connection closed'
        return line

    def write(self, msg):
        if msg[-1] != '\n': msg += '\n'
        try:
            self.output.write(msg)
            self.output.flush()
        except IOError, e:
            raise WriteError, e[1]
        
