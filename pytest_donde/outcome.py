# coding: utf-8

import json

from . import index_mapper

class Outcome:

    def __init__(self):
        # terminology:
        # nindex := index of a nodeid
        # lindex := index of a loc
        # loc := location := (file, line_no)
        self.locs = index_mapper.IndexMapper()
        self.nodeids = index_mapper.IndexMapper()
        self.nindex_to_lindices = {}
        self.nindex_to_duration = {}

    # we can detect if a user forgot to register duration,
    # but not if they forgot to set coverage,
    # because a test could just visit no lines.
    # hence, the interface is asymmetric in this aspect.
    # for durations we default to `None` and later we validate for float.
    # for coverage we default to `set()` and do no validation

    def _register_nodeid(self, nodeid):
        nindex = self.nodeids.register(nodeid)
        self.nindex_to_lindices.setdefault(nindex, set())
        self.nindex_to_duration.setdefault(nindex, None)
        return nindex

    def _register_loc(self, loc):
        lindex = self.locs.register(loc)
        return lindex

    def register_coverage(self, nodeid, loc):
        nindex = self._register_nodeid(nodeid)
        lindex = self._register_loc(loc)
        self.nindex_to_lindices[nindex].add(lindex)

    def register_duration(self, nodeid, duration):
        nindex = self.nodeids.register(nodeid)
        # FIXME should we warn on repeated attempts to set this value?
        self.nindex_to_duration[nindex] = duration

    def assert_completeness(self):
        # there can be tests, for which no location exists,
        # because: they just visit no loc of the considered code base
        #
        # there can be locations, for which no tests exists,
        # because: tests could have been removed via discard_nodeid
        #
        # there cannot be tests, for which no duration exists
        for nindex, duration in self.nindex_to_duration.items():
            if duration is None:
                nodeid = self.nodeids.from_index(nindex)
                raise Exception(f'Inconsistent record: Missing duration for node {nodeid}')


    def to_file(self, path):
        self.assert_completeness()

        data = {
            'lindex_to_loc': self.locs.index_to_val,
            'nindex_to_nodeid': self.nodeids.index_to_val,
            'nindex_to_lindices': {k: list(sorted(v)) for k,v in self.nindex_to_lindices.items()},
            'nindex_to_duration': self.nindex_to_duration,
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
            result.locs.register(loc)

        nindex_to_nodeid = {int(k): v for k,v in data['nindex_to_nodeid'].items()}
        for _, nodeid in sorted(nindex_to_nodeid.items()):
            result.nodeids.register(nodeid)

        for nindex, lindices in data['nindex_to_lindices'].items():
            result.nindex_to_lindices[int(nindex)] = set(map(int, lindices))

        for nindex, duration in data['nindex_to_duration'].items():
            result.nindex_to_duration[int(nindex)] = float(duration)

        result.assert_completeness()
        return result

    def nodeid_to_duration(self, nodeid):
        nindex = self.nodeids.to_index(nodeid)
        return self.nindex_to_duration[nindex]

    def discard_nodeid(self, nodeid):
        nindex = self.nodeids.discard(nodeid)

        if nindex in self.nindex_to_duration:
            self.nindex_to_duration.pop(nindex)

        if nindex in self.nindex_to_lindices:
            self.nindex_to_lindices.pop(nindex)

    def iter_nodeids(self):
        for nodeid in sorted(self.nodeids.val_to_index):
            yield nodeid
