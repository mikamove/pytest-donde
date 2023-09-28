# coding: utf-8

import pytest

from pytest_donde import index_mapper

def test_index_mapper():
    m = index_mapper.IndexMapper()
    m.register('b')
    m.register('a')

    assert m.index_to_val == {0: 'b', 1: 'a'}

    assert m.to_index('z') == 2

    assert m.index_to_val == {0: 'b', 1: 'a', 2: 'z'}

    assert m.to_index('a') == 1
    assert m.to_index('b') == 0
    assert m.from_index(1) == 'a'
    assert m.from_index(0) == 'b'

    with pytest.raises(Exception, match='attempt to register an already known value'):
        m.register('a')


    with pytest.raises(KeyError):
        m.from_index(99)
