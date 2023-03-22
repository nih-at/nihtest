This is nihtest, a testing tool for command line utilities.

Tests are run in a sandbox directory to guarantee a clean separation of the test.

It checks that exit code, standard and error outputs are as expected and compares the files in the sandbox after the run with the expected results.

It is written in Python.

It is documented in man pages: [nihtest(1)](https://raw.githack.com/nih-at/nihtest/master/man/nihtest.html), the config
file format [nihtest.conf(5)](https://raw.githack.com/nih-at/nihtest/master/man/nihtest.conf.html) and the test
case language [nihtest-case(5)](https://raw.githack.com/nih-at/nihtest/master/man/nihtest-case.html).

