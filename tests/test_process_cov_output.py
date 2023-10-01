# coding: utf-8
import pytest

from pytest_donde.process_cov_output import process_cov_json
from pytest_donde import DondeException

@pytest.mark.parametrize('content', [
    '{"a": "b"}'
])
def test_invalid_json(content, tmp_path):
    path = tmp_path / 'dummy.json'
    with open(path, 'w') as fo:
        fo.write(content)

    with pytest.raises(DondeException, match='donde.*processing.*json.*node "files" not found'):
        process_cov_json(path)
