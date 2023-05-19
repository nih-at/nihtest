import os
import pathlib
import shutil

from nihtest import Command
from nihtest import Configuration
from nihtest import Utility


class Data:
    def __init__(self, file_name=None, data=None):
        if (file_name is not None and data is not None) or (file_name is None and data is None):
            raise RuntimeError("exactly one of file_name or data must be specified")
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

        if self.result.file_name:
            output_file_name = configuration.find_input_file(self.result.file_name)
            file_extension = pathlib.Path(self.name).suffix[1:]
            output_extension = pathlib.Path(self.result.file_name).suffix[1:]
            key = f"{file_extension}.{output_extension}"
            if key in configuration.comparators:
                comparator = configuration.comparators[key]
                arguments = comparator[1:] + [input_file_name, output_file_name]
                command = Command.Command(configuration.find_program(comparator[0]), arguments)
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
            output_data = self.result.data

        if not output_is_binary:
            try:
                input_data = Utility.read_lines(input_file_name)
                return Utility.compare_lines(self.name, output_data, input_data, configuration.verbose != Configuration.When.NEVER)
            except UnicodeDecodeError:
                output_data = os.linesep.join(output_data)

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
            # TODO: create sub-directories in sandbox
            if self.input.file_name is not None:
                input_file_name = configuration.find_input_file(self.input.file_name)
                shutil.copyfile(input_file_name, output_file_name)
            else:
                with open(output_file_name, "w") as file:
                    for line in self.input.data:
                        file.write(line + os.linesep)
