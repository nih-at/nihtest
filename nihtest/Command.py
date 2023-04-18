import os
import shutil
import subprocess


class Command:
    def __init__(self, program, arguments, stdin=None, environment=None):
        self.program = program
        self.arguments = arguments
        self.environment = environment
        if stdin is None:
            stdin = []
        self.stdin = os.linesep.join(stdin)
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
        result = subprocess.run([program] + self.arguments, capture_output=True, check=False, text=True, input=self.stdin, env=environment)
        self.exit_code = result.returncode
        self.stdout = result.stdout.splitlines()
        self.stderr = result.stderr.splitlines()
