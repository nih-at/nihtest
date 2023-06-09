import os
import shutil
import subprocess


class Command:
    def __init__(self, program, arguments, stdin=None, environment=None):
        self.program = program
        self.arguments = arguments
        self.environment = environment
        self.stdin = None
        self.stdin_file = None
        if stdin is None:
            stdin = []
        if isinstance(stdin, str):
            self.stdin_file = stdin
        else:
            self.stdin = os.linesep.join(stdin) + os.linesep
        self.stdout = None
        self.stderr = None
        self.exit_code = None

    def run(self):
        program = self.program if os.path.exists(self.program) else shutil.which(self.program)
        if program is None:
            raise RuntimeError(f"can't find program {self.program}")
        if self.environment:
            environment = os.environ | self.environment
        else:
            environment = None
        if self.stdin_file is not None:
            with open(self.stdin_file, "rb") as stdin:
                result = subprocess.run([program] + self.arguments, capture_output=True, check=False, text=True, stdin=stdin, env=environment)
        else:
            result = subprocess.run([program] + self.arguments, capture_output=True, check=False, text=True, input=self.stdin, env=environment)
        self.exit_code = result.returncode
        self.stdout = result.stdout.splitlines()
        self.stderr = result.stderr.splitlines()
