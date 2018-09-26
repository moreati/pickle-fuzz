#!/usr/bin/env python3

import subprocess


PYTHONS = [
    ("python2.7",   [0,1,2]),
    ("python3.3",   [0,1,2,3]),
    ("python3.4",   [0,1,2,3,4]),
    ("python3.5",   [0,1,2,3,4]),
    ("python3.6",   [0,1,2,3,4]),
    ("python3.7",   [0,1,2,3,4]),
    ("pypy",        [0,1,2]),
    ("pypy3",       [0,1,2,3,4]),
]

INTEGERS = [
    1,
    1000,
    1000000,
    1000000000,
    1000000000000,
    2**62,
    2**64,
]

CODE = "import pickle, sys; pickle.dump(%d, getattr(sys.stdout, 'buffer', sys.stdout), %d)"
for python, protocols in PYTHONS:
    print(python)
    for protocol in protocols:
        print('\t%d' % protocol)
        for i in INTEGERS:
            p = subprocess.check_output(
                    [python, '-u', '-c', CODE % (i, protocol)],
            )
            print('\t\t%r' % (p,))
