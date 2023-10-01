# -*- coding: utf-8 -*-

import pytest
import _pytest

from .record import Record
from .process_cov_output import process_cov_json

def pytest_addoption(parser):
    group = parser.getgroup('donde')
    group.addoption(
        '--donde',
        action='store',
        dest='donde_source',
        metavar='PATH',
        default=None,
        help='write record of coverage-and-time analysis for the source code directory PATH',
    )
    group.addoption(
        '--donde-to',
        action='store',
        metavar='FILE',
        dest='donde_output_path',
        default='donde.json',
        help='specify alternative target path for record file',
    )

# FIXME this solution to control pytest_cov strongly relies on their implementation details
# - because pytest_cov uses the same hook without hookwrapper,
#   we are guaranteed to come first
# - we modify the config parameters, hence strongly rely on their interface
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_load_initial_conftests(early_config):
    if early_config.known_args_namespace.donde_source is not None:
        path = DondeRecordPlugin._path_coveragerc
        DondeRecordPlugin.create_temp_coveragerc(path)
        _reconfigure_cov_parameters(early_config.known_args_namespace, path)

    yield

def pytest_configure(config):
    if config.getoption('donde_source') is not None:
        config.pluginmanager.register(DondeRecordPlugin())

def _reconfigure_cov_parameters(options, path_covrc):
    options.no_cov = False
    options.cov_source = [options.donde_source]
    options.cov_report = {
        'json': None
    }

    vars(options)['cov_config'] = path_covrc
    options.no_cov_on_fail = False
    options.cov_append = False
    options.cov_branch = None
    options.cov_fail_under = None
    options.cov_context = 'test'

class DondeRecordPlugin:

    _item_duration_stash_key = _pytest.stash.StashKey[float]()

    _path_coveragerc = '.donde_coveragerc'
    _path_cov_json = 'coverage.json'

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, call, item):
        yield
        if call.when == 'call':
            item.stash[self._item_duration_stash_key] = call.duration

    def pytest_sessionfinish(self, session):
        record = process_cov_json(self._path_cov_json)

        for item in session.items:
            marker = item.get_closest_marker('skip')
            if marker and marker.name == 'skip':
                # FIXME not covered
                record.discard_nodeid(item.nodeid)
                continue

            duration = item.stash[self._item_duration_stash_key]
            record.register_duration(item.nodeid, duration)

        record.to_file(session.config.getoption('donde_output_path'))

    def pytest_terminal_summary(self, terminalreporter):
        path = terminalreporter.config.known_args_namespace.donde_output_path
        terminalreporter.write(f'--------------------- donde ---------------------\n')
        terminalreporter.write(f'donde record written to {path}')

    coveragerc_content = '''[json]
show_contexts = True
'''

    @classmethod
    def create_temp_coveragerc(cls, path):
        with open(path, 'w') as fo:
            fo.write(cls.coveragerc_content)
