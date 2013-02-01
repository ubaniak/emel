class Downloaders
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def download(self):
        raise NotImplementedError("Class " + self.__class__.__name__ +
            " has not implemented method download.")
