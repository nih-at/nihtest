class Output:
    def __init__(self, header, verbose):
        self.header = header
        self.header_printed = False
        self.verbose = verbose

    def print(self, message):
        if not self.verbose:
            return
        if not self.header_printed:
            print(self.header)
            self.header_printed = True
        print(message)
