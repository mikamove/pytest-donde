# coding: utf-8
import pytest

from pytest_donde import process_cov_output
from pytest_donde import DondeException
from pytest_donde.outcome import Outcome

@pytest.mark.parametrize('content', [
    '{"a": "b"}'
])
def test_invalid_json(content, tmp_path):
    path = tmp_path / 'dummy.json'
    with open(path, 'w') as fo:
        fo.write(content)
    outcome = Outcome()
    with pytest.raises(DondeException, match='donde.*processing.*json.*node "files" not found'):
        process_cov_output.process_cov_json(path, outcome)
