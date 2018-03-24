#!/usr/bin/env python

import cPickle
import cStringIO
import pickletools
from hypothesis import assume, example, given, strategies as st
from hypothesis import HealthCheck, settings, unlimited


opcodes = st.sampled_from([opcode.code for opcode in pickletools.opcodes])
opargs = st.one_of(
    st.sampled_from([
        b"c__builtin__\neval\n(S'print(123)'\ntR",
        b"__class__",
        b"__getattribute__",
    ]),
    st.binary(),
)
ops = st.one_of([opcodes, opargs])

@st.composite
def pickles(draw):
    xs = draw(st.lists(ops, min_size=1))
    return b''.join(xs)

@given(st.lists(ops, min_size=1))
@settings(
    max_examples=1<<32, max_iterations=1<<32,
    deadline=None, timeout=unlimited,
    suppress_health_check=[
        HealthCheck.hung_test,
    ],
)
def test_environment_is_unchanged(l):
    s = b''.join(l)
    unpickler = cPickle.Unpickler(cStringIO.StringIO(s))
    unpickler.find_global = None
    lcls = locals()
    gbls = globals()
    try:
        unpickler.load()
    except Exception:
        pass
    assert lcls == locals()
    assert gbls == globals()
