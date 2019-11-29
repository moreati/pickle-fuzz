#!/usr/bin/env python

import difflib
try:
    import cPickle as cpickle
except ImportError:
    import pickle as cpickle
import pickle as py_pickle

import pprint
import pyperf

import pencode

CANDIDATES = [
#    ('py_pickle',   pickle._dumps,  pickle._loads),
    ('cpickle',         cpickle.dumps,          cpickle.loads,          [3]),
    ('pencode',         pencode.pencode,        pencode.pdecode,        [None]),
#    ('cickle',      cickle.dumps,   pickle.dumps),
]

def setup():
    return [[
        1000+i,
        u'%d' % (1000+i,),
        42,
        42.0,
        # safepickle doesn't handle type==long
        10121071034790721094712093712037123,
        None,
        True,
        b'qwertyuiop',
        u'qwertyuiop',
        [u'q', u'w', u'e', u'r', u't', u'y', u'u', u'i', u'o', u'p'],
        (u'q', u'w', u'e', u'r', u't', u'y', u'u', u'i', u'o', u'p'),
        {u'q', u'w', u'e', u'r', u't', u'y', u'u', u'i', u'o', u'p'},
        frozenset([u'q', u'w', u'e', u'r', u't', u'y', u'u', u'i', u'o', u'p']),
        {u'e': 101, u'i': 105, u'o': 111, u'q': 113, u'p': 112,
         u'r': 114, u'u': 117, u't': 116, u'w': 119, u'y': 121},
        [u'q', u'w', u'e', u'r', u't', u'y', u'u', u'i', u'o', u'p', i],
        (u'q', u'w', u'e', u'r', u't', u'y', u'u', u'i', u'o', u'p', i),
        {u'q', u'w', u'e', u'r', u't', u'y', u'u', u'i', u'o', u'p', i},
        frozenset([u'q', u'w', u'e', u'r', u't', u'y', u'u', u'i', u'o', u'p', i]),
        {u'e': 101, u'i': 105, u'o': 111, u'q': 113, u'p': 112,
         u'r': 114, u'u': 117, u't': 116, u'w': 119, u'y': 121, u'x': i},
    ] for i in range(1000)]

def cases():
    for name, dumps, loads, protocols in CANDIDATES:
        for protocol in protocols:
            yield name, dumps, loads, protocol


if __name__ == '__main__':
    runner = pyperf.Runner()
    obj1 = setup()
    for name, dumps, loads, protocol in cases():
        if protocol is None:
            s = dumps(obj1)
        else:
            s = dumps(obj1, protocol)
        obj2 = loads(s)
        if obj1 != obj2:
            print(name)
            raise ValueError(''.join(difflib.context_diff(
                pprint.pformat(obj1).splitlines(keepends=True),
                pprint.pformat(obj2).splitlines(keepends=True),
                fromfile=name,
                tofile=name,
            )))
        runner.timeit(
            name='{name},proto={protocol},dumps'.format(name=name,protocol=protocol),
            stmt='dumps(obj)' if protocol is None else 'dumps(obj, protocol)',
            globals={'dumps': dumps, 'obj': obj1, 'protocol': protocol},
        )
        runner.timeit(
            name='{name},proto={protocol},loads'.format(name=name,protocol=protocol),
            stmt='loads(s)',
            globals={'loads': loads, 's': s},
        )
