import configparser
import enum
import os.path


def get_array(config, key):
    if value := get_value(config, key):
        return value.split("\n")
    else:
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
        raise RuntimeError(f"unknown value '{name}")
    return default_value


class When(enum.Enum):
    ALWAYS = enum.auto()
    FAILED = enum.auto()
    NEVER = enum.auto()


class Configuration:
    def __init__(self, args):
        config = configparser.ConfigParser()
        config.read(args.config_file)
        settings = []
        if "settings" in config:
            settings = config["settings"]
        self.default_program = get_value(settings, "default-program")
        self.sandbox_directory = get_value(settings, "sandbox-directory", ".")
        self.feature_files = get_array(settings, "features-files")
        self.test_input_directories = get_array(settings, "test-input-directories")
        self.program_directories = get_array(settings, "program-directories")
        self.keep_sandbox = get_when(settings, "keep-sandbox", When.NEVER)
        self.print_results = get_when(settings, "print-results", When.FAILED)
        self.comparators = get_value(config, "comparators", [])
        self.verbose = When.FAILED
        self.run_test = True

        if args.quiet:
            self.verbose = When.NEVER
        if args.verbose:
            self.verbose = When.ALWAYS
        if args.keep_broken:
            self.keep_sandbox = When.FAILED
        if args.no_cleanup:
            self.keep_sandbox = When.ALWAYS
        if args.setup_only:
            self.run_test = False

    def find_input_file(self, filename):
        if file := self.find_file(filename, self.test_input_directories):
            return file
        raise RuntimeError(f"can't find input file '{filename}'")

    def find_program(self, program):
        if file := self.find_file(program, self.program_directories):
            return file
        # TODO: search in PATH
        return program

    def find_file(self, filename, directories):
        if os.path.exists(filename):
            return filename
        for directory in directories:
            name = os.path.join(directory, filename)
            if os.path.exists(name):
                return name
        return None
