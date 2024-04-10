import dateutil.parser
import re
import shlex
import sys

from nihtest import File
from nihtest import Utility


def decode_escapes(string):
    return string.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t").replace("\\\\", "\\")


class Directive:
    def __init__(self, usage, method, minimum_arguments, maximum_arguments=None, only_once=False):
        self.usage = usage
        self.method = method
        self.minimum_arguments = minimum_arguments
        if maximum_arguments:
            self.maximum_arguments = maximum_arguments
        else:
            self.maximum_arguments = self.minimum_arguments
        self.only_once = only_once


class TestCase:
    def __init__(self, configuration, args):
        self.name = args.testcase
        if self.name[-5:] == ".test":
            self.name = self.name[:-5]
        self.args = args
        self.configuration = configuration
        self.environment = configuration.environment.copy()
        self.environment_clear = configuration.environment_clear
        self.environment_passthrough = configuration.environment_passthrough.copy()
        self.environment_unset = configuration.environment_unset.copy()
        file_name = args.testcase
        if file_name[-5:] != ".test":
            file_name += ".test"
        self.file_name = self.configuration.find_input_file(file_name)
        self.file = open(self.file_name, mode="r", encoding='utf-8')
        self.line_number = 0
        self.directives_seen = {}
        self.arguments = []
        self.description = ""
        self.features = []
        self.files = []
        self.precheck = None
        self.preload = []
        self.program = configuration.default_program
        self.exit_code = 0
        self.read_only = []
        self.stderr = []
        self.stderr_replace = []
        self.stdin = []
        self.stdout = []
        self.stdout_replace = []
        self.ok = True
        self.directories = []
        self.modification_times = {}
        self.working_directory = configuration.default_working_directory
        self.parse_case()
        if not self.ok:
            raise RuntimeError("invalid test case")

    def readline(self):
        self.line_number += 1
        line = self.file.readline()
        if line == "":
            return None
        return line.rstrip('\r\n')

    def parse_case(self):
        while (line := self.readline()) is not None:
            if line == "" or line[0] == "#":
                continue
            self.parse_line(line)
        if len(self.stderr_replace) == 0:
            self.stderr_replace = self.configuration.default_stderr_replace

    def error(self, message):
        print(f"{self.file_name}:{self.line_number}: {message}", file=sys.stderr)
        self.ok = False

    def parse_line(self, line):
        try:
            words = list(map(decode_escapes, shlex.split(line)))
            name = words[0]
            arguments = words[1::]
        except Exception as e:
            self.error(f"syntax error: {e}")
            return

        if name not in TestCase.directives:
            self.error(f"unknown directive '{name}'")
            return

        directive = TestCase.directives[name]

        if directive.only_once and name in self.directives_seen:
            self.error(f"'{name}' only allowed once")
            return
        self.directives_seen[name] = self.line_number
        if len(arguments) < directive.minimum_arguments:
            self.error(f"too few arguments for '{name}'")
            return
        if directive.maximum_arguments != -1 and len(arguments) > directive.maximum_arguments:
            self.error(f"too many arguments for '{name}'")
            return
        directive.method(self, arguments)

    def get_inline_data(self):
        data = []
        while (line := self.readline()) is not None:
            if line == "end-of-inline-data":
                return data
            data.append(line)
        self.error("missing end-of-inline-data")
        return data

    def file_data(self, argument):
        if argument == "{}":
            return None
        if len(argument) >= 2 and argument[0] == "<" and argument[-1] == ">":
            inline_file_name = argument[1:-1]
            if inline_file_name == "empty" or inline_file_name.startswith("empty."):
                data = []
            else:
                data = self.get_inline_data()
            return File.Data(file_name=inline_file_name, data=data)
        return File.Data(file_name=argument)

    def io_data(self, arguments):
        if len(arguments) > 0:
            file_name = self.configuration.find_input_file(arguments[0])
            return Utility.read_lines(file_name)
        return self.get_inline_data()

    def directive_arguments(self, arguments):
        self.arguments = arguments

    def directive_description(self, text):
        self.description = text

    def directive_environment_clear(self, _arguments):
        self.environment_clear = True

    def directive_environment_passthrough(self, arguments):
        self.environment_passthrough += arguments

    def directive_environment_set(self, arguments):
        self.environment[arguments[0]] = arguments[1]

    def directive_environment_unset(self, arguments):
        self.environment_unset += arguments

    def directive_features(self, arguments):
        self.features = arguments

    def directive_file(self, arguments):
        input_source = self.file_data(arguments[1])
        if len(arguments) > 2:
            result = self.file_data(arguments[2])
        else:
            result = input_source
        self.files.append(File.File(name=arguments[0], input=input_source, result=result))

    def directive_mkdir(self, arguments):
        self.directories.append(arguments[0])

    def directive_precheck(self, arguments):
        self.precheck = arguments

    def directive_preload(self, arguments):
        self.preload.append(arguments[0])

    def directive_program(self, arguments):
        self.program = arguments[0]

    def directive_read_only(self, arguments):
        self.read_only.append(arguments[0])
    def directive_return(self, arguments):
        self.exit_code = int(arguments[0])  # TODO: error check?

    def directive_set_modification_time(self, arguments):
        if arguments[1].isnumeric():
            timestamp = int(arguments[1])
        else:
            timestamp = dateutil.parser.isoparse(arguments[1]).timestamp()
        self.modification_times[arguments[0]] = timestamp

    def directive_stderr(self, arguments):
        self.stderr = self.io_data(arguments)

    def directive_stderr_replace(self, arguments):
        self.stderr_replace.append((re.compile(arguments[0]), arguments[1]))

    def directive_stdin(self, arguments):
        if len(arguments) > 0:
            self.stdin = self.configuration.find_input_file(arguments[0])
        else:
            self.stdin = self.get_inline_data()

    def directive_stdout(self, arguments):
        self.stdout = self.io_data(arguments)

    def directive_stdout_replace(self, arguments):
        self.stdout_replace.append((re.compile(arguments[0]), arguments[1]))

    def directive_working_directory(self, arguments):
        self.working_directory = arguments[0]

    directives = {
        "arguments": Directive(method=directive_arguments,
                               usage="[argument ...]",
                               minimum_arguments=0, maximum_arguments=-1),
        "description": Directive(method=directive_description,
                                 minimum_arguments=0, maximum_arguments=-1,
                                 usage="text"),
        "environment-clear": Directive(method=directive_environment_clear,
                                       usage="",
                                       minimum_arguments=0),
        "environment-passthrough": Directive(method=directive_environment_passthrough,
                                             usage="variable ...",
                                             minimum_arguments=1, maximum_arguments=-1),
        "environment-set": Directive(method=directive_environment_set,
                                     usage="variable value",
                                     minimum_arguments=2),
        "environment-unset": Directive(method=directive_environment_unset,
                                       usage="variable ...",
                                       minimum_arguments=1, maximum_arguments=-1),
        "features": Directive(method=directive_features,
                              usage="feature ...",
                              minimum_arguments=1),
        "file": Directive(method=directive_file,
                          usage="name in [out]",
                          minimum_arguments=2, maximum_arguments=3),
        "mkdir": Directive(method=directive_mkdir,
                           usage="name",
                           minimum_arguments=1),
        "precheck": Directive(method=directive_precheck,
                              usage="program [argument ...]",
                              minimum_arguments=1, maximum_arguments=-1,
                              only_once=True),
        "preload": Directive(method=directive_preload,
                             usage="object",
                             minimum_arguments=1),
        "program": Directive(method=directive_program,
                             usage="name",
                             minimum_arguments=1,
                             only_once=True),
        "read-only": Directive(method=directive_read_only,
                               usage="name",
                               minimum_arguments=1),
        "return": Directive(method=directive_return,
                            usage="exit-code",
                            minimum_arguments=1,
                            only_once=True),
        "set-modification-time": Directive(method=directive_set_modification_time,
                                           usage="file time",
                                           minimum_arguments=2),
        "stderr": Directive(method=directive_stderr,
                            usage="[file]",
                            minimum_arguments=0, maximum_arguments=1,
                            only_once=True),
        "stderr-replace": Directive(method=directive_stderr_replace,
                                    usage="pattern replacement",
                                    minimum_arguments=2),
        "stdin": Directive(method=directive_stdin,
                           usage="[file]",
                           minimum_arguments=0, maximum_arguments=1,
                           only_once=True),
        "stdout": Directive(method=directive_stdout,
                            usage="[file]",
                            minimum_arguments=0, maximum_arguments=1,
                            only_once=True),
        "stdout-replace": Directive(method=directive_stdout_replace,
                                    usage="pattern replacement",
                                    minimum_arguments=2),
        "working-directory": Directive(method=directive_working_directory,
                                       usage="directory",
                                       minimum_arguments=1,
                                       only_once=True)
    }

    def get_program_directories(self):
        return self.configuration.program_directories
