cmake_minimum_required(VERSION 3.12)

# Also update version in nihtest/__main__.py and pyproject.toml
project(nihtest
        VERSION 1.0.0
        DESCRIPTION "NiH testing framework"
        HOMEPAGE_URL "https://github.com/nih-at/nihtest"
        LANGUAGES C)

enable_testing()

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(VENV ${CMAKE_BINARY_DIR}/venv)
if (WIN32)
    set(VENV_BIN_DIR ${VENV}/Scripts)
    set(VENV_PYTHON ${VENV_BIN_DIR}/python.exe)
else ()  # assume Linux
    set(VENV_BIN_DIR ${VENV}/bin)
    set(VENV_PYTHON ${VENV_BIN_DIR}/python)
endif ()

set(NIHTEST ${VENV_BIN_DIR}/nihtest)

file(GLOB SOURCES ${CMAKE_SOURCE_DIR}/nihtest/*.py)

add_custom_command(
        OUTPUT ${NIHTEST}
        COMMAND ${Python3_EXECUTABLE} -m venv ${VENV}
        COMMAND ${VENV_BIN_DIR}/pip install -q --disable-pip-version-check ${CMAKE_SOURCE_DIR}
        DEPENDS ${SOURCES}
)

add_custom_target(venv ALL DEPENDS ${NIHTEST})

# TODO: target for wheel

add_subdirectory(tests)