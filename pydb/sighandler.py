"""$Id: sighandler.py,v 1.15 2006/09/09 01:24:08 rockyb Exp $
Handles signal handlers within Pydb.
"""
#TODO:
#  - Doublecheck handle_pass and other routines.
#  - can remove signal handler altogether when
#         ignore=True, print=False, pass=True
#     
#
import signal

def lookup_signame(num):
    """Find the corresponding signal name for 'num'. Return None
    if 'num' is invalid."""
    signames = signal.__dict__
    if num not in signames.values(): return None
    for signame in signames.keys():
        if signames[signame] == num: return signame
    # Something went wrong. Should have returned above

def lookup_signum(name):
    """Find the corresponding signal number for 'name'. Return None
    if 'name' is invalid."""
    if (name.startswith('SIG') and hasattr(signal, name)):
        return getattr(signal, name)
    else:
        name = "SIG"+name
        if hasattr(signal, name):
            return getattr(signal, name)
        return None

fatal_signals = ['SIGKILL', 'SIGSTOP']

class SignalManager:

    """Manages Signal Handling information for the debugger

    - Do we print/not print when signal is caught
    - Do we pass/not pass the signal to the program
    - Do we stop/not stop when signal is caught

    All the methods to change these attributes return None on error, or
    True or False if we have set the action (pass/print/stop) for a signal
    handler.
    """
    def __init__(self, pydb): 
        self.pydb    = pydb
        self.sigs    = {}
        self.siglist = [] # List of signals. Dunno why signal doesn't provide.
    
        # set up signal handling for these known signals
        ignore= ['SIGALRM', 'SIGCHLD',  'SIGURG',  'SIGIO',      'SIGVTALRM'
                 'SIGPROF', 'SIGWINCH', 'SIGPOLL', 'SIGWAITING', 'SIGLWP',
                 'SIGCANCEL', 'SIGTRAP', 'SIGTERM', 'SIGQUIT', 'SIGILL',
                 'SIGINT']

        self.info_fmt='%-14s%-4s\t%-4s\t%s'
        self.header  = self.info_fmt % ('Signal', 'Stop', 'Print',
                                        'Pass to program')

        for signame in signal.__dict__.keys():
            # Look for a signal name on this os.
            if signame.startswith('SIG') and '_' not in signame:
                self.siglist.append(signame)
                if signame not in fatal_signals + ignore:
                    self.sigs[signame] = self.SigHandler(signame, pydb.msg,
                                                         pydb.set_trace,
                                                         False)
    def print_info_signal_entry(self, signame):
        """Print status for a single signal name (signame)"""
        if signame not in self.sigs.keys():
            # Fake up an entry as though signame were in sigs.
            self.pydb.msg(self.info_fmt % (signame, 'False', 'False', 'True'))
            return
            
        sig_obj = self.sigs[signame]
        self.pydb.msg(self.info_fmt % (signame, str(sig_obj.stop is not None),
                                       str(sig_obj.print_method is not None),
                                       str(sig_obj.pass_along)))

    def info_signal(self, args):
        """Print information about a signal"""
        if len(args) == 0: return
        signame = args[0]
        if signame in ['handle', 'signal']:
            # This has come from pydb's info command
            if len(args) == 1:
                # Show all signal handlers
                self.pydb.msg(self.header)
                self.pydb.msg("")
                for signame in self.siglist:
                    self.print_info_signal_entry(signame)
                return
            else:
                signame = args[1]

        if signame not in self.siglist:
            try_signame = 'SIG'+signame
            if try_signame not in self.sigs.keys():
                self.pydb.msg("%s is not a signal name I know about."
                              % signame)
                return
            signame = try_signame
        self.pydb.msg(self.header)
        self.print_info_signal_entry(signame)

    def action(self, arg):
        """Delegate the actions specified in 'arg' to another
        method.
        """
        if not arg:
            self.info_signal(['handle'])
            return
        args = arg.split()
        signame = args[0]
        if not self.sigs.has_key(signame):
            signame = "SIG"+signame
            if not self.sigs.has_key(signame):
                return
        if len(args) == 1:
            self.info_signal(signame)
            return
        # We can display information about 'fatal' signals, but not
        # change their actions.
        if signame in fatal_signals:
            return

        # multiple commands might be specified, i.e. 'nopass nostop'
        for attr in args[1:]:
            if attr.startswith('no'):
                on = False
                attr = attr[2:]
            else:
                on = True
            if 'stop'.startswith(attr):
                self.handle_stop(signame, on)
            elif 'print'.startswith(attr) and len(attr) >= 2:
                self.handle_print(signame, on)
            elif 'pass'.startswith(attr):
                self.handle_pass(signame, on)
            else:
                self.pydb.errmsg('Invalid arguments')

    def handle_stop(self, signame, set_stop):
        """Set whether we stop or not when this signal is caught.
        If 'set_stop' is True your program will stop when this signal
        happens."""
        if set_stop:
            self.sigs[signame].stop = self.pydb.set_trace
            # stop keyword implies print AND nopass
            self.sigs[signame].print_method = self.pydb.msg
            self.sigs[signame].pass_along   = False
        else:
            self.sigs[signame].stop = None
        return set_stop

    def handle_pass(self, signame, set_pass):
        """Set whether we pass this signal to the program (or not)
        when this signal is caught. If set_pass is True, Pydb should allow
        your program to see this signal.
        """
        self.sigs[signame].pass_along = set_pass
        if set_pass:
            # Pass implies nostop
            self.sigs[signame].stop = None
        return set_pass

    def handle_ignore(self, signame, set_ignore):
        """'pass' and 'noignore' are synonyms. 'nopass and 'ignore' are
        synonyms."""
        self.handle_pass(signame, not set_ignore)
        return set_ignore

    def handle_print(self, signame, set_print):
        """Set whether we print or not when this signal is caught."""
        if set_print:
            self.sigs[signame].print_method = self.pydb.msg
        else:
            # noprint implies nostop
            self.sigs[signame].print_method = None
            self.sigs[signame].stop         = None
        return set_print

    ## SigHandler is a class private to SignalManager
    class SigHandler:
        """Store information about what we do when we handle a signal,

        - Do we print/not print when signal is caught
        - Do we pass/not pass the signal to the program
        - Do we stop/not stop when signal is caught

        Parameters:
           signame : name of signal (e.g. SIGUSR1 or USR1)
           print_method routine to use for "print"
           stop routine to call to invoke debugger when stopping
           pass_along: True is signal is to be passed to user's handler
        """
        def __init__(self, signame, print_method, stop, pass_along=True):

            self.signum = lookup_signum(signame)
            if not self.signum: return

            self.old_handler  = signal.getsignal(self.signum)
            self.pass_along   = pass_along
            self.print_method = print_method
            self.signame      = signame
            self.stop         = stop
            return

        def handle(self, signum, frame):
            """This method is called when a signal is received."""
            if self.print_method:
                self.print_method('Program received signal %s' % self.signame)
            if self.stop:
                self.stop(frame)
            elif self.pass_along:
                # pass the signal to the program 
                if self.old_handler:
                    self.old_handler(signum, frame)

# When invoked as main program, do some basic tests of a couple of functions
if __name__=='__main__':
    for signum in range(signal.NSIG):
        signame = lookup_signame(signum)
        if signame is not None:
            assert(signum == lookup_signum(signame))
            # Try without the SIG prefix
            assert(signum == lookup_signum(signame[3:]))

    import pydb
    p = pydb.Pdb()
    h = SignalManager(p)
    # Set to known value
    h.action('SIGUSR1 print pass stop')
    h.info_signal(['USR1'])
    # noprint implies no stop
    h.action('SIGUSR1 noprint')
    h.info_signal(['USR1'])
    h.action('foo nostop')
    # stop keyword implies print
    h.action('SIGUSR1 stop')
    h.info_signal(['SIGUSR1'])
    h.action('SIGUSR1 noprint')
    h.info_signal(['SIGUSR1'])
    h.action('SIGUSR1 nopass')
    h.info_signal(['SIGUSR1'])
    
