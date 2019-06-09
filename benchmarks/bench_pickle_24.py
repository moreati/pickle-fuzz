import cPickle as cpickle

import timeit

PROTOCOLS = [0, 2]

# TODO pyppickle

def repeat(setup='pass', stmt='pass', repeat=timeit.default_repeat):
    precision = 3
    t = timeit.Timer(stmt, setup)
    # determine number so that 2 <= total time < 20
    for i in range(1, 10):
        number = 10**i
        try:
            x = t.timeit(number)
        except:
            t.print_exc()
            sys.exit(1)
        if x >= 2:
            break
    try:
        r = t.repeat(repeat, number)
    except:
        t.print_exc()
        sys.exit(1)

    return [(t, number) for t in sorted(r)]


def eng(seconds, number):
    nsec = seconds * 1e9 / number
    if nsec < 1000: return nsec, 'ns'
    usec = nsec / 1000
    if usec < 1000: return usec, 'us'
    msec = usec / 1000
    if msec < 1000: return msec, 'ms'
    return seconds, 's'


LENGTHS = [0, 1, 10, 100, 1000, 10000, 100000, 1000000]
for protocol in PROTOCOLS:
    for zeros in LENGTHS:
        if protocol == 0:
            # A pathological pickle that Python wouldn't normally create,
            # but that the protocol allows
            s = ('F1.'+'0'*zeros+'\n.').encode('ascii')
        else:
            s = cpickle.dumps(float('1.'+'0'*zeros), protocol=protocol)
        print 'loads,float,protocol=%i,len=%i' % (protocol, zeros+1)
        times = repeat(
            setup='from cPickle import loads; s=%r' % s,
            stmt='loads(s)',
            repeat=5,
        )
        print ', '.join('%.3f %s' % eng(*r) for r in sorted(times))
        print times

    for exponent in LENGTHS:
        s = cpickle.dumps(10L**exponent, protocol=protocol)
        print 'loads,int,protocol=%i,len=%i' % (protocol, exponent+1)
        times = repeat(
            setup='from cPickle import loads; s=%r' % s,
            stmt='loads(s)',
            repeat=5,
        )
        print ', '.join('%.3f %s' % eng(*r) for r in sorted(times))
        print times

    for n in LENGTHS:
        s = cpickle.dumps(('s'*n).encode('ascii'), protocol=protocol)
        print 'loads,bytes,protocol=%i,len=%i' % (protocol, n)
        times = repeat(
            setup='from cPickle import loads; s=%r' % s,
            stmt='loads(s)',
            repeat=5,
        )
        print ', '.join('%.3f %s' % eng(*r) for r in sorted(times))
        print times

    for n in LENGTHS:
        s = cpickle.dumps(u's'*n, protocol=protocol)
        print 'loads,unicode,protocol=%i,len=%i' % (protocol, n)
        times = repeat(
            setup='from cPickle import loads; s=%r' % s,
            stmt='loads(s)',
            repeat=5,
        )
        print ', '.join('%.3f %s' % eng(*r) for r in sorted(times))
        print times

