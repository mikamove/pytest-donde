# coding: utf-8

__version__ = '0.0.30'

class DondeException(Exception):
    def __init__(self, msg):
        super().__init__(f'[donde] {msg}.\nConsider a report at https://github.com/mikamove/pytest-donde/issues')

