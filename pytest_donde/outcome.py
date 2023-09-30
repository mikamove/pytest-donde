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


    _key_donde_version = 'donde_version'
    _key_lindex_to_loc = 'lindex_to_loc'
    _key_nodeid_to_lindices = 'nodeid_to_lindices'
    _key_nodeid_to_duration = 'nodeid_to_duration'

    def to_file(self, path):
        self.assert_completeness()

        data = {
            self._key_donde_version: __version__,
            self._key_lindex_to_loc: self._locs.index_to_val,
            self._key_nodeid_to_lindices: {k: list(sorted(v)) for k,v in self.nodeid_to_lindices.items()},
            self._key_nodeid_to_duration: self.nodeid_to_duration,
        }

        with open(path, 'w') as fo:
            json.dump(data, fo)

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as fi:
            data = json.load(fi)

        result = cls()

        json_lindex_to_loc = data[cls._key_lindex_to_loc]
        lindex_to_loc = {int(k): tuple(v) for k,v in json_lindex_to_loc.items()}

        for _, loc in sorted(lindex_to_loc.items()):
            result._locs.register(loc)

        json_nodeid_to_lindices = data[cls._key_nodeid_to_lindices]
        result.nodeid_to_lindices = {k: set(map(int, v)) for k, v in json_nodeid_to_lindices.items()}

        json_nodeid_to_duration = data[cls._key_nodeid_to_duration]
        result.nodeid_to_duration = {k: float(v) for k, v in json_nodeid_to_duration.items()}

        result.assert_completeness()
        return result

    def discard_nodeid(self, nodeid):
        self.nodeid_to_duration.pop(nodeid, None)
        self.nodeid_to_lindices.pop(nodeid, None)

    def nodeids(self):
        return list(sorted(self.nodeid_to_duration))
