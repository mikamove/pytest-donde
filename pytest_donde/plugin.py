# -*- coding: utf-8 -*-

import pytest
import _pytest

from .outcome import Outcome
from . import process_cov_output

def pytest_addoption(parser):
    group = parser.getgroup('donde')
    group.addoption(
        '--donde',
        action='store',
        dest='donde_source',
        metavar='PATH',
        default=None,
        help='record coverage-and-time analysis for the source code directory PATH',
    )
    group.addoption(
        '--donde-to',
        action='store',
        metavar='FILE',
        dest='donde_output_path',
        default='donde.json',
        help='specify alternative target path for analysis outcome',
    )

# FIXME this solution to control pytest_cov strongly relies on their implementation details
# - because pytest_cov uses the same hook without hookwrapper,
#   we are guaranteed to come first
# - we modify the config parameters, hence strongly rely on their interface
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_load_initial_conftests(early_config):
    if early_config.known_args_namespace.donde_source is not None:
        path_covrc = DondeRecordPlugin.PATH_COVERAGERC
        DondeRecordPlugin.create_temp_coveragerc(path_covrc)
        _reconfigure_cov_parameters(early_config.known_args_namespace, path_covrc)

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

    ITEM_DURATION_STASH_KEY = _pytest.stash.StashKey[float]()

    PATH_COVERAGERC = '.donde_coveragerc'
    PATH_COV_JSON = 'coverage.json'

    @pytest.mark.hookwrapper
    def pytest_runtest_makereport(self, call, item):
        yield
        if call.when == 'call':
            item.stash[self.ITEM_DURATION_STASH_KEY] = call.duration

    def pytest_sessionfinish(self, session):
        result = Outcome()
        process_cov_output.process_cov_json(self.PATH_COV_JSON, result)

        for item in session.items:
            marker = item.get_closest_marker('skip')
            if marker and marker.name == 'skip':
                try:
                    result.discard_nodeid(item.nodeid)
                except KeyError:
                    pass

                continue

            result.register_nodeid(item.nodeid)
            duration = item.stash[self.ITEM_DURATION_STASH_KEY]

            result.register_duration(item.nodeid, duration)

        path = session.config.known_args_namespace.donde_output_path
        result.to_file(path)

    def pytest_terminal_summary(self, terminalreporter):
        path = terminalreporter.config.known_args_namespace.donde_output_path
        terminalreporter.write(f'--------------------- donde ---------------------\n')
        terminalreporter.write(f'donde results written to {path}')

    coveragerc_content = '''[json]
show_contexts = True
'''

    @classmethod
    def create_temp_coveragerc(cls, path):
        with open(path, 'w') as fo:
            fo.write(cls.coveragerc_content)
