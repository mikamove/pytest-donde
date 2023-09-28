# coding: utf-8

class IndexMapper:

    def __init__(self):
        self.val_to_index = {}
        self.index_to_val = {}
        self.index = 0

    def __contains__(self, val):
        return val in self.val_to_index

    def register(self, val, exists_ok=False):
        if val in self:
            if not exists_ok:
                raise Exception(f'IndexMapper attempt to register an already known value {val}.')
            index = self.to_index(val)
        else:
            self.val_to_index[val] = self.index
            self.index_to_val[self.index] = val
            index = self.index
            self.index += 1
        return index

    def to_index(self, val):
        if val not in self:
            self.register(val)
        return self.val_to_index[val]

    def from_index(self, index):
        return self.index_to_val[index]

    def discard(self, val):
        index = self.val_to_index.pop(val)
        self.index_to_val.pop(index)
        return index
