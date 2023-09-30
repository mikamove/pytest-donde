# coding: utf-8

class IndexMapper:

    def __init__(self):
        self.val_to_index = {}
        self.index_to_val = {}
        self.index = 0

    def __contains__(self, val):
        return val in self.val_to_index

    def register(self, val):
        if val in self:
            return self.to_index(val)

        self.val_to_index[val] = self.index
        self.index_to_val[self.index] = val
        index = self.index
        self.index += 1
        return index

    def to_index(self, val):
        return self.val_to_index[val]

    def from_index(self, index):
        return self.index_to_val[index]

    def discard(self, val):
        index = self.val_to_index.pop(val)
        self.index_to_val.pop(index)
        return index
