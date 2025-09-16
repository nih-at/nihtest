import configparser
import enum
import os.path
import platform
import re
import shlex
import shutil
import sys

config_schema = {
    "comparators": True,
    "copiers": True,
    "comparator-preprocessors": True,
    "environment": True,
    "settings": [
        "default-program",
        "default-stderr-replace",
        "default-working-directory",
        "features-files",
        "keep-sandbox",
        "print-results",
        "program-directories",
        "sandbox-directory",
        "test-input-directories",
        "environment-clear",
        "environment-passthrough",
        "environment-unset"
    ],
    "suite": [
        "expected-failing-tests",
        "tests"
    ]
}


def validate(config, schema, filename):
    ok = True
    for section in config.sections():
        if section in schema:
            if schema[section] is True:
                continue
            else:
                for key in config[section]:
                    if key not in schema[section]:
                        print(f"{filename}: unknown directive '{key}' in section '{section}'", file=sys.stderr)
                        ok = False
        else:
            print(f"{filename}: unknown section '{section}'", file=sys.stderr)
            ok = False
    return ok


def process_stderr_replace(string):
    arguments = shlex.split(string)
    return re.compile(arguments[0]), arguments[1]


def get_section(config, key):
    if key in config:
        section = config[key]
        value = {}
        for subkey in section:
            value[subkey] = section[subkey]
        return value

    return {}


def get_boolean(config, key, default_value):
    if key in config:
        if config[key] == "true":
            return True
        elif config[key] == "false":
            return False
        else:
            raise f"invalid value '{config[key]}' for {key}"
    else:
        return default_value


def get_array(config, key):
    if value := get_value(config, key):
        return value.split("\n")
    return []


def get_value(config, key, default_value=None):
    if key in config:
        return config[key]
    return default_value


def get_when(config, key, default_value):
    if name := get_value(config, key):
        if name == "always":
            return When.ALWAYS
        if name == "failed":
            return When.FAILED
        if name == "never":
            return When.NEVER
        raise RuntimeError(f"unknown value '{name}'")
    return default_value


class When(enum.Enum):
    ALWAYS = enum.auto()
    FAILED = enum.auto()
    NEVER = enum.auto()


class Configuration:
    class Suite:
        def __init__(self, config):
            self.tests = get_array(config, "tests")
            self.expected_failing_tests = get_array(config, "expected-failing-tests")

    def __init__(self, args):
        config = configparser.ConfigParser()
        config.optionxform = str

        config.read(args.config_file)
        if not validate(config, config_schema, args.config_file):
            sys.exit(99)

        settings = {}
        if "settings" in config:
            settings = config["settings"]
        self.default_program = get_value(settings, "default-program")
        self.default_stderr_replace = get_array(settings, "default-stderr-replace")
        self.default_working_directory = get_value(settings, "default-working-directory")
        self.feature_files = get_array(settings, "features-files")
        self.keep_sandbox = get_when(settings, "keep-sandbox", When.NEVER)
        self.print_results = get_when(settings, "print-results", When.FAILED)
        self.program_directories = get_array(settings, "program-directories")
        self.sandbox_directory = get_value(settings, "sandbox-directory", ".")
        self.test_input_directories = get_array(settings, "test-input-directories")
        self.comparator_preprocessors = get_section(config, "comparator-preprocessors")
        self.comparators = get_section(config, "comparators")
        self.copiers = get_section(config, "copiers")
        self.environment = get_section(config, "environment")
        self.environment_clear = get_boolean(settings, "environment-clear", False)
        self.environment_passthrough = get_array(settings, "environment-passthrough")
        self.environment_unset = get_array(settings, "environment-unset")
        self.verbose = When.FAILED
        self.run_test = True
        self.debugger = None
        self.debugger_separator = None

        self.default_stderr_replace = list(map(process_stderr_replace, self.default_stderr_replace))
        for key, value in self.copiers.items():
            self.copiers[key] = shlex.split(value)
        for key, value in self.comparators.items():
            self.comparators[key] = shlex.split(value)
        for key, value in self.comparator_preprocessors.items():
            self.comparator_preprocessors[key] = shlex.split(value)

        if args.quiet:
            self.verbose = When.NEVER
        if args.verbose:
            self.verbose = When.ALWAYS
        if args.keep_broken:
            self.keep_sandbox = When.FAILED
        if args.no_cleanup:
            self.keep_sandbox = When.ALWAYS
        if args.setup_only:
            self.keep_sandbox = When.ALWAYS
            self.run_test = False
        if args.debug:
            for debugger in ["gdb", "lldb"]:
                program =  shutil.which(debugger)
                if program is not None:
                    self.debugger = program
                    if debugger == "lldb":
                        self.debugger_separator = "--"
                    elif debugger == "gdb":
                        self.debugger_separator = "--args"
                    break
            if self.debugger is None:
                print("no debugger found", file=sys.stderr)
                sys.exit(1)

        self.suite = Configuration.Suite(config["suite"] if "suite" in config else {})

    def find_input_file(self, filename):
        if file := self.find_file(filename, self.test_input_directories):
            return file
        raise RuntimeError(f"can't find input file '{filename}'")

    def find_program(self, program):
        if platform.system() == "Windows" and not (program.endswith(".exe") or program.endswith(".com")):
            program += ".exe"
        if file := self.find_file(program, self.program_directories):
            return file
        return program

    def find_file(self, filename, directories):
        if os.path.exists(filename):
            return filename
        for directory in directories:
            name = os.path.join(directory, filename)
            if os.path.exists(name):
                return name
        return None

    def get_program_directories(self):
        return self.program_directories