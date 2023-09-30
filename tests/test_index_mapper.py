# coding: utf-8

import pytest

from pytest_donde.index_mapper import IndexMapper

def test_index_mapper():
    m = IndexMapper()
    m.register('b') == 0
    m.register('a') == 1
    m.register('a') == 1
    m.register('b') == 0
    m.register('c') == 1

    assert m.index_to_val() == {0: 'b', 1: 'a', 2: 'c'}
