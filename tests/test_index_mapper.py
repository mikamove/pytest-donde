# coding: utf-8

import pytest

from pytest_donde.index_mapper import IndexMapper

def test_index_mapper():
    m = IndexMapper()
    m.to_index('b') == 0
    m.to_index('a') == 1
    m.to_index('a') == 1
    m.to_index('b') == 0
    m.to_index('c') == 1

    assert m.index_to_val() == {0: 'b', 1: 'a', 2: 'c'}
