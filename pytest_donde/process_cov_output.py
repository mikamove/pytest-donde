# coding: utf-8

import json
from .record import Record, _get_node
from . import DondeException

def process_cov_json(path_cov_json):
    with open(path_cov_json, 'r') as fi:
        cov_data = json.load(fi)

    try:
        return _process_cov_json(cov_data)
    except Exception as exc:
        raise DondeException(f'processing {path_cov_json}: {exc}') from exc

def _process_cov_json(cov_data):

    record = Record()

    json_files = _get_node(cov_data, 'files')

    for fname, fname_data in sorted(json_files.items()):

        json_contexts = _get_node(fname_data, 'contexts')

        for line_no_str, contexts in sorted(json_contexts.items()):
            loc = (fname, int(line_no_str))
            for context in contexts:
                if not context.endswith('|run'):
                    continue
                nodeid = context[:-4]
                record.register_coverage(nodeid, loc)
    return record
