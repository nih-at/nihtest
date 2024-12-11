import os


class Directory:
    def __init__(self, name, create, result):
        self.name = name
        self.create = create
        self.result = result

    def prepare(self, directory):
        if self.create:
            os.mkdir(os.path.join(directory, self.name))

    def compare(self, directory):
        return os.path.isdir(os.path.join(directory, self.name)) == self.result
