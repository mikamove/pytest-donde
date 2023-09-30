# coding: utf-8

import json

from .index_mapper import IndexMapper
from . import __version__

class Outcome:

    def __init__(self):
        # terminology:
        # lindex := index of a loc
        # loc := location := (file, line_no)
        self._locs = IndexMapper()
        self.nodeid_to_lindices = {}
        self.nodeid_to_duration = {}

    # we can detect if a user forgot to register duration,
    # but not if they forgot to register coverage,
    # because a test could just simply cover zero lines.
    # hence, we act asymmetrically:
    # - for durations we default to `None` and later require float for completeness.
    # - for coverage we default to `set()` and do no validation

    def _register_nodeid(self, nodeid):
        self.nodeid_to_lindices.setdefault(nodeid, set())
        self.nodeid_to_duration.setdefault(nodeid, None)

    def register_coverage(self, nodeid, loc):
        self._register_nodeid(nodeid)
        lindex = self._locs.register(loc)
        self.nodeid_to_lindices[nodeid].add(lindex)

    def register_duration(self, nodeid, duration):
        self._register_nodeid(nodeid)
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

    def to_file(self, path):
        self.assert_completeness()

        data = {
            'donde_version': __version__,
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
