# coding: utf-8

import itertools
import json
import pytest

from pytest_donde import process_cov_output
from pytest_donde.record import Record
from pytest_donde.index_mapper import IndexMapper


def assert_equal_records(record1, record2):
    assert record1.nodeids() == record2.nodeids()
    for nodeid in record1.nodeids():
        assert record1.nodeid_to_locs(nodeid) == record2.nodeid_to_locs(nodeid)
    assert record1.nodeid_to_duration == pytest.approx(record2.nodeid_to_duration)

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

def test_record_setup_behavior():
    rec = Record()

    rec.register_coverage(NIDS[0], LOCS[0])
    rec.register_coverage(NIDS[1], LOCS[0])
    rec.register_coverage(NIDS[1], LOCS[1])
    rec.register_coverage(NIDS[1], LOCS[2])
    rec.register_coverage(NIDS[2], LOCS[0])
    rec.register_coverage(NIDS[2], LOCS[3])
    rec.register_coverage(NIDS[3], LOCS[2])
    rec.register_coverage(NIDS[4], LOCS[2])

    rec.register_coverage('dummy', LOCS[0])
    rec.discard_nodeid('dummy')
    rec._register_nodeid('dummy2')
    rec.discard_nodeid('dummy2')

    rec.register_duration(NIDS[2], DURATIONS[2])
    rec.register_duration(NIDS[0], DURATIONS[0])
    rec.register_duration(NIDS[1], DURATIONS[1])
    rec.register_duration(NIDS[3], DURATIONS[3])
    rec.register_duration(NIDS[4], DURATIONS[4])

    assert rec.nodeid_to_duration == {k: v for k,v in zip(NIDS, DURATIONS)}
    assert rec.nodeid_to_lindices == {
        NIDS[0]: {0, },
        NIDS[1]: {0,1,2, },
        NIDS[2]: {0,3, },
        NIDS[3]: {2, },
        NIDS[4]: {2, },
    }

examples_valid_equivalence_classes = [
    ['examples/records/example_valid01.json', 'examples/records/example_valid01_reordered01.json'],
    ['examples/records/example_valid02.json'],
    ['examples/records/example_valid03.json'],
]

examples_valid = [ex for eclass in examples_valid_equivalence_classes for ex in eclass]

examples_invalid = [
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
]

def test_record_setup_behavior_invalid():

    rec = Record.from_file(examples_valid[2])
    rec.assert_completeness()

    rec.nodeid_to_duration[NIDS[0]] = None

    with pytest.raises(Exception, match=r'Inconsistent record.*Missing duration for node test_a.py::test_x\[1-2-3\]'):
        rec.assert_completeness()

@pytest.mark.parametrize('example_name, match', [
    (ex, None) for ex in examples_valid
] + examples_invalid)
def test_json_example_validity(example_name, match):
    if match is None:
        Record.from_file(example_name)
    else:
        with pytest.raises(Exception, match=match):
            Record.from_file(example_name)

@pytest.mark.parametrize('example_name1, example_name2', [
    (ex1, ex2) for eclass in examples_valid_equivalence_classes for (ex1, ex2) in itertools.combinations_with_replacement(eclass, 2)
])
def test_json_example_equivalence(example_name1, example_name2):
    rec1 = Record.from_file(example_name1)
    rec2 = Record.from_file(example_name2)
    assert_equal_records(rec1, rec2)

@pytest.mark.parametrize('example_name', examples_valid)
def test_json_io_bijectivity(example_name):
    rec1 = Record.from_file(example_name)
    path ='/tmp/test.uncov.json'
    rec1.to_file(path)
    rec2 = Record.from_file(path)
    assert_equal_records(rec1, rec2)
