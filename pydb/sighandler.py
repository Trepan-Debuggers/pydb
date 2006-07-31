"""$Id: sighandler.py,v 1.2 2006/07/31 00:06:24 rockyb Exp $
Handles signal handlers within Pydb.
"""
import signal

def lookup_signame(num):
    """Find the corresponding signal number for 'name'. Return None
    if 'name' is invalid."""
    if hasattr(signal, name):
        return getattr(signal, name)
    else:
        return None

def lookup_signum(name):
    """Find the corresponding signal number for 'name'. Return None
    if 'name' is invalid."""
    if hasattr(signal, name):
        return getattr(signal, name)
    else:
        return None

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
        # This list contains tuples made up of four items, one tuple for
        # every signal handler we've created. The tuples contain
        # (signal_num, stop, print, pass)
        self._sig_attr = []
        self._sig_stop = []
        self._sig_print = []
        self._sig_pass = []

        for sig in signal.__dict__.keys():
            if sig.startswith('SIG') and '_' not in sig:
                self._sig_attr.append(sig)

        # set up signal handling for some known signals
        # SIGKILL is non-maskable. Should we *really* include it here?
        fatal = ['SIGINT', 'SIGTRAP', 'SIGTERM', 'SIGQUIT', 'SIGILL', \
                 'SIGKILL', 'SIGSTOP']
        for sig in self._sig_attr:
            if str(sig) not in fatal:
                num = lookup_signum(sig)
                if num:
                    self._set_sig(sig, (True, True, True))
                    signal.signal(num, self.handle)
            else:
                self._set_sig(sig, (False, False, True))

    def _get_sig(self, name):
        st = name in self._sig_stop
        pr = name in self._sig_print
        pa = name in self._sig_pass
        return (st, pr, pa)

    def _set_sig(self, name, (st, pr, pa)):
        """Set the actions to be taken when a signal, specified by
        'name', is received.
        """
        if st:
            if name not in self._sig_stop:
                self._sig_stop.append(name)
        else:
            if name in self._sig_stop:
                self._sig_stop.pop(self._sig_stop.index(name))
        if pr:
            if name not in self._sig_print:
                self._sig_print.append(name)
        else:
            if name in self._sig_print:
                self._sig_print.pop(self._sig_print.index(name))
        if pa:
            if name not in self._sig_pass:
                self._sig_pass.append(name)
        else:
            if name in self._sig_pass:
                self._sig_pass.pop(self._sig_pass.index(name))

    def info_signal(self, signame):
        """Print information about a signal"""
        header='%-14s%-4s\t%-4s\t%s' % \
                ('Signal', 'Stop', 'Print', 'Pass to program\n')
        fmt='%-14s%-3s\t%-3s\t%s'
        if 'handle' in signame or 'signal' in signame:
            # This has come from pydb's info command
            if len(signame) == 1:
                self.pydb.msg(header)
                for sig in self._sig_attr:
                    s = sig in self._sig_stop
                    pr = sig in self._sig_print
                    pa = sig in self._sig_pass
                    self.pydb.msg(fmt % (sig,s,pr,pa))
            else:
                self.info_signal(signame[1])
            return
            
        s = signame in self._sig_stop
        pr = signame in self._sig_print
        pa = signame in self._sig_pass
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
        if args[0] in self._sig_attr:
            if len(args) == 1:
                self.info_signal(args[0])
                return
            # multiple commands might be specified, i.e. 'nopass nostop'
            for attr in args[1:]:
                if attr.startswith('no'):
                    on = False
                    attr = attr[2:]
                else:
                    on = True
                if attr.startswith('stop'):
                    self.handle_stop(args[0], on)
                elif attr.startswith('print'):
                    self.handle_print(args[0], on)
                elif attr.startswith('pass'):
                    self.handle_pass(args[0], on)
                else:
                    self.pydb.errmsg('Invalid arguments')

    def handle_stop(self, signum, change):
        """Change whether we stop or not when this signal is caught.
        If 'change' is True your program will stop when this signal
        happens."""
        if not isinstance(change, bool):
            return
        old_attr = self._get_sig(signum)
        st, pr, pa = change, old_attr[1], old_attr[2]
        if st:
            pr = True
        self._set_sig(signum, (st, pr, pa))
        return change

    def handle_pass(self, signum, change):
        """Change whether we pass this signal to the program (or not)
        when this signal is caught. If change is True, Pydb should allow
        your program to see this signal.
        """
        if not isinstance(change, bool):
            return
        old_attr = self._get_sig(signum)
        st, pr, pa = old_attr[0], old_attr[1], change
        self._set_sig(signum, (st, pr, pa))
        return change

    # ignore is a synonym for nopass and noignore is a synonym for pass
    def handle_ignore(self, signum, change):
        if not isinstance(change, bool):
            return
        self.handle_pass(not change)
        return change

    def handle_print(self, signum, change):
        """Change whether we print or not when this signal is caught."""
        if not isinstance(change, bool):
            return
        old_attr = self._get_sig(signum)
        st, pr, pa = old_attr[0], change, old_attr[2]
        if not change:
            # noprint implies nostop
            st = False
        self._set_sig(signum, (st, pr, pa))
        return change

    def handle(self, signum, frame):
        """This method is called when a signal is received."""
        sig = lookup_signame(signum)
        st, pa, pr = self._get_sig(sig)
        if pr:
            self.pydb.msg('Program received signal %s' % sig)
        if st:
            # XXX Rocky what's the best way to handle this? 
            self.pydb.use_rawinput = False
            self.pydb.interaction(self.pydb.curframe, None)
