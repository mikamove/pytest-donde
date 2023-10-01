# coding: utf-8

class IndexMapper:

    def __init__(self):
        self._val_to_index = {}
        self._index = 0

    def to_index(self, val, exist_ok=True):
        if val not in self._val_to_index:
            self._val_to_index[val] = self._index
            self._index += 1
        elif not exist_ok:
            raise ValueError(val)

        return self._val_to_index[val]

    def index_to_val(self):
        return {index: val for val, index in self._val_to_index.items()}
