# coding: utf-8

import pytest

from src import f

@pytest.mark.parametrize('a,b,c,z', [
    (1,1,1,-2),
    (1,0,0,14),
    (1,0,1,0),
    (1,1,0,16),
    (0,0,1,0),
    (0,1,0,10),
    (0,1,1,-8),
    (0,0,0,2),
])
def test_f(a,b,c,z):
    assert f(a,b,c) == z
