import os

# A class that is responsible for configuring the server when running the build.
class InDirectory(object):

    def __init__(self, nm, create=False):
        self.dir = nm
        self.old = None
        if create and not os.path.exists(self.dir):
            os.makedirs(self.dir)


    def __enter__(self):
        self.old = os.getcwd()
        if os.path.exists(self.dir):
            os.chdir(self.dir)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.old:
            os.chdir(self.old)

