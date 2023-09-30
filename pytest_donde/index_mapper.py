# coding: utf-8

class IndexMapper:

    def __init__(self):
        self.val_to_index = {}
        self.index = 0

    def register(self, val):
        if val not in self.val_to_index:
            self.val_to_index[val] = self.index
            self.index += 1

        return self.val_to_index[val]

    def index_to_val(self):
        return {index: val for val, index in self.val_to_index.items()}
