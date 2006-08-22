"""$Id: sighandler.py,v 1.8 2006/08/22 01:14:35 rockyb Exp $
Handles signal handlers within Pydb.
"""
#FIXME:
#  - sigpass routine is probably not right - save old signal handler as
#    3rd entry of triplet and None if no old handler?
#  - remove pychecker errors.
#  - can remove signal handler altogether when
#         ignore=True, print=False, pass=True
#     
#
import signal

def lookup_signame(num):
    """Find the corresponding signal name for 'num'. Return None
    if 'num' is invalid."""
    for signame in signal.__dict__.keys():
        if signal.__dict__[signame] == num:
            return signame

def lookup_signum(name):
    """Find the corresponding signal number for 'name'. Return None
    if 'name' is invalid."""
    if hasattr(signal, name):
        return getattr(signal, name)
    else:
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
                            self._sigs[sig] = (False, False, True)
                        else:
                            self._sigs[sig] = (True, True, True)
                            old_handler = signal.signal(num, self.handle)
                            self.old_handlers[num] = old_handler
                else:
                    # Make an entry in the _sig dict for these signals
                    # even though they cannot be ignored or caught.
                    self._sigs[sig] = (False, False, True)

    def info_signal(self, signame):
        """Print information about a signal"""
        header='%-14s%-4s\t%-4s\t%s' % \
                ('Signal', 'Stop', 'Print', 'Pass to program\n')
        fmt='%-14s%-3s\t%-3s\t%s'
        if 'handle' in signame or 'signal' in signame:
            # This has come from pydb's info command
            if len(signame) == 1:
                self.pydb.msg(header)
                for sig in self._sigs.keys():
                    st, pr, pa = self._sigs[sig]
                    self.pydb.msg(fmt % (sig, st, pr, pa))
            else:
                self.info_signal(signame[1])
            return
            
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
        if not self._sigs.has_key(args[0]):
            return
        if len(args) == 1:
            self.info_signal(args[0])
            return
        
        # We can display information about 'fatal' signals, but not
        # change their actions.
        if args[0] in fatal_signals:
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

    def handle_stop(self, signame, change):
        """Change whether we stop or not when this signal is caught.
        If 'change' is True your program will stop when this signal
        happens."""
        if not isinstance(change, bool):
            return
        old_attr = self._sigs[signame]
        st, pr, pa = change, old_attr[1], old_attr[2]
        if st:
            # stop keyword implies print
            pr = True
        self._sigs[signame] = (st, pr, pa)
        return change

    def handle_pass(self, signame, change):
        """Change whether we pass this signal to the program (or not)
        when this signal is caught. If change is True, Pydb should allow
        your program to see this signal.
        """
        if not isinstance(change, bool):
            return
        old_attr = self._sigs[signame]
        st, pr, pa = old_attr[0], old_attr[1], change
        self._sigs[signame] = (st, pr, pa)
        return change

    # ignore is a synonym for nopass and noignore is a synonym for pass
    def handle_ignore(self, signame, change):
        if not isinstance(change, bool):
            return
        self.handle_pass(signame, not change)
        return change

    def handle_print(self, signame, change):
        """Change whether we print or not when this signal is caught."""
        if not isinstance(change, bool):
            return
        old_attr = self._sigs[signame]
        st, pr, pa = old_attr[0], change, old_attr[2]
        if not change:
            # noprint implies nostop
            st = False
        self._sigs[signame] = (st, pr, pa)
        return change

    def handle(self, signum, frame):
        """This method is called when a signal is received."""
        sig = lookup_signame(signum)
        st, pr, pa = self._sigs[sig]
        if pr:
            self.pydb.msg('Program received signal %s' % sig)
        if st:
            self.pydb.use_rawinput = False
            self.pydb.step_ignore = 1
            self.pydb.interaction(self.pydb.curframe, None)
        if pa:
            # pass the signal to the program 
            old_handler = self.old_handlers[signum]
            if old_handler:
                old_handler(signum, frame)
