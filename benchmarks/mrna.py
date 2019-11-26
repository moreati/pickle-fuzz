#
# Serializer.
#

import struct
import sys
import timeit

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

try:
    xrange
except NameError:
    xrange = range

PY24 = sys.version_info < (2, 5)
PY3 = sys.version_info > (3,)
if PY3:
    b = str.encode
    BytesType = bytes
    UnicodeType = str
    FsPathTypes = (str,)
    BufferType = lambda buf, start: memoryview(buf)[start:]
    long = int
    iteritems = dict.items
else:
    b = str
    BytesType = str
    FsPathTypes = (str, unicode)
    BufferType = buffer
    UnicodeType = unicode
    iteritems = dict.iteritems


(
    KIND_TRUE, KIND_FALSE, KIND_NONE, KIND_NEG_32, KIND_NEG_64, KIND_POS_32,
    KIND_POS_64, KIND_DOUBLE, KIND_UTF8, KIND_BYTES, KIND_LIST, KIND_TUPLE,
    KIND_SET, KIND_DICT, KIND_BLOB, KIND_SECRET, KIND_ERROR, KIND_CONTEXT,
    KIND_SENDER, KIND_KWARGS,
) = (
    chr(n).encode()
    for n in range(20)
)

_pack_u32 = lambda n: struct.pack('>I', n)
_pack_u64 = lambda n: struct.pack('>Q', n)
_pack_d64 = lambda n: struct.pack('>d', n)
_unpack_u32 = lambda s: struct.unpack('>I', s)[0]
_unpack_u64 = lambda s: struct.unpack('>Q', s)[0]
_unpack_d64 = lambda s: struct.unpack('>d', s)[0]
_bools = (KIND_FALSE, KIND_TRUE)


def _decode_s(read, _):
    length = _unpack_u32(read(4))
    encoded = read(length)
    if len(encoded) != length:
        raise ValueError('cannot decode: truncated input')
    return encoded


def _decode_dict(read, router):
    return dict(
        (_decode(read, router), _decode(read, router))
        for _ in xrange(_unpack_u32(read(4)))
    )


_DECODE_MAP = {
    KIND_TRUE: lambda read, _: True,
    KIND_FALSE: lambda read, _: False,
    KIND_NONE: lambda read, _: None,
    KIND_NEG_32: lambda read, _: -_unpack_u32(read(4)),
    KIND_NEG_64: lambda read, _: -_unpack_u64(read(8)),
    KIND_POS_32: lambda read, _: _unpack_u32(read(4)),
    KIND_POS_64: lambda read, _: _unpack_u64(read(8)),
    KIND_DOUBLE: lambda read, _: _unpack_d64(read(8)),
    KIND_UTF8: lambda read, router: _decode_s(read, router).decode('utf-8'),
    KIND_BYTES: _decode_s,
    KIND_LIST: lambda read, router: [
        _decode(read, router)
        for _ in xrange(_unpack_u32(read(4)))
    ],
    KIND_TUPLE: lambda read, router: tuple(
        _decode(read, router)
        for _ in xrange(_unpack_u32(read(4)))
    ),
    KIND_SET: lambda read, router: set(
        _decode(read, router)
        for _ in xrange(_unpack_u32(read(4)))
    ),
    KIND_DICT: lambda read, router: _decode_dict(read, router),
    #KIND_BLOB: lambda read, router: Blob(_decode_s(read, router)),
    #KIND_SECRET: lambda read, router: Secret(
    #    _decode_s(read, router).decode('utf-8')
    #),
    #KIND_ERROR: lambda read, router: CallError(
    #    _decode_s(read, router).decode('utf-8')
    #),
    #KIND_CONTEXT: lambda read, router: Context(router, _unpack_u32(read(4))),
    #KIND_SENDER: lambda read, router: Sender(
    #    router.context_by_id(_unpack_u32(read(4))),
    #    _unpack_u32(read(4))
    #),
    #KIND_KWARGS: lambda read, router: Kwargs(_decode_dict(read, router)),
}


def _encode_int(w, o):
    if o < 0:
        o = -o
        if o <= 2**32-1:
            w(KIND_NEG_32)
            w(_pack_u32(o))
        elif o <= 2**64-1:
            w(KIND_NEG_64)
            w(_pack_u64(o))
        else:
            raise ValueError('cannot encode %r: exceeds -(2**64-1)' % (o,))
    elif o <= 2**32-1:
        w(KIND_POS_32)
        w(_pack_u32(o))
    elif o <= 2**64-1:
        w(KIND_POS_64)
        w(_pack_u64(o))
    else:
        raise ValueError('cannot encode %r: exceeds 2**64-1' % (o,))


def _encode_double(w, o):
    w(KIND_DOUBLE)
    w(_pack_d64(o))


def _encode_s(w, o, kind=KIND_BYTES):
    l = len(o)
    if l > 2**32:
        raise ValueError('cannot encode: size %r exceeds 2**32' % (l,))
    w(kind)
    w(_pack_u32(l))
    w(o)


def _encode_list(w, o, kind=KIND_LIST, size=-1):
    w(kind)
    if size == -1:
        size = len(o)
    w(_pack_u32(size))
    for elem in o:
        _encode(w, elem)


def _encode_dict(w, o, kind=KIND_DICT):
    _encode_list(
        w,
        (vv for item in iteritems(o) for vv in item),
        kind,
        len(o),
    )


_ENCODE_MAP = {
    bool: lambda w, o: w(_bools[o]),
    type(None): lambda w, o: w(KIND_NONE),
    int: _encode_int,
    long: _encode_int,
    float: _encode_double,
    BytesType: _encode_s,
    UnicodeType: lambda w, o: _encode_s(w, o.encode('utf-8'), KIND_UTF8),
    #Blob: lambda w, o: _encode_s(w, o, KIND_BLOB),
    #Secret: lambda w, o: _encode_s(w, o.encode('utf-8'), KIND_SECRET),
    #CallError: lambda w, o: _encode_s(w, str(o).encode('utf-8'), KIND_ERROR),
    #Context: _encode_context,
    #Sender: _encode_sender,
    list: _encode_list,
    tuple: lambda w, o: _encode_list(w, o, KIND_TUPLE),
    set: lambda w, o: _encode_list(w, o, KIND_SET),
    dict: lambda w, o: _encode_dict(w, o, KIND_DICT),
    #Kwargs: lambda w, o: _encode_dict(w, o, KIND_KWARGS),
}


def _encode(w, o):
    try:
        return _ENCODE_MAP[o.__class__](w, o)
    except KeyError:
        for key in _ENCODE_MAP:
            if isinstance(o, key):
                _ENCODE_MAP[o.__class__] = _ENCODE_MAP[key]
                return _encode(w, o)
        raise TypeError('cannot serialize ' + str(o.__class__))


def encode(o):
    io = []
    _encode(io.append, o)
    return b('').join(io)


def _decode(read, router):
    op = read(1)
    if not op:
        raise ValueError('cannot decode: truncated input')

    try:
        return _DECODE_MAP[op](read, router)
    except KeyError:
        raise ValueError('cannot decode: unknown opcode %r' % (ord(op),))


def decode(s, router=None):
    return _decode(BytesIO(s).read, router)


if __name__ == '__main__':
    encode('foo')