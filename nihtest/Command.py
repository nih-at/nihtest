import os
import subprocess


class Command:
    def __init__(self, program, arguments, stdin=[]):
        self.program = program
        self.arguments = arguments
        self.stdin = os.linesep.join(stdin)
        self.stdout = None
        self.stderr = None
        self.exit_code = None

    def run(self):
        # TODO: find self.program in path
        result = subprocess.run([self.program] + self.arguments, capture_output=True, text=True, input=self.stdin)
        self.exit_code = result.returncode
        self.stdout = result.stdout.splitlines()
        self.stderr = result.stderr.splitlines()
