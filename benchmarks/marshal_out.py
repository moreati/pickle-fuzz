#!/usr/bin/env python
from __future__ import print_function

import ast
import marshal
import sys

x = ast.literal_eval(sys.argv[1])
m = marshal.dumps(x, 1)

print('Sending %r, marshalled as %r' % (x, m), file=sys.stderr)

try:
    # Python 3.x
    sys.stdout.buffer.write(m)
    sys.stdout.buffer.flush()
except AttributeError:
    # Python 2.x
    sys.stdout.write(m)
    sys.stdout.flush()
