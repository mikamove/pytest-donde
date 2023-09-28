# coding: utf-8

__version__ = '1.0.0'

class DondeException(Exception):
    def __init__(self, msg):
        super().__init__(f'[donde] {msg}.\nConsider a report at https://github.com/mikamove/pytest-donde/issues')

