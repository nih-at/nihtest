import argparse
import sys

from nihtest import Test
from nihtest import Configuration

VERSION = "1.0.0" # TODO: get from Cmake

def main():
    parser = argparse.ArgumentParser(
        prog='nihtest',
        description="nihtest " + VERSION  + "\nCopyright (C) 2023 Dieter Baron and Thomas Klausner")
    parser.add_argument('testcase', help='Testcase to run')
    parser.add_argument('-C', '--config-file', metavar='FILE', help='use FILE as config file', default="nihtest.conf")
    parser.add_argument('--keep-broken', action='store_true', help='keep sandbox if test fails')
    parser.add_argument('--no-cleanup', action='store_true', help='keep sandbox')
    parser.add_argument('-q', '--quiet', action='store_true', help="don't print test result")
    parser.add_argument('--setup-only', action='store_true', help="set up sandbox, but don't run test")
    parser.add_argument('-v', '--verbose', action='store_true', help="print detailed test results")
    parser.add_argument('-V', '--version', action='store_true', help='display version number and exit')

    args = parser.parse_args()

    if args.version:
        print("nihtest " + VERSION)
        sys.exit(0)

    configuration = Configuration.Configuration(args)

    try:
        test = Test.Test(configuration, args)
        return test.run().value
    except RuntimeError as ex:
        print(f"{sys.argv[0]}: {ex}", file=sys.stderr)
        sys.exit(99)


if __name__ == "__main__":
    sys.exit(main())
