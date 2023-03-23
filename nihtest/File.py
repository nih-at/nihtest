class Data:
    def __init__(self, file_name=None, data=None):
        if file_name is not None and data is not None:
            raise RuntimeError("only one of file_name or data can be specified")
        self.file_name = file_name
        self.data = data


class File:
    def __init__(self, name, input=None, result=None):
        self.name = name
        self.input = input
        self.result = result
