import argparse
import sys

from nihtest import Configuration
from nihtest import Suite
from nihtest import Test

VERSION = "1.10.0"


def main():
    parser = argparse.ArgumentParser(
        prog='nihtest',
        description="nihtest " + VERSION + "\nCopyright (C) 2023 Dieter Baron and Thomas Klausner")
    parser.add_argument('testcase', nargs='*')
    parser.add_argument('--all', action='store_true', help='run all test in suite')
    parser.add_argument('-C', '--config-file', metavar='FILE', help='use FILE as config file', default="nihtest.conf")
    parser.add_argument("--debug", action="store_true", help="run debugger on program in sandbox")
    parser.add_argument('--keep-broken', action='store_true', help='keep sandbox if test fails')
    parser.add_argument('--no-cleanup', action='store_true', help='keep sandbox')
    parser.add_argument('-q', '--quiet', action='store_true', help="don't print test result")
    parser.add_argument('--setup-only', action='store_true', help="set up sandbox, but don't run test")
    parser.add_argument('-v', '--verbose', action='store_true', help="print detailed test results")
    parser.add_argument('-V', '--version', action='version', version='nihtest ' + VERSION)

    args = parser.parse_args()

    configuration = Configuration.Configuration(args)

    is_suite = False

    if args.all:
        is_suite = True
        if len(args.testcase) != 0:
            print(f"{sys.argv[0]}: can't explicitly specify test cases when using --all")
            sys.exit(1)
    else:
        if len(args.testcase) == 0:
            print(f"{sys.argv[0]}: no test cases specified")
            sys.exit(1)
        elif len(args.testcase) == 1:
            if "*" in args.testcase[0] or "?" in args.testcase[0] or "[" in args.testcase[0] or "]" in args.testcase[0]:
                is_suite = True
        else:
            is_suite = True


    try:
        if is_suite:
            suite = Suite.Suite(configuration, args)
            return suite.run().value
        else:
            test = Test.Test(configuration, args, args.testcase[0])
        return test.run().value
    except RuntimeError as ex:
        print(f"{sys.argv[0]}: {ex}", file=sys.stderr)
        sys.exit(99)


if __name__ == "__main__":
    sys.exit(main())
