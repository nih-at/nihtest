cmake_minimum_required(VERSION 3.12)

project(nihtest
        VERSION 0.1.0
        DESCRIPTION "NiH testing framework"
        HOMEPAGE_URL "https://github.com/nih-at/nihtest"
        LANGUAGES C)

set(TEST_PROGRAMS
  can-preload
  comparator
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
add_test(NAME true COMMAND nihtest-true)
add_test(NAME false COMMAND nihtest-false)
set_tests_properties(false PROPERTIES WILL_FAIL TRUE)
add_test(NAME echo COMMAND nihtest-echo "This test was successful.")
set_tests_properties(echo PROPERTIES PASS_REGULAR_EXPRESSION "This test was successful.")
add_test(NAME cat COMMAND nihtest-cat ${CMAKE_CURRENT_SOURCE_DIR}/success.txt)
set_tests_properties(cat PROPERTIES PASS_REGULAR_EXPRESSION "This is a successful test.")
add_test(NAME getenv-defined COMMAND nihtest-getenv "DEFINED")
set_tests_properties(getenv-defined PROPERTIES ENVIRONMENT DEFINED="This is a successful test.")
set_tests_properties(getenv-defined PROPERTIES PASS_REGULAR_EXPRESSION "DEFINED=\"This is a successful test.\"")
add_test(NAME getenv-undefined COMMAND nihtest-getenv "UNDEFINED")
set_tests_properties(getenv-undefined PROPERTIES PASS_REGULAR_EXPRESSION "UNDEFINED=<null>")

file(GLOB TESTS ${CMAKE_CURRENT_SOURCE_DIR}/*.test)
foreach(FULL_CASE IN LISTS TESTS)
  get_filename_component(CASE ${FULL_CASE} NAME)
  add_test(NAME ${CASE} COMMAND ${NIHTEST} ${CASE})
  set_tests_properties(${CASE} PROPERTIES SKIP_RETURN_CODE 77)
  #  set_tests_properties(${CASE} PROPERTIES ENVIRONMENT "PATH=${path}")
endforeach()

# for testing the "features" keyword
set(HAVE_TEST_EXISTING_FEATURE 1)
set(HAVE_TEST_MISSING_FEATURE 0)

configure_file(nihtest.conf.in ${CMAKE_CURRENT_BINARY_DIR}/nihtest.conf @ONLY) # for *.tests
configure_file(nihtest-conf.in ${CMAKE_CURRENT_BINARY_DIR}/nihtest-conf @ONLY) # for *.input

enable_testing()

# TODO: testing depends on venv
