cmake_minimum_required(VERSION 3.12)

project(nihtest
        VERSION 0.1.0
        DESCRIPTION "NiH testing framework"
        HOMEPAGE_URL "https://github.com/nih-at/nihtest"
        LANGUAGES C)

set(TEST_PROGRAMS
  false
  true
  echo
  cat
  getenv
  file
)

foreach(PROGRAM ${TEST_PROGRAMS})
  add_executable(nihtest-${PROGRAM} ${PROGRAM}.c)
endforeach()

ADD_LIBRARY(ineffective-remove MODULE ineffective-remove.c)
TARGET_LINK_LIBRARIES(ineffective-remove ${CMAKE_DL_LIBS})

# Tests for helper programs
add_test(NAME true COMMAND true)
add_test(NAME false COMMAND false)
set_tests_properties(false PROPERTIES WILL_FAIL TRUE)
add_test(NAME echo COMMAND echo "This test was successful.")
set_tests_properties(echo PROPERTIES PASS_REGULAR_EXPRESSION "This test was successful.")
add_test(NAME cat COMMAND cat ${CMAKE_CURRENT_SOURCE_DIR}/success.txt)
set_tests_properties(cat PROPERTIES PASS_REGULAR_EXPRESSION "This is a successful test.")
add_test(NAME getenv-defined COMMAND getenv "DEFINED")
set_tests_properties(getenv-defined PROPERTIES ENVIRONMENT DEFINED="This is a successful test.")
set_tests_properties(getenv-defined PROPERTIES PASS_REGULAR_EXPRESSION "DEFINED=\"This is a successful test.\"")
add_test(NAME getenv-undefined COMMAND getenv "UNDEFINED")
set_tests_properties(getenv-undefined PROPERTIES PASS_REGULAR_EXPRESSION "UNDEFINED=<null>")

# these are not sorted alphabetically but by features
set(NIHTEST_TESTS
  false-fail
  false-pass
  true-fail
  true-pass
  description-pass
  stdout-fail
  stdout-pass
  stderr-fail
  stderr-pass
  stderr-replace-pass
  features-fail
  features-pass
  features-skip
  stdin-pass
  stdin-file-pass
  precheck-fail
  precheck-pass
  precheck-skip
  setenv-pass
  file-del-fail
  file-del-pass
  file-new-fail
  file-new-pass
  file-fail
  file-pass
  file-subdirectory-pass
  preload-pass
  parameter-tests-1
  parameter-tests-2
  parameter-tests-3
  parameter-tests-4
  diff-1
  diff-2
  )

# Tests for nihtest itself
foreach(CASE ${NIHTEST_TESTS})
  add_test(NAME ${CASE} COMMAND python -m nihtest ${PROJECT_SOURCE_DIR}/${CASE})
  set_tests_properties(${CASE} PROPERTIES ENVIRONMENT "PYTHONPATH=${PROJECT_SOURCE_DIR}/..")
  set_tests_properties(${CASE} PROPERTIES SKIP_RETURN_CODE 77)
  if(${CASE} MATCHES ".*-fail$") 
    set_tests_properties(${CASE} PROPERTIES WILL_FAIL TRUE)
  endif()
endforeach()

# for testing the "features" keyword
set(HAVE_TEST_EXISTING_FEATURE 1)
set(HAVE_TEST_MISSING_FEATURE 0)

configure_file(nihtest.conf.in ${CMAKE_CURRENT_BINARY_DIR}/nihtest.conf @ONLY)
configure_file(nihtest-conf.in ${CMAKE_CURRENT_BINARY_DIR}/nihtest-conf @ONLY)

enable_testing()