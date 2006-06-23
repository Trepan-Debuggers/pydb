"""$Id: fns.py,v 1.5 2006/06/23 08:53:48 rockyb Exp $
Functions to support the Extended Python Debugger."""
from optparse import OptionParser
import inspect, os, sys, re, traceback

# A pattern for a def header seems to be used a couple of times.
_re_def_str = r'^\s*def\s'
_re_def = re.compile(_re_def_str)
    
def find_function(funcname, filename):
    cre = re.compile(r'def\s+%s\s*[(]' % funcname)
    # cre = re.compile(r'%s\s*%s\s*[(]' % (_re_def_str, funcname))
    try:
        fp = open(filename)
    except IOError:
        return None
    # consumer of this info expects the first line to be 1
    lineno = 1
    answer = None
    while 1:
        line = fp.readline()
        if line == '':
            break
        if cre.match(line):
            answer = funcname, filename, lineno
            break
        lineno = lineno + 1
    fp.close()
    return answer

def get_confirmation(self, prompt):
    """Get a yes/no answer to prompt. self is an object that has
    a boolean noninteractive attribute and a msg method."""
    while True and not self.noninteractive:
        try:
            reply = raw_input(prompt)
        except EOFError:
            reply = 'no'
            reply = reply.strip().lower()
            if reply in ('y', 'yes'):
                return True
            elif reply in ('n', 'no'):
                return False
            else:
                self.msg("Please answer y or n.")
    return False
                

def get_exec_string(frame, max=30):
    """get_exec_string(frame, max)->prefix string Get
    the initial part the string in an exec command.  frame is the
    frame, and max characters of the string will be returned adjusted
    with a trailing ... and any quote mark.  A real hack until
    tracebacks do better in location reporting. """
    
    if frame == None: return None
    fi, li, fn, text = traceback.extract_stack(frame)[-1]
    re_exec = re.compile(r'(^|\s+)exec\s+(.*)')
    mo = re_exec.search(text)
    if mo:
        exec_arg = mo.group(2)
        if len(exec_arg) > max:
            if exec_arg[0] == '"' or \
                   exec_arg[0] == "'":
                quote=exec_arg[0]
            else:
                quote=''
                return "%s...%s" % (exec_arg[0:max], quote)
        else:
            return exec_arg
    return None

def is_def_stmt(line, frame):
    """Return True if we are looking at a def statement"""
    # Should really also check that operand is a code object
    return _re_def.match(line) and op_at_frame(frame)=='LOAD_CONST'

def is_exec_stmt(frame):
    """Return True if we are looking at an exec statement"""
    return frame.f_back is not None and op_at_frame(frame.f_back)=='EXEC_STMT'

def get_last_tb_or_frame_tb(frameno=1):

    """Intended to be used going into post mortem routines.  If
    sys.last_traceback is set, we will return that and assume that
    this is what post-mortem will want. If sys.last_traceback has not
    been set, then perhaps we *about* to raise an error and are
    fielding an exception. So assume that sys.exec_info()[frameno]
    is where we want to look."""

    traceback = sys.exc_info()[frameno]

    try:
        if inspect.istraceback(sys.last_traceback):
            # We do have a traceback so prefer that.
            traceback = sys.last_traceback
    except AttributeError:
        pass
    return traceback


from opcode import opname
def op_at_frame(frame, pos=None):
    code = frame.f_code.co_code
    if pos is None: pos = frame.f_lasti
    op = ord(code[pos])
    # print "+++ %s" % opname[op]
    return opname[op]

