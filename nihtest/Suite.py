import glob
import os

from nihtest import Test

class Suite:
    class Case:
        def __init__(self, name, expect_failing=False):
            self.name = name
            self.expect_failing = expect_failing

    def __init__(self, configuration, args):
        self.configuration = configuration
        self.args = args
        self.tests = {}
        self.stats = {}
        if len(args.testcase) > 0:
            self.add_cases(args.testcase)
            self.add_cases(configuration.suite.expected_failing_tests, expect_failing=True, no_new_cases=True)
        else:
            self.add_cases(configuration.suite.tests)
            self.add_cases(configuration.suite.expected_failing_tests, expect_failing=True)

    def run(self):
        total = len(self.tests)
        current = 0
        failed = 0
        skipped = 0
        current_len = len(f"{total}")
        name_len = 0
        ok = True
        for case in self.tests.values():
            name_len = max(name_len, len(case.name))

        for name in sorted(self.tests.keys()):
            case = self.tests[name]
            try:
                test = Test.Test(self.configuration, self.args, name, case.name)
                result = test.run()
                if case.expect_failing:
                    if result == Test.TestResult.OK:
                        result = Test.TestResult.UNEXPECTED_OK
                    elif result == Test.TestResult.FAILED:
                        result = Test.TestResult.EXPECTED_FAIL

            except RuntimeError as ex:
                # TODO: print {ex} if verbose
                result = Test.TestResult.EXCEPTION

            if result == Test.TestResult.SKIPPED:
                skipped += 1
            elif result != Test.TestResult.OK and result != Test.TestResult.EXPECTED_FAIL:
                ok = False
                failed += 1
            if result not in self.stats:
                self.stats[result] = []
            self.stats[result].append(case.name)
            current += 1
            print(f"Test {current:{current_len}}/{total} {case.name:<{name_len}}  {result.name}")


        percent = int(100 * (total - failed - skipped) / (total - skipped))
        if failed == 1:
            print(f"\n{percent}% tests passed, {failed} test failed out of {total - skipped}")
        else:
            print(f"\n{percent}% tests passed, {failed} tests failed out of {total - skipped}")

        self.print_failures(Test.TestResult.FAILED, "failed")
        self.print_failures(Test.TestResult.UNEXPECTED_OK, "unexpectedly passed")
        self.print_failures(Test.TestResult.SKIPPED, "did not run")

        return Test.TestResult.OK if ok else Test.TestResult.FAILED

    def add_cases(self, names, expect_failing=False, no_new_cases=False):
        for name in names:
            if not name.endswith(".test"):
                name += ".test"

            files = self.find_files(name)
            if len(files) == 0:
                raise RuntimeError(f"no test cases found for '{name}'")

            for (file, test_name) in files:
                if no_new_cases and file not in self.tests:
                    continue
                self.tests[file] = Suite.Case(test_name, expect_failing)

    def find_files(self, name):
        files = []
        if os.path.isabs(name):
            for file in glob.glob(name):
                files.append((file, file[-5:]))
        else:
            for directory in ["."] + self.configuration.test_input_directories:
                for file in glob.glob(name, root_dir=directory):
                    files.append((os.path.join(directory, file), file[:-5]))

        return files

    def print_failures(self, result, description):
        if result not in self.stats or self.stats[result] == []:
            return
        print(f"\nThe following tests {description}:")
        for name in self.stats[result]:
            print(f"  {name}")
