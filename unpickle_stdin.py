#!/usr/bin/env python

import pickle
import struct
import sys

import afl


class RestrictedUnpickler(pickle.Unpickler):
    def load_global(self):
        raise ValueError('You shall not pass!')

afl.init()

unpickler = RestrictedUnpickler(sys.stdin)
try:
    o = unpickler.load()
except pickle.UnpicklingError:
    pass
except AttributeError:
    pass
except EOFError:
    pass
except ImportError:
    pass
except IndexError:
    pass
except KeyError:
    pass
except MemoryError:
    pass
except NameError:
    pass
except struct.error:
    pass
except SyntaxError:
    pass
except TypeError:
    pass
except UnicodeError:
    pass
except ValueError:
    pass
