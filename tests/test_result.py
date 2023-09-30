# coding: utf-8

import json
import pytest

from pytest_donde import process_cov_output
from pytest_donde.outcome import Outcome
from pytest_donde.index_mapper import IndexMapper


LOCS = [
    ('a/b.py', 2),
    ('a/b.py', 5),
    ('a/c.py', 1),
    ('a/c.py', 2),
]

NIDS = [
    'test_a.py::test_x[1-2-3]',
    'test_b/test_b_1.py::test_b[0]',
    'test_b/test_b_1.py::test_b[1]',
    'test_c/test_c_1.py::test_c',
    'test_c/test_c_2.py::test_c',
]

DURATIONS = [
    0.1,
    0.4,
    0.5,
    0.9,
    12.1,
]

def test_outcome():
    r = Outcome()

    r.register_coverage(NIDS[0], LOCS[0])
    r.register_coverage(NIDS[1], LOCS[0])
    r.register_coverage(NIDS[1], LOCS[1])
    r.register_coverage(NIDS[1], LOCS[2])
    r.register_coverage(NIDS[2], LOCS[0])
    r.register_coverage(NIDS[2], LOCS[3])
    r.register_coverage(NIDS[3], LOCS[2])
    r.register_coverage(NIDS[4], LOCS[2])

    r.register_coverage('dummy', LOCS[0])
    r.discard_nodeid('dummy')
    r._register_nodeid('dummy2')
    r.discard_nodeid('dummy2')

    r.register_duration(NIDS[2], DURATIONS[2])
    r.register_duration(NIDS[0], DURATIONS[0])
    r.register_duration(NIDS[1], DURATIONS[1])
    r.register_duration(NIDS[3], DURATIONS[3])
    r.register_duration(NIDS[4], DURATIONS[4])

    r.to_file('/tmp/test.uncov.json')

    assert r.nodeid_to_duration == {
        NIDS[0]: DURATIONS[0],
        NIDS[1]: DURATIONS[1],
        NIDS[2]: DURATIONS[2],
        NIDS[3]: DURATIONS[3],
        NIDS[4]: DURATIONS[4],
    }
    assert r.nodeid_to_lindices == {
        NIDS[0]: set([0]),
        NIDS[1]: set([0,1,2]),
        NIDS[2]: set([0,3]),
        NIDS[3]: set([2]),
        NIDS[4]: set([2]),
    }

    r2 = Outcome.from_file('/tmp/test.uncov.json')

    assert r2.nodeid_to_duration == r.nodeid_to_duration
    assert r2.nodeid_to_lindices == r.nodeid_to_lindices
    assert r2._locs.index_to_val == r._locs.index_to_val
    assert r2._locs.index_to_val == r._locs.index_to_val
