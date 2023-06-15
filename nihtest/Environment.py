import os


class Environment:
    def __init__(self, configuration):
        default_passthrough = ["PATH"]
        default_environment = {
            "TZ": "UTC"
        }

        self.environment = {}

        passthrough = configuration.environment_passthrough
        if not configuration.environment_clear:
            self.environment |= default_environment
            passthrough += default_passthrough

        for variable in passthrough:
            self.environment[variable] = os.environ[variable]

        self.environment |= configuration.environment

        for variable in configuration.environment_unset:
            self.environment.pop(variable, None)
