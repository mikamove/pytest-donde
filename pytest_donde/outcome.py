# coding: utf-8

import json

from .index_mapper import IndexMapper

class Outcome:

    def __init__(self):
        # terminology:
        # lindex := index of a loc
        # loc := location := (file, line_no)
        self._locs = IndexMapper()
        self.nodeid_to_lindices = {}
        self.nodeid_to_duration = {}

    # we can detect if a user forgot to register duration,
    # but not if they forgot to set coverage,
    # because a test could just visit no lines.
    # hence, the interface is asymmetric in this aspect.
    # for durations we default to `None` and later we validate for float.
    # for coverage we default to `set()` and do no validation

    def _register_nodeid(self, nodeid):
        self.nodeid_to_lindices.setdefault(nodeid, set())
        self.nodeid_to_duration.setdefault(nodeid, None)

    def register_coverage(self, nodeid, loc):
        self._register_nodeid(nodeid)
        lindex = self._locs.register(loc)
        self.nodeid_to_lindices[nodeid].add(lindex)

    def register_duration(self, nodeid, duration):
        self._register_nodeid(nodeid)
        # FIXME should we warn on repeated attempts to set this value?
        self.nodeid_to_duration[nodeid] = duration

    def assert_completeness(self):
        # there can be tests, for which no location exists,
        # because: they just visit no loc of the considered code base
        #
        # there can be locations, for which no tests exists,
        # because: tests could have been removed via discard_nodeid
        #
        # there cannot be tests, for which no duration exists
        for nodeid, duration in self.nodeid_to_duration.items():
            if duration is None:
                raise Exception(f'Inconsistent record: Missing duration for node {nodeid}')

    @classmethod
    def _from_file_oldformat(cls, path):
        with open(path, 'r') as fi:
            data = json.load(fi)

        result = cls()

        lindex_to_loc = {int(k): tuple(v) for k,v in data['lindex_to_loc'].items()}
        for _, loc in sorted(lindex_to_loc.items()):
            result._locs.register(loc)

        nindex_to_nodeid = {int(k): v for k,v in data['nindex_to_nodeid'].items()}
        _nodeids = IndexMapper()
        for _, nodeid in sorted(nindex_to_nodeid.items()):
            _nodeids.register(nodeid)

        for nindex_str, lindices in sorted(data['nindex_to_lindices'].items()):
            nodeid = _nodeids.from_index(int(nindex_str))
            result.nodeid_to_lindices[nodeid] = set(map(int, lindices))

        for nindex_str, duration in data['nindex_to_duration'].items():
            nodeid = _nodeids.from_index(int(nindex_str))
            result.nodeid_to_duration[nodeid] = float(duration)

        result.assert_completeness()
        return result

    def to_file(self, path):
        self.assert_completeness()

        data = {
            'lindex_to_loc': self._locs.index_to_val,
            'nodeid_to_lindices': {k: list(sorted(v)) for k,v in self.nodeid_to_lindices.items()},
            'nodeid_to_duration': self.nodeid_to_duration,
        }

        with open(path, 'w') as fo:
            json.dump(data, fo)

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as fi:
            data = json.load(fi)

        result = cls()

        lindex_to_loc = {int(k): tuple(v) for k,v in data['lindex_to_loc'].items()}
        for _, loc in sorted(lindex_to_loc.items()):
            result._locs.register(loc)

        for nodeid, lindices in sorted(data['nodeid_to_lindices'].items()):
            result.nodeid_to_lindices[nodeid] = set(map(int, lindices))

        for nodeid, duration in data['nodeid_to_duration'].items():
            result.nodeid_to_duration[nodeid] = float(duration)

        result.assert_completeness()
        return result

    def discard_nodeid(self, nodeid):
        if nodeid in self.nodeid_to_duration:
            self.nodeid_to_duration.pop(nodeid)

        if nodeid in self.nodeid_to_lindices:
            self.nodeid_to_lindices.pop(nodeid)

    def iter_nodeids(self):
        for nodeid in sorted(self.nodeid_to_duration):
            yield nodeid
