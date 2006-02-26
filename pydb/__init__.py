# -*- coding: UTF-8 -*-
app_name = 'Python Extended Debugger'
URL = 'http://bashdb.sourceforge.net/pydb/'

import sys
assert sys.version_info >= (2, 3, 5), _("Python %s or newer required") % '2.3.5'
from pydb import *

