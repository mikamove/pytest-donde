# coding: utf-8

import pytest

from pytest_donde.index_mapper import IndexMapper

def test_index_mapper():
    m = IndexMapper()
    assert m.to_index('b') == 0
    assert m.to_index('a') == 1
    assert m.to_index('a') == 1
    assert m.to_index('b') == 0
    assert m.to_index('c') == 2

    assert m.index_to_val() == {0: 'b', 1: 'a', 2: 'c'}
