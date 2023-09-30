# coding: utf-8

import json
from .outcome import Outcome
from . import DondeException

def process_cov_json(path_cov_json):
    with open(path_cov_json, 'r') as fi:
        cov_data = json.load(fi)

    outcome = Outcome()

    try:
        _process_cov_json(cov_data, outcome)
    except Exception as exc:
        raise DondeException(f'processing {path_cov_json}: {exc}') from exc

    return outcome

def _process_cov_json(cov_data, outcome):

    node_files = _get_node(cov_data, 'files')

    for fname, fname_data in sorted(node_files.items()):

        node_contexts = _get_node(fname_data, 'contexts')

        for line_no_str, contexts in sorted(node_contexts.items()):
            loc = (fname, int(line_no_str))
            for context in contexts:
                if not context.endswith('|run'):
                    continue
                nodeid = context[:-4]
                outcome.register_coverage(nodeid, loc)

def _get_node(dct, key):
    try:
        return dct[key]
    except KeyError as exc:
        raise Exception(f'node "{key}" not found') from exc
