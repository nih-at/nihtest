import os
import pathlib
import shutil

from nihtest import Command
from nihtest import Environment
from nihtest import Configuration
from nihtest import Utility


class Data:
    def __init__(self, file_name, data=None):
        self.file_name = file_name
        self.data = data


class File:
    def __init__(self, name, input=None, result=None):
        self.name = name
        self.input = input
        self.result = result

    def compare(self, configuration, directory):
        if not self.result:
            return True

        input_file_name = os.path.join(directory, self.name)
        output_is_binary = False

        file_extension = pathlib.Path(self.name).suffix[1:]
        output_extension = pathlib.Path(self.result.file_name).suffix[1:]
        key = f"{file_extension}.{output_extension}"

        if self.result.data is None:
            output_file_name = configuration.find_input_file(self.result.file_name)
            if key in configuration.comparators:
                comparator = configuration.comparators[key]
                arguments = comparator[1:] + [input_file_name, output_file_name]
                command = Command.Command(configuration.find_program(comparator[0]), arguments, environment=Environment.Environment(configuration).environment)
                command.run()
                if command.exit_code != 0:
                    print(f"{self.name} differs:")
                    print("\n".join(command.stdout))
                return command.exit_code == 0
            try:
                output_data = Utility.read_lines(output_file_name)
            except UnicodeDecodeError:
                with open(output_file_name, "rb") as file:
                    output_data = file.read()
                output_is_binary = True
        else:
            if key in configuration.comparators:
                comparator = configuration.comparators[key]
                arguments = comparator[1:] + [input_file_name]
                command = Command.Command(configuration.find_program(comparator[0]), arguments, stdin=self.result.data, environment=Environment.Environment(configuration).environment)
                command.run()
                if command.exit_code != 0:
                    if command.stderr:
                        print(f"comparing {self.name} failed:")
                        print("\n".join(command.stderr))
                    else:
                        print(f"{self.name} differs:")
                        print("\n".join(command.stdout))
                return command.exit_code == 0
            output_data = self.result.data

        if key in configuration.comparator_preprocessors:
            preprocessor = configuration.comparator_preprocessors[key]
            arguments = preprocessor[1:] + [input_file_name]
            # TODO: allow binary data
            command = Command.Command(configuration.find_program(preprocessor[0]), arguments, environment=Environment.Environment(configuration).environment)
            command.run()
            return Utility.compare_lines(self.name, output_data, command.stdout, configuration.verbose != Configuration.When.NEVER)

        if not output_is_binary:
            try:
                input_data = Utility.read_lines(input_file_name)
                return Utility.compare_lines(self.name, output_data, input_data, configuration.verbose != Configuration.When.NEVER)
            except UnicodeDecodeError:
                output_data = "\n".join(output_data)

        with open(input_file_name, "rb") as file:
            input_data = file.read()
        if input_data != output_data:
            if configuration.verbose != Configuration.When.NEVER:
                print(f"{self.name} differs:")
                print("Binary files differ.")
            return False
        return True

    def prepare(self, configuration, directory):
        if self.input:
            output_file_name = os.path.join(directory, self.name)
            os.makedirs(os.path.dirname(output_file_name), 0o777, True)
            if self.input.data is None:
                input_file_name = configuration.find_input_file(self.input.file_name)
                shutil.copyfile(input_file_name, output_file_name)
            else:
                with open(output_file_name, "w", encoding='utf-8') as file:
                    Utility.write_lines(file, self.input.data)
