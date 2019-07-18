try:
    import cPickle as cpickle
except ImportError:
    import pickle as cpickle

import perf

PROTOCOLS = [0, 2]

runner = perf.Runner()

# TODO pyppickle

LENGTHS = [
    0,
    1,
    10,
    100,
    1000,
    10000,
    100000,
    1000000,
]

for protocol in PROTOCOLS:
    for zeros in LENGTHS:
        if protocol == 0:
            # A pathological pickle that Python wouldn't normally create,
            # but that the protocol allows
            s = ('F1.'+'0'*zeros+'\n.').encode('ascii')
        else:
            s = cpickle.dumps(float('1.'+'0'*zeros), protocol=protocol)
        runner.timeit(
            'loads,float,protocol=%i,len=%i' % (protocol, zeros+1),
            'loads(s)',
            globals={'loads': cpickle.loads, 's': s},
        )
    for exponent in LENGTHS:
        s = cpickle.dumps(10**exponent, protocol=protocol)
        runner.timeit(
            'loads,int,protocol=%i,len=%i' % (protocol, exponent+1),
            'loads(s)',
            globals={ 'loads': cpickle.loads, 's': s},
        )

    for n in LENGTHS:
        s = cpickle.dumps(('s'*n).encode('ascii'), protocol=protocol)
        runner.timeit(
            'loads,bytes,protocol=%i,len=%i' % (protocol, n),
            'loads(s)',
            globals={ 'loads': cpickle.loads, 's': s},
        )

    for n in LENGTHS:
        s = cpickle.dumps(u's'*n, protocol=protocol)
        runner.timeit(
            'loads,unicode,protocol=%i,len=%i' % (protocol, n),
            'loads(s)',
            globals={ 'loads': cpickle.loads, 's': s},
        )


