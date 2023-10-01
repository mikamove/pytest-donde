# coding: utf-8

import os
import shutil

import pytest

from pytest_donde.record import Record

ROOT_PATH = os.path.join(os.path.dirname(__file__), os.path.pardir)

def _setup_example(testdir, example_dir):
    shutil.copytree(os.path.join(ROOT_PATH, example_dir, 'src'),
                    os.path.join(str(testdir), 'src'))
    shutil.copyfile(os.path.join(ROOT_PATH, example_dir, 'test_src.py'),
                    os.path.join(str(testdir), 'test_src.py'))


REF_DATA = {
    'examples/example01': {
        'durations': {
            'test_src.py::test_f[0-0-0-2]': 0.3,
            'test_src.py::test_f[0-0-1-0]': 0.2,
            'test_src.py::test_f[0-1-0-10]': 0.2,
            'test_src.py::test_f[0-1-1--8]': 0.1,
            'test_src.py::test_f[1-0-0-14]': 0.2,
            'test_src.py::test_f[1-0-1-0]': 0.1,
            'test_src.py::test_f[1-1-0-16]': 0.1,
            'test_src.py::test_f[1-1-1--2]': 0.0
        }
    }
}

REF_DATA['examples/example02'] = REF_DATA['examples/example01']

@pytest.mark.parametrize('example_dir, pytest_args_additional, expected_node_ids_ordered', [
    ('examples/example01', tuple(), [
        'test_src.py::test_f[0-0-0-2]',
        'test_src.py::test_f[0-0-1-0]',
        'test_src.py::test_f[0-1-0-10]',
        'test_src.py::test_f[0-1-1--8]',
        'test_src.py::test_f[1-0-0-14]',
        'test_src.py::test_f[1-0-1-0]',
        'test_src.py::test_f[1-1-0-16]',
        'test_src.py::test_f[1-1-1--2]',
    ]),
    ('examples/example01', ('-k 0-0', ), [
        'test_src.py::test_f[0-0-0-2]',
        'test_src.py::test_f[0-0-1-0]',
        'test_src.py::test_f[1-0-0-14]',
    ]),
    ('examples/example02', tuple(), [
        'test_src.py::test_f[0-0-0-2]',
        'test_src.py::test_f[0-0-1-0]',
        'test_src.py::test_f[1-0-0-14]',
    ]),
])
def test_recorder_example01(testdir, example_dir, pytest_args_additional, expected_node_ids_ordered):
    _setup_example(testdir, example_dir)

    path_json = 'fkP0xt.json'
    testdir.runpytest('-v', '--donde=src', f'--donde-to={path_json}', *pytest_args_additional)
    assert os.path.exists(os.path.join(str(testdir), path_json))

    record = Record.from_file(os.path.join(str(testdir), path_json))

    assert record.nodeids() == expected_node_ids_ordered

    for nodeid, duration in REF_DATA[example_dir]['durations'].items():
        if nodeid in expected_node_ids_ordered:
            assert record.nodeid_to_duration[nodeid] == pytest.approx(duration, abs=1e-2)
        else:
            with pytest.raises(KeyError):
                record.nodeid_to_duration[nodeid]

def test_plugin_deactivated(testdir):
    _setup_example(testdir, 'examples/example01')
    testdir.runpytest('-v')
    assert not os.path.exists(os.path.join(str(testdir), 'donde.json'))