def process_options(pydb, debugger_name, program):
    usage_str="""%s [debugger-options] python-script [script-options...]

       Runs the extended python debugger""" % (program)

    optparser = OptionParser(usage=usage_str,
                             version="%prog @PACKAGE_VERSION@")

    optparser.add_option("-X", "--trace", dest="linetrace",
                         action="store_true", default=False, 
                         help="Show lines before executing them. " +
                         "This option also sets --batch")
    optparser.add_option("--batch", dest="noninteractive",
                         action="store_true", default=False, 
                         help="Don't run interactive commands shell on "+
                         "stops.")
    optparser.add_option("--basename", dest="basename",
                         action="store_true", default=False, 
                         help="Filenames strip off basename, (e.g.For testing)"
                         )
    optparser.add_option("-x", "--command", dest="command",
                         action="store", type='string', metavar='FILE',
                         help="Execute commands from FILE.")
    optparser.add_option("--cd", dest="cd",
                         action="store", type='string', metavar='DIR',
                         help="Change current directory to DIR.")
    optparser.add_option("-n", "--nx", dest="noexecute",
                         action="store_true", default=False, 
                         help="Don't execute commands found in any " +
                         "initialization files")
    optparser.add_option("-o", "--output", dest="output", metavar='FILE',
                         action="store", type='string',
                         help="Write debugger's output (stdout) " +
                         "to FILE")
    optparser.add_option("--error", dest="errors", metavar='FILE',
                         action="store", type='string',
                         help="Write debugger's error output (stderr) " +
                         "to FILE")

    # Set up to stop on the first non-option because that's the name
    # of the script to be debugged on arguments following that are
    # that scripts options that should be left untouched.  We would
    # not want to interpret and option for the script, e.g. --help, as
    # one one of our own, e.g. --help.

    optparser.disable_interspersed_args()

    # execfile() run out of Bdb.py uses sys.argv, so we have to
    # clobber it and make it what the debugged script expects. Also
    # the debugged script probably wants to look at sys.argv.
    # So we'll change sys.argv to look like the program were invoked
    # directly

    # Save the original just for use in restart (via exec)
    pydb._sys_argv = list(sys.argv)   
    (opts, sys.argv) = optparser.parse_args()

    if opts.linetrace: opts.noninteractive = True
    pydb.linetrace = opts.linetrace
    pydb.noninteractive = opts.noninteractive

    # --nx or -n
    if not opts.noexecute:
        # Read $HOME/.pydbrc and ./.pydbrc
        if 'HOME' in os.environ:
            envHome = os.environ['HOME']
            pydb.setup_source("%s.%src" % (envHome, debugger_name))
        pydb.setup_source(".%src" % debugger_name);

    if opts.cd:
        os.chdir(opts.cd)

    if opts.basename: pydb.basename = True

    # As per gdb, first we execute user initialization files and then
    # we execute any file specified via --command.
    if opts.command:
        pydb.setup_source(os.path.expanduser(opts.command), True);

    if opts.output:
        try: 
            sys.stdout = open(opts.output, 'w')
        except IOError, (errno, strerror):
            print "I/O in opening debugger output file %s" % opts.output
            print "error(%s): %s" % (errno, strerror)
        except ValueError:
            print "Could not convert data to an integer."
        except:
            print "Unexpected error in opening debugger output file %s" % \
                  opts.output
            print sys.exc_info()[0]
            sys.exit(2)

    if opts.errors:
        try: 
            sys.stderr = open(opts.errors, 'w')
        except IOError, (errno, strerror):
            print "I/O in opening debugger output file %s" % opts.errors
            print "error(%s): %s" % (errno, strerror)
        except ValueError:
            print "Could not convert data to an integer."
        except:
            print "Unexpected error in opening debugger output file %s" % \
                  opts.errors
            print sys.exc_info()[0]
            sys.exit(2)

def search_file(filename, path, cdir):
    """Return a full pathname for filename if we can find one. path
    is a list of directories to prepend to filename. If no file is
    found we'll return filename"""
    dirs=path.split(":")
    for dir in dirs:

        # Handle $cwd and $cdir
        if dir =='$cwd': dir='.'
        elif dir == '$cdir': dir = cdir

        tryfile = os.path.abspath(os.path.join(dir, filename))
        if os.path.isfile(tryfile):
            return tryfile
    return filename
    
def show_onoff(bool):
    """Return 'on' for True and 'off' for False, and ?? for anything
    else."""
    if bool == True: return "on"
    if bool == False: return "off"
    return "??"

