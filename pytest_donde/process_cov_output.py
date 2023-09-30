# coding: utf-8

import json

from . import DondeException

def process_cov_json(path_cov_json, outcome):
    with open(path_cov_json, 'r') as fi:
        cov_data = json.load(fi)

    try:
        return _process_cov_json(cov_data, outcome)
    except Exception as exc:
        raise DondeException(f'processing {path_cov_json}: {exc}') from exc

def _process_cov_json(cov_data, outcome):
    node_files = _get_node(cov_data, 'files')
    for fname, fname_data in sorted(node_files.items()):

        node_executed_lines = _get_node(fname_data, 'executed_lines')

        executed_locs = set()
        for line_no in sorted(node_executed_lines):
            loc = (fname, line_no)
            executed_locs.add(loc)

        node_contexts = _get_node(fname_data, 'contexts')

        registered_locs = set()
        for line_no_str, contexts in sorted(node_contexts.items()):
            loc = (fname, int(line_no_str))
            for context in contexts:
                if not context.endswith('|run'):
                    continue
                nodeid = context[:-4]
                outcome.register_coverage(nodeid, loc)
                registered_locs.add(loc)

        # every registered loc must be filed as an executed loc
        suspicious_locs = registered_locs.difference(executed_locs)
        if suspicious_locs:
            # FIXME test this
            # FIXME better warning
            print('[warn] coverage json seems inconsistent: '
                  f'for {fname} the following lines of code are registered in "contexts", '
                  f'but not attributed in "executed_lines": {suspicious_locs}')

def _get_node(dct, key):
    try:
        return dct[key]
    except KeyError as exc:
        raise Exception(f'node "{key}" not found') from exc
