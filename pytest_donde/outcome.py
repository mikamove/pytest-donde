# coding: utf-8

import json

from . import index_mapper

class Outcome:

    def __init__(self):
        self.locs = index_mapper.IndexMapper()
        self.nodeids = index_mapper.IndexMapper()
        self.nindex_to_lindices = {}
        self.nindex_to_duration = {}

    def register_location(self, loc):
        return self.locs.register(loc)

    def register_nodeid(self, nodeid):
        nindex = self.nodeids.register(nodeid, exists_ok=True)
        self.nindex_to_lindices.setdefault(nindex, set())
        return nindex

    def register_coverage(self, nodeid, loc):
        nindex = self.register_nodeid(nodeid)
        lindex = self.locs.to_index(loc)
        self.nindex_to_lindices[nindex].add(lindex)

    def register_duration(self, nodeid, duration):
        nindex = self.nodeids.to_index(nodeid)
        self.nindex_to_duration[nindex] = duration

    def to_file(self, path):
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
        for lindex, loc in sorted(lindex_to_loc.items()):
            result.locs.register(loc)

        nindex_to_nodeid = {int(k): v for k,v in data['nindex_to_nodeid'].items()}
        for nindex, nodeid in sorted(nindex_to_nodeid.items()):
            result.nodeids.register(nodeid)

        for nindex, lindices in data['nindex_to_lindices'].items():
            result.nindex_to_lindices[int(nindex)] = {int(lindex) for lindex in lindices}

        for nindex, duration in data['nindex_to_duration'].items():
            result.nindex_to_duration[int(nindex)] = float(duration)

        return result

    def nodeid_to_duration(self, nodeid):
        nindex = self.nodeids.to_index(nodeid)
        return self.nindex_to_duration[nindex]

    def discard_nodeid(self, nodeid):
        nindex = self.nodeids.discard(nodeid)
        try:
            self.nindex_to_duration.pop(nindex)
        except KeyError:
            pass
        try:
            self.nindex_to_lindices.pop(nindex)
        except KeyError:
            pass

    def iter_nodeids(self):
        for nodeid in sorted(self.nodeids.val_to_index):
            yield nodeid
