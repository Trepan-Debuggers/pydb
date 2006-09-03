"""$Id: sighandler.py,v 1.12 2006/09/03 00:33:09 rockyb Exp $
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

class SigHandler:

    """Store information about what we do when we handle a signal,

    - Do we print/not print when signal is caught
    - Do we pass/not pass the signal to the program
    - Do we stop/not stop when signal is caught

    All the methods to change these attributes return None on error, or
    True or False if we have set the action (pass/print/stop) for a signal
    handler.
    """
    def __init__(self, pydb): 
        self.pydb = pydb
        self._sigs = {}
    
        self.old_handlers = {}

        # set up signal handling for some known signals
        ignore= ['SIGALRM', 'SIGCHLD',  'SIGURG',  'SIGIO',      'SIGVTALRM'
                 'SIGPROF', 'SIGWINCH', 'SIGPOLL', 'SIGWAITING', 'SIGLWP',
                 'SIGCANCEL', 'SIGTRAP', 'SIGTERM', 'SIGQUIT', 'SIGILL',
                 'SIGINT']
        for sig in signal.__dict__.keys():
            if sig.startswith('SIG') and '_' not in sig:
                if str(sig) not in fatal_signals:
                    num = lookup_signum(sig)
                    if num:
                        if str(sig) in ignore:
                            self._sigs[sig] = [False, False, True]
                        else:
                            self._sigs[sig] = [True, True, True]
                            old_handler = signal.signal(num, self.handle)
                            self.old_handlers[num] = old_handler
                else:
                    # Make an entry in the _sig dict for these signals
                    # even though they cannot be ignored or caught.
                    self._sigs[sig] = [False, False, True]

    def info_signal(self, signame):
        """Print information about a signal"""
        header='%-14s%-4s\t%-4s\t%s' % \
                ('Signal', 'Stop', 'Print', 'Pass to program')
        fmt='%-14s%-3s\t%-3s\t%s'
        if 'handle' in signame or 'signal' in signame:
            # This has come from pydb's info command
            if len(signame) == 1:
                self.pydb.msg(header)
                self.pydb.msg("")
                for sig in self._sigs.keys():
                    st, pr, pa = self._sigs[sig]
                    self.pydb.msg(fmt % (sig, st, pr, pa))
            else:
                self.info_signal(signame[1])
            return

        if signame not in self._sigs.keys():
            try_signame = 'SIG'+signame
            if try_signame not in self._sigs.keys():
                self.pydb.msg("%s is not a signal name I know about."
                              % signame)
                return
            signame = try_signame
        s, pr, pa = self._sigs[signame]
        self.pydb.msg(header)
        self.pydb.msg(fmt % (signame, s, pr, pa))

    def action(self, arg):
        """Delegate the actions specified in 'arg' to another
        method.
        """
        if not arg:
            self.info_signal(['handle'])
            return
        args = arg.split()
        signame = args[0]
        if not self._sigs.has_key(signame):
            signame = "SIG"+signame
            if not self._sigs.has_key(signame):
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
        if not isinstance(set_stop, bool):
            return
        self._sigs[signame][0] = set_stop
        # stop keyword implies print
        if set_stop:
            self._sigs[signame][1] = True
        return set_stop

    def handle_pass(self, signame, set_pass):
        """Set whether we pass this signal to the program (or not)
        when this signal is caught. If set_pass is True, Pydb should allow
        your program to see this signal.
        """
        if not isinstance(set_pass, bool):
            return
        self._sigs[signame][2] = set_pass
        return set_pass

    def handle_ignore(self, signame, set_ignore):
        """'pass' and 'noignore' are synonyms. 'nopass and 'ignore' are
        synonyms."""
        if not isinstance(set_ignore, bool):
            return
        self.handle_pass(signame, not set_ignore)
        return set_ignore

    def handle_print(self, signame, set_print):
        """Set whether we print or not when this signal is caught."""
        if not isinstance(set_print, bool):
            return
        # noprint implies nostop
        if not set_print:
            self._sigs[signame][0] = False
        self._sigs[signame][1] = set_print
        return set_print

    def handle(self, signum, frame):
        """This method is called when a signal is received."""
        sig = lookup_signame(signum)
        st, pr, pa = self._sigs[sig]
        if pr:
            self.pydb.msg('Program received signal %s' % sig)
        if st:
            self.pydb.sig_received = True
            self.pydb.use_rawinput = False
            self.pydb.step_ignore = 1
            try:
                self.pydb.interaction(self.pydb.curframe, None)
            except IOError:
                # Caused by interrupting self.stdin.readline()
                pass
        if pa:
            # pass the signal to the program 
            old_handler = self.old_handlers[signum]
            if old_handler:
                old_handler(signum, frame)

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
    h = SigHandler(p)
    # Set to known value
    h.action('SIGUSR1 print pass stop')
    h.info_signal('USR1')
    # noprint implies no stop
    h.action('SIGUSR1 noprint')
    h.info_signal('USR1')
    h.action('foo nostop')
    # stop keyword implies print
    h.action('SIGUSR1 stop')
    h.info_signal('SIGUSR1')
    h.action('SIGUSR1 noprint')
    h.info_signal('SIGUSR1')
    h.action('SIGUSR1 nopass')
    h.info_signal('SIGUSR1')
    
