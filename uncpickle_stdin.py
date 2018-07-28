#!/usr/bin/env python3

import os
import pickle
import struct
import sys


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        raise pickle.UnpicklingError('You shall not pass!')


def main():
    unpickler = RestrictedUnpickler(sys.stdin.buffer)
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
    except OverflowError:
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


import afl
afl.init()
main()
os._exit(0)
