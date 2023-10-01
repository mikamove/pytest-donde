# coding: utf-8

import pytest

from src import f

@pytest.mark.parametrize('a,b,c,z', [
    pytest.param(1,1,1,-2, marks=pytest.mark.skip),
    (1,0,0,14),
    pytest.param(1,0,1,0, marks=pytest.mark.skip),
    pytest.param(1,1,0,16, marks=pytest.mark.skip),
    (0,0,1,0),
    pytest.param(0,1,0,10, marks=pytest.mark.skip),
    pytest.param(0,1,1,-8, marks=pytest.mark.skip),
    (0,0,0,2),
])
def test_f(a,b,c,z):
    assert f(a,b,c) == z
