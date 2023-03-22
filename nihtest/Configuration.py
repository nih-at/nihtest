import configparser
import enum


def get_value(config, key, default_value=None):
    if key in config:
        return config[key]
    else:
        return default_value


def get_when(config, key, default_value):
    if name := get_value(config, key):
        if name == "always":
            return When.ALWAYS
        elif name == "failed":
            return When.FAILED
        elif name == "never":
            return When.NEVER
        else:
            raise RuntimeError(f"unknown value '{name}")
    else:
        return default_value


class When(enum.Enum):
    ALWAYS = enum.auto()
    FAILED = enum.auto()
    NEVER = enum.auto()


class Configuration:
    def __init__(self, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        self.default_program = get_value(config, "settings.default-program")
        self.sandbox_directory = get_value(config, "settings.sandbox-directory", ".")
        self.top_build_directory = get_value(config, "settings.top-build-directory")
        if source_directories := get_value(config, "settings.source-directories"):
            self.source_directories = source_directories.split("\n")
        else:
            self.source_directories = []
        self.keep_sandbox = get_when(config, "settings.keep-sandbox", When.NEVER)
        self.print_results = get_when(config, "settings.print-results", When.FAILED)
        self.comparators = config["comparators"]
