import enum
import os
import pathlib
import platform
import re
import stat
import subprocess
import sys

from nihtest import Command
from nihtest import Configuration
from nihtest import Environment
from nihtest import Features
from nihtest import Output
from nihtest import TestCase
from nihtest import Sandbox
from nihtest import Utility


def process_output_line(line, replacements):
    for replacement in replacements:
        line = re.sub(replacement[0], replacement[1], line)
    return line


class TestResult(enum.Enum):
    OK = 0
    FAILED = 1
    ERROR = 2 # TODO: correct value
    SKIPPED = 77
    EXCEPTION = 99

    EXPECTED_FAIL = 100
    UNEXPECTED_OK = 101


class Test:
    def __init__(self, configuration, args, file_name, name=None):
        self.case = TestCase.TestCase(configuration, args, file_name, name)
        self.sandbox = None
        self.features = Features.Features(configuration)
        self.failed = []
        self.ok = True

    def error(self, message):
        print(f"{message}", file=sys.stderr)
        self.ok = False

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

        for directory in self.case.directories.values():
            directory.prepare(self.sandbox.directory)

        for file in self.case.files.values():
            file.prepare(self.case.configuration, self.sandbox.directory)

        for file, modification_time in self.case.modification_times.items():
            try:
                os.utime(os.path.join(self.sandbox.directory, file), (modification_time, modification_time))
            except Exception as e:
                self.error(f"can't set modification time for '{file}': {e}")

        if not self.ok:
            return TestResult.ERROR

        if not self.case.configuration.run_test:
            if self.case.configuration.verbose == Configuration.When.ALWAYS:
                print(self.case.program + " " + " ".join(self.case.arguments))
            return TestResult.OK

        for file in self.case.read_only:
            full_file = os.path.join(self.sandbox.directory, file)
            st = os.stat(full_file)
            os.chmod(full_file, st.st_mode & ~stat.S_IWUSR)

        self.sandbox.enter()
        executable = self.case.configuration.find_program(self.case.program, in_sandbox=True)
        environment = Environment.Environment(self.case, in_sandbox=True).environment
        if self.case.preload:
            environment["LD_PRELOAD"] = " ".join(map(lambda file: self.case.configuration.find_program("lib" + file, in_sandbox=True), self.case.preload))
        if self.case.configuration.debugger is None:
            command = Command.Command(self.case.program, self.case.arguments, self.case.stdin, environment=environment, executable=executable)
        if self.case.working_directory is not None:
            if not os.path.exists(self.case.working_directory):
                os.mkdir(self.case.working_directory)
            os.chdir(self.case.working_directory)
        if self.case.configuration.debugger is not None:
            subprocess.run([self.case.configuration.debugger, self.case.configuration.debugger_separator, executable] + self.case.arguments, check=False, text=True, encoding="utf-8", env=environment)
        else:
            command.run()
        self.sandbox.chdir_top()
        directories_got, files_got = self.list_files()
        self.sandbox.leave()

        for file in self.case.read_only:
            full_file = os.path.join(self.sandbox.directory, file)
            if os.path.exists(full_file):
                st = os.stat(full_file)
                os.chmod(full_file, st.st_mode | stat.S_IWRITE)

        if self.case.configuration.debugger is not None:
            if self.case.configuration.keep_sandbox == Configuration.When.ALWAYS:
                self.sandbox.cleanup()
            sys.exit(0)

        output = Output.Output(self.case.test_case_source + ":1: test case failed", self.case.configuration.verbose != Configuration.When.NEVER)

        self.compare(output, "exit code", [str(self.case.exit_code)], [str(command.exit_code)])
        self.compare(output,"output", self.case.stdout, self.process_output_replace(command.stdout, self.case.stdout_replace))
        self.compare(output, "error output", self.case.stderr, self.process_output_replace(command.stderr, self.case.stderr_replace))

        directories_expected = {}
        files_expected = []
        for directory in self.case.directories.values():
            if directory.result:
                directories_expected[directory.name] = True

        for file in self.case.files.values():
            if file.result:
                name = file.file_name(self.sandbox.directory)
                files_expected.append(name)
                directory_name = ""
                for directory in pathlib.Path(name).parts[:-1]:
                    if not directory_name:
                        directory_name = directory
                    else:
                        directory_name += "/" +  directory
                    directories_expected[directory_name] = True

        self.compare(output, "directory list", sorted(directories_expected.keys()), sorted(directories_got))
        self.compare(output, "file list", sorted(files_expected), sorted(files_got))

        file_content_ok = True
        for file in self.case.files.values():
            if file.name in files_got and not file.compare(output, self.case.configuration, self.sandbox.directory):
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

    def compare(self, output, description, expected, got):
        if not Utility.compare_lines(output, description, expected, got):
            self.failed.append(description)

    def list_files(self):
        skip_directories = []
        files = []
        directories = []
        for directory, sub_directories, sub_files in os.walk("."):
            directory = directory.replace("\\", "/")
            skip = False
            for skip_directory in skip_directories:
                if directory == skip_directory or directory.startswith(skip_directory + "/"):
                    skip = True
                    break
            if skip:
                continue

            for dir in sub_directories:
                if directory == ".":
                    name = dir
                else:
                    name = os.path.join(directory, dir)[2:].replace("\\", "/")
                if name in self.case.files:
                    files.append(name)
                    skip_directories.append("./" + name)
                else:
                    directories.append(name)

            for file in sub_files:
                if directory == ".":
                    name = file
                else:
                    name = os.path.join(directory, file)[2:].replace("\\", "/")
                files.append(name)

        return directories, files

    def precheck_passed(self):
        if not self.case.precheck:
            return True
        program = self.case.configuration.find_program(self.case.precheck[0])
        command = Command.Command(program, self.case.precheck[1:])
        command.run()
        return command.exit_code == 0

    def process_output_replace(self, lines, replacements):
        return list(map(lambda line: process_output_line(line, replacements), lines))
