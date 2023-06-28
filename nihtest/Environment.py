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
            if variable == "PATH" and configuration.get_program_directories():
                additional_path = os.pathsep.join(configuration.get_program_directories())
                if self.environment[variable]:
                    self.environment[variable] += os.pathsep + additional_path
                else:
                    self.environment[variable] = additional_path

        self.environment |= configuration.environment

        for variable in configuration.environment_unset:
            self.environment.pop(variable, None)
