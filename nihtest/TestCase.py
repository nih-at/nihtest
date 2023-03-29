import re
import sys

from nihtest import File


class Directive:
    def __init__(self, usage, method, single_argument=False, minimum_arguments=0, maximum_arguments=None,
                 required=False, only_once=False):
        self.usage = usage
        self.method = method
        self.single_argument = single_argument
        self.minimum_arguments = minimum_arguments
        if maximum_arguments:
            self.maximum_arguments = maximum_arguments
        else:
            self.maximum_arguments = self.minimum_arguments
        self.required = required
        self.only_once = only_once


class TestCase:
    def __init__(self, configuration, args):
        self.name = args.testcase
        if self.name[-5:] == ".test":
            self.name = self.name[:-5]
        self.args = args
        self.configuration = configuration
        file_name = args.testcase
        if file_name[-5:] != ".test":
            file_name += ".test"
        self.file_name = self.configuration.find_input_file(file_name)
        self.file = open(self.file_name, mode="r")
        self.line_number = 0
        self.directives_seen = {}
        self.arguments = []
        self.description = ""
        self.features = []
        self.files = []
        self.program = configuration.default_program
        self.exit_code = 0
        self.stderr = []
        self.stderr_replace = []
        self.stdin = []
        self.stdout = []
        self.ok = True
        self.parse_case()
        if not self.ok:
            raise RuntimeError("invalid test case")

    def readline(self):
        self.line_number += 1
        return self.file.readline().rstrip('\r\n')

    def parse_case(self):
        while line := self.readline():
            if line == "" or line[0] == "#":
                continue
            self.parse_line(line)

        for name, directive in TestCase.directives.items():
            if directive.required and name not in self.directives_seen:
                self.error(f"missing required directive '{name}'")

    def error(self, message):
        print(f"{self.file_name}:{self.line_number}: {message}", file=sys.stderr)
        self.ok = False

    def parse_line(self, line):
        words = line.split()
        name = words[0]
        arguments = words[1::]

        if name not in TestCase.directives:
            self.error(f"unknown directive '{name}'")
            return

        directive = TestCase.directives[name]

        if directive.single_argument:
            directive.method(self, line[len(name):].lstrip())
        else:
            if len(arguments) < directive.minimum_arguments:
                self.error(f"too few arguments for '{name}'")
                return
            if directive.maximum_arguments != -1 and len(arguments) > directive.maximum_arguments:
                self.error(f"too many arguments for '{name}'")
                return
            if directive.only_once and name in self.directives_seen:
                self.error(f"'{name}' only allowed once")
                return

            self.directives_seen[name] = self.line_number

        directive.method(self, arguments)

    def get_inline_data(self):
        data = []
        while line := self.readline():
            if line == "end-of-inline-data":
                return data
            data.append(line)
        self.error("missing end-of-inline-data")
        return data

    def file_data(self, argument):
        if argument == "{}":
            return None
        if argument == "<inline>":
            return self.get_inline_data()
        return File.Data(file_name=argument)

    def directive_arguments(self, arguments):
        #TODO: quoting
        self.arguments = arguments

    def directive_description(self, text):
        self.description = text

    def directive_features(self, arguments):
        self.features = arguments

    def directive_file(self, arguments):
        input_source = self.file_data(arguments[1])
        if len(arguments) > 2:
            result = self.file_data(arguments[2])
        else:
            result = input_source
        self.files.append(File.File(name=arguments[0], input=input_source, result=result))

    def directive_program(self, arguments):
        self.program = arguments[0]

    def directive_return(self, arguments):
        self.exit_code = int(arguments[0])  # TODO: error check?

    def directive_stderr(self, arguments):
        if len(arguments) > 0:
            self.stderr = self.file_data(arguments[0])
        else:
            self.stderr = self.file_data("<inline>")

    def directive_stderr_replace(self, arguments):
        self.stderr_replace.append((re.compile(arguments[0]), arguments[1]))

    def directive_stdin(self, arguments):
        if len(arguments) > 0:
            self.stdin = self.file_data(arguments[0])
        else:
            self.stdin = self.file_data("<inline>")

    def directive_stdout(self, arguments):
        if len(arguments) > 0:
            self.stdout = self.file_data(arguments[0])
        else:
            self.stdout = self.file_data("<inline>")

    directives = {
        "arguments": Directive(method=directive_arguments,
                               usage="[argument ...]",
                               minimum_arguments=0,
                               maximum_arguments=-1),
        "description": Directive(method=directive_description,
                                 usage="text",
                                 single_argument=True),
        "features": Directive(method=directive_features,
                              usage="feature ...",
                              minimum_arguments=1),
        "file": Directive(method=directive_file,
                          usage="test in [out]",
                          minimum_arguments=2, maximum_arguments=3),
        # mkdir
        # preload
        # precheck
        "program": Directive(method=directive_program,
                             usage="name",
                             minimum_arguments=1,
                             only_once=True),
        "return": Directive(method=directive_return,
                            usage="exit-code",
                            minimum_arguments=1,
                            only_once=True),
        # setenv
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
        # touch
        # ulimit
    }
