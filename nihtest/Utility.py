import os
import sys

from nihtest import CompareArrays


def compare_lines(description, expected, got, verbose):
    if not verbose:
        return expected == got

    compare = CompareArrays.CompareArrays(expected, got)
    diff = compare.get_diff()
    if diff:
        print(f"{description} differs:")
        write_lines(sys.stdout, diff)
        return False
    return True


def read_lines(file_name):
    lines = []
    with open(file_name, "r") as file:
        while line := file.readline():
            lines.append(line.rstrip("\r\n"))
    return lines


def write_lines(file, lines):
    for line in lines:
        file.writelines(line + os.linesep)
