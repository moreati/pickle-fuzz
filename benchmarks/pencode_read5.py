"""Tiny binary JSON struct encoder.

We use this in preference to JSON primarily because it can handle the
difference between bytes and unicode strings, which is much more efficient
than encoding bytes-as-base64-in-JSON.

"""
import io
import sys
import struct
import codecs

SZ = struct.Struct('!I')
REF = struct.Struct('!cI')

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


def bsz(seq, pack=SZ.pack):
    """Encode the length of a sequence as big-endian 4-byte uint."""
    return pack(len(seq))


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
            id(None): REF.pack(b'R', 0),
            id(False): REF.pack(b'R', 1),
            id(True): REF.pack(b'R', 2),
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


def pdecode(buf):
    """Decode a pencoded byte string to a structure."""
    return PDecoder().decode(buf)


class PDecoder(object):
    def __init__(self):
        self.br_count = 3
        self.backrefs = {
            0: None,
            1: False,
            2: True,
        }
        self.d = {
            ord(b'b'): self._pdecode_bytes_,
            ord(b's'): self._pdecode_unicode,
            ord(b'S'): self._pdecode_py2str,
            ord(b'i'): self._pdecode_int,
            ord(b'f'): self._pdecode_float,
            ord(b'l'): self._pdecode_list,
            ord(b'q'): self._pdecode_set,
            ord(b'Q'): self._pdecode_frozenset,
            ord(b't'): self._pdecode_tuple,
            ord(b'd'): self._pdecode_dict,
        }

    def decode(self, buf):
        file = io.BytesIO(buf)
        return self._decode(file.read, self.backrefs, self.d)

    def _pdecode_bytes_(self, read, sz, backrefs, d, br_id):
        return read(sz)

    def _pdecode_unicode(self, read, sz, backrefs, d, br_id,
                         utf8_decode=codecs.utf_8_decode):
        return utf8_decode(read(sz))[0]

    def _pdecode_py2str(self, read, sz, backrefs, d, br_id):
        return read(sz)
        #if not PY2:
        #    obj = obj.decode('ascii')

    def _pdecode_int(self, read, sz, backrefs, d, br_id):
        return int(read(sz))

    def _pdecode_float(self, read, sz, backrefs, d, br_id):
        return float(read(sz))

    def _pdecode_list(self, read, sz, backrefs, d, br_id):
        obj = []
        backrefs[br_id] = obj
        _decode = self._decode
        obj.extend(_decode(read, backrefs, d) for _ in range_(sz))
        return obj

    def _pdecode_set(self, read, sz, backrefs, d, br_id):
        obj = set()
        backrefs[br_id] = obj
        _decode = self._decode
        obj.update(_decode(read, backrefs, d) for _ in range_(sz))
        return obj

    def _pdecode_frozenset(self, read, sz, backrefs, d, br_id):
        _decode = self._decode
        return frozenset(_decode(read, backrefs, d) for _ in range_(sz))

    def _pdecode_tuple(self, read, sz, backrefs, d, br_id):
        _decode = self._decode
        return tuple(_decode(read, backrefs, d) for _ in range_(sz))
        
    def _pdecode_dict(self, read, sz, backrefs, d, br_id):
        obj = {}
        backrefs[br_id] = obj
        _decode = self._decode
        for _ in range_(sz):
            key = _decode(read, backrefs, d)
            value = _decode(read, backrefs, d)
            obj[key] = value
        return obj

    def _decode(self, read, backrefs, d, unpack=struct.Struct('!BI').unpack):
        b = read(5)
        code, ref_id_or_sz = unpack(b)
        if code == 82: # ord(b'R')
            obj = backrefs[ref_id_or_sz]
            return obj

        br_id = self.br_count
        self.br_count += 1

        #try:
        #pdecode_func = d[code]
        #except KeyError:
        #    raise ValueError('Unknown pack opcode %r' % code)
        obj = d[code](read, ref_id_or_sz, backrefs, d, br_id)

        backrefs[br_id] = obj
        return obj
