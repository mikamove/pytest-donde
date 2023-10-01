# coding: utf-8

import json

from .index_mapper import IndexMapper
from . import __version__

class Record:

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
        lindex = self._locs.to_index(loc)
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

        for nodeid, duration in self.nodeid_to_duration.items():
            if duration is None:
                raise Exception(f'Inconsistent record: Missing duration for nodeid "{nodeid}"')

        nodeids_with_duration = set(self.nodeid_to_duration)
        nodeids_with_coverage = set(self.nodeid_to_lindices)
        for nodeid in nodeids_with_coverage.difference(nodeids_with_duration):
            raise Exception(f'Inconsistent record: Missing duration for nodeid "{nodeid}"')

        # TODO add quotes to all msgs

        lindex_to_val = self._locs.index_to_val()
        for nodeid, lindices in self.nodeid_to_lindices.items():
            for lindex in lindices.difference(lindex_to_val):
                raise Exception(f'Inconsistent record: Missing definition for location index {lindex} referenced by nodeid "{nodeid}"')

    _key_donde_version = 'donde_version'
    _key_lindex_to_loc = 'lindex_to_loc'
    _key_nodeid_to_lindices = 'nodeid_to_lindices'
    _key_nodeid_to_duration = 'nodeid_to_duration'

    def to_file(self, path):
        self.assert_completeness()

        data = {
            self._key_donde_version: __version__,
            self._key_lindex_to_loc: self._locs.index_to_val(),
            self._key_nodeid_to_lindices: {k: list(sorted(v)) for k,v in self.nodeid_to_lindices.items()},
            self._key_nodeid_to_duration: self.nodeid_to_duration,
        }

        with open(path, 'w') as fo:
            json.dump(data, fo)

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as fi:
            data = json.load(fi)

        record = cls()

        node = _get_node(data, cls._key_lindex_to_loc)
        lindex_to_loc = {int(k): tuple(v) for k,v in node.items()}

        for _, loc in sorted(lindex_to_loc.items()):
            try:
                record._locs.to_index(loc, exist_ok=False)
            except ValueError as exc:
                raise Exception(f'Inconsistent record: Duplicate index definition for location {loc[0]}:{loc[1]}') from exc

        node = _get_node(data, cls._key_nodeid_to_lindices)
        record.nodeid_to_lindices = {k: set(map(int, v)) for k, v in node.items()}

        node = _get_node(data, cls._key_nodeid_to_duration)
        record.nodeid_to_duration = {k: float(v) for k, v in node.items()}

        record.assert_completeness()
        return record

    def discard_nodeid(self, nodeid):
        self.nodeid_to_duration.pop(nodeid, None)
        self.nodeid_to_lindices.pop(nodeid, None)

    def nodeids(self):
        return list(sorted(self.nodeid_to_duration))

    def nodeid_to_locs(self, nodeid):
        lindex_to_val = self._locs.index_to_val()
        return set(lindex_to_val[lindex] for lindex in self.nodeid_to_lindices[nodeid])

def _get_node(dct, key):
    try:
        return dct[key]
    except KeyError as exc:
        raise Exception(f'node "{key}" not found in json file') from exc
