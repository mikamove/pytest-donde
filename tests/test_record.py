# coding: utf-8

import json
import pytest

from pytest_donde import process_cov_output
from pytest_donde.record import Record
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

def test_record():
    r = Record()

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

    r2 = Record.from_file('/tmp/test.uncov.json')

    assert r2.nodeid_to_duration == r.nodeid_to_duration
    assert r2.nodeid_to_lindices == r.nodeid_to_lindices
    assert r2._locs.index_to_val() == r._locs.index_to_val()
    assert r2._locs.index_to_val() == r._locs.index_to_val()

def assert_equality(record1, record2):
    assert record1.nodeids() == record2.nodeids()
    for nodeid in record1.nodeids():
        assert record1.nodeid_to_locs(nodeid) == record2.nodeid_to_locs(nodeid)
    assert record1.nodeid_to_duration == pytest.approx(record2.nodeid_to_duration)

@pytest.mark.parametrize('example_name, match', [
    ('examples/records/example_valid01.json', None),
    ('examples/records/example_valid01_reordered01.json', None),
    ('examples/records/example_valid02.json', None),
    ('examples/records/example_invalid01.json',
     'lindex_to_loc.*not found in json'),
    ('examples/records/example_invalid02.json',
     'nodeid_to_lindices.*not found in json'),
    ('examples/records/example_invalid03.json',
     'nodeid_to_duration.*not found in json'),
    ('examples/records/example_invalid04.json',
     'Inconsistent record.*Missing duration for node test3'),
    ('examples/records/example_invalid05.json',
     'Inconsistent record.*Duplicate reference to.*(\'src1.py\', 1).*'),
    ('examples/records/example_invalid07.json',
     'Inconsistent record.*Missing definition for location index 77 referenced by nodeid test3'),
    ('examples/records/example_invalid07.json',
     'Inconsistent record.*Missing definition for location index 77 referenced by nodeid test3'),
])
def test_json_example_validity(example_name, match):
    if match is None:
        Record.from_file(example_name)
    else:
        with pytest.raises(Exception, match=match):
            Record.from_file(example_name)

@pytest.mark.parametrize('example_name1, example_name2', [
    ('examples/records/example_valid01.json', 'examples/records/example_valid01_reordered01.json'),
])
def test_json_example_equivalence(example_name1, example_name2):

    rec1 = Record.from_file(example_name1)
    rec2 = Record.from_file(example_name2)
    assert_equality(rec1, rec2)

