#!/usr/bin/python
# coding: utf-8

import marshal
import os
import sys

PROTOCOL = 1
SAMPLES = [
    None,
    False,
    True,
    0,
    0.0,
    0+0j,
    b'abc\xff',
    u'def£',
    [],
    [1,2,3],
    {},
    {'a':1, 'b':2, 'c':3},
    set(),
    set([1,2,3]),
    frozenset(),
    frozenset([1,2,3]),
]

PY_MAJOR, PY_MINOR = sys.version_info[0:2]
OUTPUT_DIR = 'py{}.{}'.format(PY_MAJOR, PY_MINOR)
OUTPUT_NAME = 'trial.proto{}.marshal'.format(PROTOCOL)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, OUTPUT_NAME)

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

with open(OUTPUT_PATH, 'wb') as f:
    for sample in SAMPLES:
        marshal.dump(sample, f, PROTOCOL)
        f.write(b'\n')
