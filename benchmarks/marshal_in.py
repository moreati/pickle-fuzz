#!/usr/bin/env python
from __future__ import print_function

import marshal
import sys

try:
    # Python 3.x
    m = sys.stdin.buffer.read()
except AttributeError:
    m = sys.stdin.read()

x = marshal.loads(m)

print('Received %r, unmarshalled from %r' % (x, m), file=sys.stderr)
