#!/usr/bin/env python

import pickle

import pyperf

import pencode

PROTOCOLS = [3] #range(pickle.HIGHEST_PROTOCOL+1)

CANDIDATES = [
#    ('py_pickle',   pickle._dumps,  pickle._loads),
    ('cpickle',     pickle.dumps,   pickle.loads),
    ('pencode',     pencode.pencode, pencode.pdecode),
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
    for name, dumps, loads in CANDIDATES:
        for protocol in PROTOCOLS:
            yield name, dumps, loads, protocol


if __name__ == '__main__':
    runner = pyperf.Runner()
    obj1 = setup()
    for name, dumps, loads, protocol in cases():
        s = dumps(obj1)
        obj2 = loads(s)
        assert obj1 == obj2
        runner.timeit(
            name='{name},proto={protocol},dumps'.format(name=name,protocol=protocol),
            stmt='dumps(obj)',
            globals={'dumps': dumps, 'obj': obj1},
        )
        runner.timeit(
            name='{name},proto={protocol},loads'.format(name=name,protocol=protocol),
            stmt='loads(s)',
            globals={'loads': loads, 's': s},
        )
