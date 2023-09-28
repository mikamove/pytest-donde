# pytest_donde

`pytest_donde` records per-test-item coverage and duration into a persistent file and offers an API to access this data in your plugins or scripts.

## details

### create persistent record

```shell
python -m pytest --donde=/path/to/src
```

This creates a `donde.json` file with the following information for every test item:
- run duration (sec),
- covered lines of code w.r.t. `/path/to/src`

by wrapping `pytest-cov`, evaluating its output, and putting this together with collected test item durations.

### access record

```python
from pytest_donde import Outcome
outcome = Outcome.from_file('donde.json')
```

A demo example (which is trivial, because it uses only durations, not coverage):

```python

class PluginPreferFastest:

    def __init__(self, path_input):
        self.outcome = Outcome.from_file(path_input)

    def pytest_collection_modifyitems(self, session, config, items):

        def key(item):
            try:
                return self.outcome.nodeid_to_duration(item.nodeid)
            except KeyError:
                # test is unknown to the donde.json record,
                # possibly it was skipped there or was added after the record was made
                # we prefer it to run at the beginning
                return 0.0

        items[:] = sorted(items, key=key)
```

## install

```shell
python -m pip install pytest-donde
```
