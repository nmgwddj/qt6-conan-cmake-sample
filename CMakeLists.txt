cmake_minimum_required(VERSION 3.18)

project(QtWithConan VERSION 0.1 LANGUAGES CXX)

# Pre-commit hooks
if (NOT EXISTS ${CMAKE_CURRENT_LIST_DIR}/.git/hooks/pre-commit)
    if (POLICY CMP0094)  # https://cmake.org/cmake/help/latest/policy/CMP0094.html
        CMAKE_POLICY(SET CMP0094 NEW)  # FindPython should return the first matching Python
    endif ()
    # needed on GitHub Actions CI: actions/setup-python does not touch registry/frameworks on Windows/macOS
    # this mirrors PythonInterp behavior which did not consult registry/frameworks first
    if (NOT DEFINED Python_FIND_REGISTRY)
        set(Python_FIND_REGISTRY "LAST")
    endif ()
    if (NOT DEFINED Python_FIND_FRAMEWORK)
        set(Python_FIND_FRAMEWORK "LAST")
    endif ()
    find_package(Python REQUIRED COMPONENTS Interpreter)
    message(STATUS "Python executable: ${Python_EXECUTABLE}")
    execute_process(COMMAND ${Python_EXECUTABLE} -m pip install pre-commit)
    execute_process(COMMAND pre-commit install WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}")
endif ()

if (NOT EXISTS ${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    if (NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
        message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
        file(DOWNLOAD "https://raw.githubusercontent.com/conan-io/cmake-conan/master/conan.cmake" "${CMAKE_BINARY_DIR}/conan.cmake")
    endif ()
    include(${CMAKE_BINARY_DIR}/conan.cmake)
    conan_cmake_autodetect(settings)
    conan_cmake_install(PATH_OR_REFERENCE .. BUILD missing SETTINGS ${settings})
endif ()

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_VERBOSE_MAKEFILE ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
include(${CMAKE_BINARY_DIR}/conan_paths.cmake)
conan_basic_setup(${PROJECT_NAME} KEEP_RPATHS)

find_package(Qt6 COMPONENTS Core Widgets Gui CONFIG REQUIRED)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

file(GLOB QT_WITH_CONAN_SOURCES *.cc *.h)

# add executable
if (APPLE)
    add_executable(${PROJECT_NAME} MACOSX_BUNDLE ${QT_WITH_CONAN_SOURCES})
else ()
    add_executable(${PROJECT_NAME} MANUAL_FINALIZATION ${QT_WITH_CONAN_SOURCES})
endif ()

# linking
target_link_libraries(${PROJECT_NAME} PRIVATE
    ${CONAN_LIBS}
)
