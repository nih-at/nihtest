import os
import shutil
import subprocess


class Command:
    def __init__(self, program, arguments, stdin=None, environment=None, executable=None):
        self.program = program
        self.executable = executable if executable is not None else program
        self.arguments = arguments
        self.environment = environment
        self.stdin = ""
        self.stdin_file = None
        if stdin is None:
            stdin = []
        if isinstance(stdin, str):
            self.stdin_file = stdin
        elif stdin:
            self.stdin = "\n".join(stdin) + "\n"
        self.stdout = None
        self.stderr = None
        self.exit_code = None

    def run(self):
        executable = self.executable if os.path.exists(self.executable) else shutil.which(self.executable)
        if executable is None:
            raise RuntimeError(f"can't find program {self.executable}")
        if self.stdin_file is not None:
            with open(self.stdin_file, "rb") as stdin:
                result = subprocess.run([self.program] + self.arguments, executable=executable, capture_output=True, check=False, text=True, encoding="utf-8", stdin=stdin, env=self.environment)
        else:
            result = subprocess.run([self.program] + self.arguments, executable=executable, capture_output=True, check=False, text=True, encoding="utf-8", input=self.stdin, env=self.environment)
        self.exit_code = result.returncode
        self.stdout = result.stdout.splitlines()
        self.stderr = result.stderr.splitlines()
