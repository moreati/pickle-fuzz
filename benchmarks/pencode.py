"""Tiny binary JSON struct encoder.

We use this in preference to JSON primarily because it can handle the
difference between bytes and unicode strings, which is much more efficient
than encoding bytes-as-base64-in-JSON.

"""
import sys
import struct
import codecs

SZ = struct.Struct('!I')
REF = struct.Struct('!cI')

utf8_decode = codecs.getdecoder('utf8')


PY3 = sys.version_info >= (3,)
PY2 = not PY3

if PY3:
    unicode = str
    range_ = range
    long = int
    bytes_ = bytes
    py2str = ()  # Python 3 has a proper bytes/str distinction, no fudge type
else:
    range_ = xrange  # noqa
    py2str = str

    # Python 2 doesn't have an explicit bytes type, so don't
    # encode anything as bytes unless explicitly tagged
    bytes_ = ()


try:
    Bytes = sys.modules['__bubble__'].Bytes
except (KeyError, AttributeError):
    class Bytes(object):
        """Wrapper to tag a string to be transferred as bytes."""
        def __init__(self, bytestring):
            self.bytes = bytestring


def pencode(obj):
    """Encode the given Python primitive structure, returning a byte string."""
    p = Pencoder()
    p._pencode(obj, p.backrefs, p.out)
    return p.getvalue()


def bsz(seq):
    """Encode the length of a sequence as big-endian 4-byte uint."""
    return SZ.pack(len(seq))


def _pencode_bytes_(obj):
    return [b'b', bsz(obj), obj]

def _pencode_Bytes(obj):
    return [b'b', bsz(obj.bytes), obj.bytes]

def _pencode_py2str(obj):
    bs = obj.encode('ascii')
    return [b'S', bsz(bs), bs]

def _pencode_unicode(obj):
    bs = obj.encode('utf8')
    return [b's', bsz(bs), bs]

def _pencode_int(obj):
    bs = str(int(obj)).encode('ascii')
    return [b'i', bsz(bs), bs]

_pencode_long = _pencode_int

def _pencode_float(obj):
    bs = repr(float(obj)).encode('ascii')
    return [b'f', bsz(bs), bs]

SEQTYPE_CODES = {
    set: b'q',
    frozenset: b'Q',
    list: b'l',
    tuple: b't',
}
CODE_SEQTYPES = dict((v, k) for k, v in SEQTYPE_CODES.items())

VALTYPE_FUNCS = {
    bytes_: _pencode_bytes_,
    Bytes: _pencode_Bytes,
    py2str: _pencode_py2str,
    unicode: _pencode_unicode,
    int: _pencode_int,
    long: _pencode_long,
    float: _pencode_float,
}

class Pencoder(object):
    def __init__(self):
        self.out = []
        self.backrefs = {
            id(None): b'n',
            id(False): b'F',
            id(True): b'T',
        }

    def getvalue(self):
        return b''.join(self.out)

    def _pencode(self, obj, backrefs, out):
        """Inner function for encoding of structures."""
        objid = id(obj)
        if objid in backrefs:
            out.append(backrefs[objid])
            return
        else:
            backrefs[objid] = REF.pack(b'R', len(backrefs))

        otype = type(obj)
        if otype in VALTYPE_FUNCS:
            func = VALTYPE_FUNCS[otype]
            out.extend(func(obj))
        elif otype in SEQTYPE_CODES:
            code = SEQTYPE_CODES[otype]
            out.extend([code, bsz(obj)])
            _pencode = self._pencode
            for item in obj:
                _pencode(item, backrefs, out)
        elif isinstance(obj, dict):
            out.extend([b'd', bsz(obj)])
            _pencode = self._pencode
            for k in obj:
                _pencode(k, backrefs, out)
                _pencode(obj[k], backrefs, out)
        else:
            raise ValueError('Unserialisable type %s' % type(obj))


class obuf(object):
    """Wrapper to unpack data from a buffer."""
    def __init__(self, buf):
        self.buf = buf
        self.offset = 0

    def read_size(self):
        v = SZ.unpack_from(self.buf, self.offset)[0]
        self.offset += SZ.size
        return v

    def read_bytes(self, n):
        start = self.offset
        end = self.offset = start + n
        return self.buf[start:end]


def pdecode(buf):
    """Decode a pencoded byte string to a structure."""
    return PDecoder().decode(buf)


class PDecoder(object):
    def __init__(self):
        self.br_count = 3
        self.backrefs = {
            b'n': None,
            b'F': False,
            b'T': True,
        }
        self.d = {
            b'b': self._pdecode_bytes_,
            b's': self._pdecode_unicode,
            b'S': self._pdecode_py2str,
            b'i': self._pdecode_int,
            b'f': self._pdecode_float,
            b'l': self._pdecode_list,
            b'q': self._pdecode_set,
            b'Q': self._pdecode_frozenset,
            b't': self._pdecode_tuple,
            b'd': self._pdecode_dict,
        }


    def decode(self, buf):
        return self._decode(obuf(buf))

    def _pdecode_bytes_(self, obuf, br_id):
        sz = obuf.read_size()
        obj = obuf.read_bytes(sz)
        return obj

    def _pdecode_unicode(self, obuf, br_id):
        sz = obuf.read_size()
        obj = utf8_decode(obuf.read_bytes(sz))[0]
        return obj

    def _pdecode_py2str(self, obuf, br_id):
        sz = obuf.read_size()
        obj = obuf.read_bytes(sz)
        if not PY2:
            obj = obj.decode('ascii')
        return obj

    def _pdecode_int(self, obuf, br_id):
        sz = obuf.read_size()
        obj = int(obuf.read_bytes(sz))
        return obj

    def _pdecode_float(self, obuf, br_id):
        sz = obuf.read_size()
        obj = float(obuf.read_bytes(sz))
        return obj

    def _pdecode_list(self, obuf, br_id):
        sz = obuf.read_size()
        obj = []
        self.backrefs[br_id] = obj
        obj.extend(self._decode(obuf) for _ in range_(sz))
        return obj

    def _pdecode_set(self, obuf, br_id):
        sz = obuf.read_size()
        obj = set()
        self.backrefs[br_id] = obj
        obj.update(self._decode(obuf) for _ in range_(sz))
        return obj

    def _pdecode_frozenset(self, obuf, br_id):
        sz = obuf.read_size()
        obj = frozenset(self._decode(obuf) for _ in range_(sz))
        return obj

    def _pdecode_tuple(self, obuf, br_id):
        sz = obuf.read_size()
        obj = tuple(self._decode(obuf) for _ in range_(sz))
        return obj

    def _pdecode_dict(self, obuf, br_id):
        sz = obuf.read_size()
        obj = {}
        self.backrefs[br_id] = obj
        for _ in range_(sz):
            key = self._decode(obuf)
            value = self._decode(obuf)
            obj[key] = value
        return obj

    def _decode(self, obuf):
        code = obuf.read_bytes(1)
        if code in self.backrefs:
            return self.backrefs[code]

        if code == b'R':
            ref_id = obuf.read_size()
            obj = self.backrefs[ref_id]
            return obj

        br_id = self.br_count
        self.br_count += 1

        try:
            pdecode_func = self.d[code]
        except KeyError:
            raise ValueError('Unknown pack opcode %r' % code)
        obj = pdecode_func(obuf, br_id)

        self.backrefs[br_id] = obj
        return obj
