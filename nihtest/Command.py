import os
import shutil
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
        program = self.program if os.path.exists(self.program) else shutil.which(self.program)
        if program is None:
            raise RuntimeError(f"can't find program {self.program}")
        result = subprocess.run([program] + self.arguments, capture_output=True, text=True, input=self.stdin)
        self.exit_code = result.returncode
        self.stdout = result.stdout.splitlines()
        self.stderr = result.stderr.splitlines()
