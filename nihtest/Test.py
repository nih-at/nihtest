import enum
import os
import platform
import re

from nihtest import Command
from nihtest import Configuration
from nihtest import Features
from nihtest import TestCase
from nihtest import Sandbox
from nihtest import Utility


def process_stderr_line(line, replacements):
    for replacement in replacements:
        line = re.sub(replacement[0], replacement[1], line)
    return line


class TestResult(enum.Enum):
    OK = 0
    FAILED = 1
    SKIPPED = 77


class Test:
    def __init__(self, configuration, args):
        self.case = TestCase.TestCase(configuration, args)
        self.sandbox = None
        self.features = Features.Features(configuration)
        self.failed = []

    def run(self):
        if self.case.preload and platform.system() in ["Darwin", "Windows"]:
            # TODO: status output if verbose
            return TestResult.SKIPPED

        for feature in self.case.features:
            if not self.features.has_feature(feature):
                # TODO: status output if verbose
                return TestResult.SKIPPED

        if not self.precheck_passed():
            # TODO: status output if verbose
            return TestResult.SKIPPED

        self.sandbox = Sandbox.Sandbox(self.case.name, self.case.configuration.keep_sandbox == Configuration.When.NEVER)

        for directory in self.case.directories:
            os.mkdir(os.path.join(self.sandbox.directory, directory))

        for file in self.case.files:
            file.prepare(self.case.configuration, self.sandbox.directory)

        if not self.case.configuration.run_test:
            return TestResult.OK

        self.sandbox.enter()
        program = self.case.configuration.find_program(self.case.program)
        environment = {
            "TZ": "UTC",
            "LANG": "C",
            "LC_CTYPE": "C",
            "POSIXLY_CORRECT": "1"
        }
        environment.update(self.case.environment)
        if self.case.preload:
            environment["LD_PRELOAD"] = " ".join(map(lambda file: self.case.configuration.find_program("lib" + file), self.case.preload))
        command = Command.Command(program, self.case.arguments, self.case.stdin, environment=environment)
        command.run()
        files_got = self.list_files()
        self.sandbox.leave()

        self.compare("exit code", [str(self.case.exit_code)], [str(command.exit_code)])
        self.compare("output", self.case.stdout, command.stdout)
        self.compare("error output", self.case.stderr, self.process_stderr(command.stderr))

        files_expected = []
        for file in self.case.files:
            if file.result:
                files_expected.append(file.name)

        self.compare("file list", sorted(files_expected), sorted(files_got))

        file_content_ok = True
        for file in self.case.files:
            if file.name in files_got and not file.compare(self.case.configuration, self.sandbox.directory):
                file_content_ok = False
        if not file_content_ok:
            self.failed.append("file contents")

        if self.case.configuration.keep_sandbox == Configuration.When.NEVER or (
                self.case.configuration.keep_sandbox == Configuration.When.FAILED and not self.failed):
            self.sandbox.cleanup()

        if self.failed:
            if self.case.configuration.verbose != Configuration.When.NEVER:
                print(self.case.name + " -- FAIL: " + ", ".join(self.failed))
                return TestResult.FAILED
        else:
            return TestResult.OK

    def compare(self, description, expected, got):
        if not Utility.compare_lines(description, expected, got,
                                     self.case.configuration.verbose != Configuration.When.NEVER):
            self.failed.append(description)

    def list_files(self):
        files = []
        for directory, _, sub_files in os.walk("."):
            for file in sub_files:
                if directory == ".":
                    name = file
                else:
                    name = os.path.join(directory, file)[2:]
                files.append(name)
        return files

    def precheck_passed(self):
        if not self.case.precheck:
            return True
        program = self.case.configuration.find_program(self.case.precheck[0])
        command = Command.Command(program, self.case.precheck[1:])
        command.run()
        return command.exit_code == 0

    def process_stderr(self, lines):
        return list(map(lambda line: process_stderr_line(line, self.case.stderr_replace), lines))
