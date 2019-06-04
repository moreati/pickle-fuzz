#!/usr/bin/env python

from __future__ import absolute_import,division, print_function
import array
import collections
import ast
import datetime
import decimal
import errno
import io
try:
    import lzma
except ImportError:
    from backports import lzma
import math
import os
import pickle
import re
import sys

try:
    unichr
except NameError:
    unichr = chr

PLATFORM = '{platform}_{bits}_{byteorder}'.format(
    platform=sys.platform,
    bits=int(math.log(sys.maxsize*2, 2)),
    byteorder=sys.byteorder,
)

SUPPORTED_PROTOCOLS = tuple(range(0, pickle.HIGHEST_PROTOCOL+1))

EmptyNT = collections.namedtuple('EmptyNT', '')
EasyAsNT = collections.namedtuple('EasyAsNT', 'a b c')


def examples():
    yield ('builtins', 'bool', {
            'false': False,
            'true': True,
    })
    yield ('builtins', 'bytearray', {
            'empty': bytearray(),
            'abc': bytearray(b'abc'),
            '2e8': bytearray(range(256)),
            '2e10': bytearray(1//255 for i in range(2**10)),
            '2e20': bytearray(1//255 for i in range(2**20)),
    })
    yield ('builtins', 'bytes', {
            'empty': b'',
            'abc': b'abc',
            '2e8': bytes(bytearray(range(256))),
            '2e10': bytes(bytearray(1//255 for i in range(2**10))),
            '2e20': bytes(bytearray(1//255 for i in range(2**20))),
    })
    yield ('builtins', 'complex', {
            'zero': 0+0j,
            'h2g2': 42+42j,
    })
    yield ('builtins', 'dict', {
            'empty': {},
            'abc123': {u'a': 1, u'b': 2, u'c': 3},
            '2e8': {unichr(i): i for i in range(256)},
            '2e10': {unichr(i): i for i in range(2**10)},
            '2e20': {unichr(i): i for i in range(2**20)},
    })
    yield ('builtins', 'float', {
            'zero': 0.0,
            'nzero': -0.0,
            'h2g2': 42.0,
            'ninf': float('-inf'),
            'pinf': float('+inf'),
            'nan': float('nan'),
    })
    yield ('builtins', 'frozenset', {
            'empty': frozenset(),
            'abc': frozenset({u'a', u'b', u'c'}),
            '2e8': frozenset({unichr(i) for i in range(256)}),
            '2e10': frozenset({unichr(i) for i in range(2**10)}),
            '2e20': frozenset({unichr(i) for i in range(2**20)}),
    })
    yield ('builtins', 'int', {
            'zero': 0,
            'h2g2': 42,
            '1e3': 1*10**3,
            '1e6': 1*10**6,
            '1e9': 1*10**9,
            '1e12': 1*10**12,
            '1e15': 1*10**15,
            '1e18': 1*10**18,
            '1e21': 1*10**21,
            '1e100': 1*10**100,
            '1e1000': 1*10**1000,
            '1e1000000': 1*10**1000000,
    })
    yield ('builtins', 'list', {
            'empty': [],
            'abc': [u'a', u'b', u'c'],
            '2e8': [unichr(i) for i in range(256)],
            '2e10': [unichr(i) for i in range(2**10)],
            '2e20': [unichr(i) for i in range(2**20)],
    })
    yield ('builtins', 'none', {
            'none': None,
    })
    yield ('builtins', 'set', {
            'empty': set(),
            'abc': {u'a', u'b', u'c'},
            '2e8': {unichr(i) for i in range(256)},
            '2e10': {unichr(i) for i in range(2**10)},
            '2e20': {unichr(i) for i in range(2**20)},
    })
    yield ('builtins', 'text', {
            'empty': u'',
            'abc': u'abc',
            '2e8': u''.join(unichr(i) for i in range(256)),
            '2e10': u''.join(unichr(i) for i in range(2**10)),
            '2e20': u''.join(unichr(i) for i in range(2**20)),
    })
    yield ('builtins', 'tuple', {
            'empty': (),
            'abc': (u'a', u'b', u'c'),
            '2e8': tuple(unichr(i) for i in range(256)),
            '2e10': tuple(unichr(i) for i in range(2**10)),
            '2e20': tuple(unichr(i) for i in range(2**20)),
    })

    if sys.version_info.major == 2:
        yield ('builtins', 'long', {
                'zero': ast.literal_eval('0L'),
                'h2g2': ast.literal_eval('42L'),
        })

    # array
    yield ('stdlib', 'array', {
            'empty': array.array('i'),
            '2e8': array.array('i', range(256)),
            '2e10': array.array('i', range(2**10)),
            '2e20': array.array('i', range(2**20)),
    })

    # collections
    yield ('stdlib', 'Counter', {
            'empty': collections.Counter(),
            'abc': collections.Counter(u'abc'),
    })
    yield ('stdlib', 'OrderedDict', {
            'empty': collections.OrderedDict(),
            'abc': collections.OrderedDict([(u'a', 1), (u'b', 2), (u'c', 3)]),
    })
    yield ('stdlib', 'defaultdict', {
            'empty': collections.defaultdict(int),
            'abc': collections.defaultdict(int, {u'a': 1, u'b': 2, u'c': 3}),
    })
    yield ('stdlib', 'namedtuple', {
            'empty': EmptyNT(),
            'abc': EasyAsNT(1, 2, 3),
    })

    # datetime
    yield ('stdlib', 'date', {
            'epoch': datetime.date(1970, 1, 1),
            'contact': datetime.date(2001, 1, 1),
    })
    yield ('stdlib', 'datetime', {
            'epoch': datetime.datetime(1970, 1, 1, 0, 0),
            'contact': datetime.datetime(2001, 1, 1, 0, 0),
    })
    yield ('stdlib', 'time', {
            'midnight': datetime.time(0, 0),
    })
    yield ('stdlib', 'timedelta', {
            'zero': datetime.timedelta(0),
    })
    yield ('stdlib', 'tzinfo', {
            'utc': datetime.tzinfo('UTC'),
    })

    # decimal
    yield ('stdlib', 'Decimal', {
            'zero': decimal.Decimal(0),
            'h2g2': decimal.Decimal(42),
    })

    # io
    yield ('stdlib', 'BytesIO', {
            'empty': io.BytesIO(b''),
            'abc': io.BytesIO(b'abc'),
    })

    # re
    yield ('stdlib', 'SRE_Pattern', {
            'empty': re.compile(''),
            'abc': re.compile('abc'),
    })


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST:
            return
        raise


def filename(category, kind, label, protocol):
    return 'cpython{major}{minor}/{platform}/{category}/{kind}/{label}.proto{protocol}.pkl.xz'.format(
        major=sys.version_info.major,
        minor=sys.version_info.minor,
        platform=PLATFORM,
        category=category,
        kind=kind,
        label=label,
        protocol=protocol,
    )


def objs():
    for category, kind, labels_objs in examples():
        for label, obj in labels_objs.items():
            for protocol in SUPPORTED_PROTOCOLS:
                yield category, kind, label, obj, protocol


def save_obj(category, kind, label, obj, protocol):
    path = filename(category, kind, label, protocol)
    mkdir_p(os.path.dirname(path))

    with lzma.open(path, 'wb') as f:
        try:
            pickle.dump(obj, f, protocol=protocol)
        except TypeError:
            print("pickle failed: {}".format(path), file=sys.stderr)


def main():
    for category, kind, label, obj, protocol in objs():
        save_obj(category, kind, label, obj, protocol)


if __name__ == '__main__':
    main()
