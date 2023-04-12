import difflib
import os
import sys


def compare_lines(description, expected, got, verbose):
    raw_diff = list(difflib.Differ().compare(expected, got))
    diff = []
    ok = True
    for raw_line in raw_diff:
        if raw_line[0] == "?":
            continue
        if raw_line[0] != " ":
            ok = False
        diff.append(raw_line[0] + raw_line[2:])
    if not ok and verbose:
        print(f"{description} differs:")
        write_lines(sys.stdout, diff)
    return ok


def read_lines(file_name):
    lines = []
    with open(file_name, "r") as file:
        lines.append(file.readline())
        # TODO: strip newlines
    return lines


def write_lines(file, lines):
    for line in lines:
        file.writelines(line + os.linesep)
