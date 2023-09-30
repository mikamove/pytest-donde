# coding: utf-8

import pytest

from pytest_donde.index_mapper import IndexMapper

def test_index_mapper():
    m = IndexMapper()
    m.register('b')
    m.register('a')

    assert m.index_to_val == {0: 'b', 1: 'a'}

    assert m.to_index('a') == 1
    assert m.to_index('b') == 0
    assert m.from_index(1) == 'a'
    assert m.from_index(0) == 'b'

    with pytest.raises(KeyError):
        m.from_index(99)
