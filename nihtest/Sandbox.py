import os
import shutil
import tempfile


class Sandbox:
    def __init__(self, name, auto_cleanup):
        self.auto_cleanup = auto_cleanup
        self.entered = False
        self.directory = None
        self.parent_directory = os.getcwd()
        basename = os.path.basename(name)
        self.directory = tempfile.mkdtemp(prefix=f"sandbox_{basename}.d", dir=".")

    def __del__(self):
        if self.entered:
            self.leave()
        if self.directory and self.auto_cleanup:
            self.cleanup()

    def cleanup(self):
        if self.entered:
            self.leave()
        if self.directory:
            shutil.rmtree(self.directory)
            self.directory = None

    def enter(self):
        if self.entered:
            raise RuntimeError("already in sandbox")
        if not self.directory:
            raise RuntimeError("sandbox no longer exists")
        os.chdir(self.directory)
        self.entered = True

    def leave(self):
        if not self.entered:
            raise RuntimeError("not in sandbox")
        os.chdir(self.parent_directory)
        self.entered = False

    def chdir_top(self):
        if not self.entered:
            raise RuntimeError("not in sandbox")
        os.chdir(os.path.join(self.parent_directory, self.directory))
