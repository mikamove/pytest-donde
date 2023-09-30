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

    with pytest.raises(KeyError):
        m.to_index('c')
