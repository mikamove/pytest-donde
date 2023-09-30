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

@pytest.mark.parametrize('to_file, from_file', [
    (lambda r, path: r.to_file(path), lambda path: Outcome.from_file(path)),
    (lambda r, path: to_file_oldformat(r, path), lambda path: from_file_oldformat(path)),
], ids=['new', 'old'])
def test_outcome(to_file, from_file):
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

    to_file(r, '/tmp/test.uncov.json')

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

    r2 = from_file('/tmp/test.uncov.json')

    assert r2.nodeid_to_duration == r.nodeid_to_duration
    assert r2.nodeid_to_lindices == r.nodeid_to_lindices
    assert r2._locs.index_to_val == r._locs.index_to_val
    assert r2._locs.index_to_val == r._locs.index_to_val


def to_file_oldformat(outcome, path):
    outcome.assert_completeness()

    _nodeids = IndexMapper()

    for nodeid in outcome.nodeids():
        _nodeids.register(nodeid)

    data = {
        'lindex_to_loc': outcome._locs.index_to_val,
        'nindex_to_nodeid': _nodeids.index_to_val,
        'nindex_to_lindices': {_nodeids.to_index(nid): list(sorted(v)) for nid,v in outcome.nodeid_to_lindices.items()},
        'nindex_to_duration': {_nodeids.to_index(nid): v for nid, v in outcome.nodeid_to_duration.items()},
        'nodeid_to_lindices': {k: list(sorted(v)) for k,v in outcome.nodeid_to_lindices.items()},
        'nodeid_to_duration': outcome.nodeid_to_duration,
    }

    with open(path, 'w') as fo:
        json.dump(data, fo)


def from_file_oldformat(path):
    with open(path, 'r') as fi:
        data = json.load(fi)

    result = Outcome()

    lindex_to_loc = {int(k): tuple(v) for k,v in data['lindex_to_loc'].items()}
    for _, loc in sorted(lindex_to_loc.items()):
        result._locs.register(loc)

    nindex_to_nodeid = {int(k): v for k,v in data['nindex_to_nodeid'].items()}
    _nodeids = IndexMapper()
    for _, nodeid in sorted(nindex_to_nodeid.items()):
        _nodeids.register(nodeid)

    for nindex_str, lindices in sorted(data['nindex_to_lindices'].items()):
        nodeid = _nodeids.from_index(int(nindex_str))
        result.nodeid_to_lindices[nodeid] = set(map(int, lindices))

    for nindex_str, duration in data['nindex_to_duration'].items():
        nodeid = _nodeids.from_index(int(nindex_str))
        result.nodeid_to_duration[nodeid] = float(duration)

    result.assert_completeness()
    return result
