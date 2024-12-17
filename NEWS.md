# 1.9.0 [2024-12-17]

- Fail for unexpeced empty directories.
- Allow specifying existance of directories.
- Check for duplicate file/directory specifications in test case.
- Deprecate `mkdir` directive, use `directory` instead.

# 1.8.0 [2024-06-07]

- Prefer custom path to system path.

# 1.7.0 [2024-04-19]

- Add `test-case-source` directory for better support of script generated test cases.

# 1.6.0 [2024-04-10]

- Print command line for `--verbose --setup-only`.
- Add `stdout-replace` directive.
- Better integration with IDEs.

# 1.5.2 [2024-03-20]

- Fix @SANDBOX@ substitution in file names on Windows.

# 1.5.1 [2024-03-15]

- Fix preload test with newer glibc.

# 1.5.0 [2024-01-17]

- Allow copiers/comparators to handle directories. 

# 1.4.0 [2024-01-03]

- Add copiers.
- Add `working-directory` directive.
- Add `read-only` directive.

# 1.3.0 [2023-12-22]

- Add `set-modification-time` directive.
- Fix inline stdin data.
- Improve error handling.
- Require python 3.9.

# 1.2.0 [2023-07-19]

- Explicitly specify encoding for stdout of subcommands.

# 1.1.1 [2023-06-27]

- Fix Windows compatibility. 

# 1.1.0 [2023-06-15] 

- Improve environment variable handling.
- Reject config file with unknown sections or directives.

# 1.0.0 [2023-06-09]

- Initial public release of Python version of nihtest.
