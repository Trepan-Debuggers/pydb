def func(num, f):
    f = open('log', 'w+')
    f.write('signal received\n')
    f.close()

import signal
signal.signal(signal.SIGUSR1, func)

x = 2
