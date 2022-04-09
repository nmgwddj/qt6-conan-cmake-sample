cmake_minimum_required(VERSION 3.18)

# 设置基础环境
set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_VERBOSE_MAKEFILE ON)

# 设置默认的编译配置为 Debug，conan.cmake 需要确定你当前正在使用哪种编译配置以决定如何下载和编译三方库
if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Debug" CACHE STRING "Choose the type of build." FORCE)
    message(STATUS "No CMAKE_BUILD_TYPE selected, defaulting to ${CMAKE_BUILD_TYPE}")
endif ()

project(QtWithConan VERSION 0.1 LANGUAGES CXX)

# 判断如果当前 CMAKE_BINARY_DIR 目录没有 conanbuildinfo.cmake 的配置信息证明还没有正确加载 Conan 库
# 从 github 下载好 conan.cmake 并 include 到 CMake 工程中
# 判断是否指定了 CONAN_PROFILE_BUILD 和 CONAN_PROFILE_HOST 参数以决定是否使用交叉编译，这里暂时不讨论
# 如果不是交叉编译，则调用 conan_cmake_autodetect 自动监测当前 CMake 环境配置，如 C++ 标准、build-type、编译器等信息
# 调用 conan_cmake_install 根据获取的 settings 和 conanfile.py 配置自动安装依赖包，其中 BUILD mssing 表示如果 conan center 没有我们需要的预编译包，则执行本地编译。
if (NOT EXISTS ${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    if (NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
        message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
        file(DOWNLOAD "https://raw.githubusercontent.com/conan-io/cmake-conan/master/conan.cmake" "${CMAKE_BINARY_DIR}/conan.cmake")
    endif ()
    include(${CMAKE_BINARY_DIR}/conan.cmake)
    if (CONAN_PROFILE_BUILD AND CONAN_PROFILE_HOST)
    conan_cmake_install(PATH_OR_REFERENCE .. BUILD missing
                        SETTINGS_HOST build_type=${CMAKE_BUILD_TYPE}
                        SETTINGS_BUILD build_type=${CMAKE_BUILD_TYPE}
                        PROFILE_BUILD ${CONAN_PROFILE_BUILD}
                        PROFILE_HOST ${CONAN_PROFILE_HOST})
                        # ENV_HOST CONAN_CMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE})
    else ()
        conan_cmake_autodetect(settings)
        conan_cmake_install(PATH_OR_REFERENCE .. BUILD missing SETTINGS ${settings})
    endif ()
endif ()

# 在 conan_cmake_install 执行后，会在 CMAKE_BINARY_DIR 目录下生成 cmake 的配置信息和 Qt 的依赖库路径信息，我们将其引入到 CMake 工程中，并调用 conan_basic_setup 来自动配置各个环境变量信息。
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
include(${CMAKE_BINARY_DIR}/conan_paths.cmake)
conan_basic_setup(${PROJECT_NAME} KEEP_RPATHS)

# 查找 Qt 包信息备用
if (MSVC)
  find_package(Qt5 COMPONENTS Core Widgets Gui CONFIG REQUIRED)
else ()
  find_package(Qt6 COMPONENTS Core Widgets Gui CONFIG REQUIRED)
endif ()

# 开启 MOC
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

# 扫描当前源代码文件列表
file(GLOB QT_WITH_CONAN_SOURCES *.cc *.h)

# 创建可执行程序
if (APPLE)

  add_executable(${PROJECT_NAME} MACOSX_BUNDLE ${QT_WITH_CONAN_SOURCES})
else ()
  add_executable(${PROJECT_NAME} ${QT_WITH_CONAN_SOURCES})
endif ()

# 链接 Conan 指向的 Qt 库文件
target_link_libraries(${PROJECT_NAME} PRIVATE
  ${CONAN_LIBS}
)

if (APPLE)
  # macOS 下我们查找 macdeployqt 可执行程序
  find_program(DEPLOYQT_EXECUTABLE macdeployqt)
  # 设置仅在 Release 发布包编译后执行 deploy 操作。因为调试环境下我们所依赖的库路径都已经在可执行程序的 @rpath 中了。所以没有必要每次都部署
  if (CMAKE_BUILD_TYPE STREQUAL "Release")
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
      COMMAND ${DEPLOYQT_EXECUTABLE} ${CMAKE_BINARY_DIR}/bin/QtWithConan.app
      COMMENT "Deploying qt dependencies after build..."
      WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    )
  endif()
endif ()
if (MSVC)
  # Windows 下我们查找 windeployqt 可执行程序
  find_program(DEPLOYQT_EXECUTABLE windeployqt)
  # Windows 同上，但是不能仅在 Release 下才执行，调试环境依然需要部署
  add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${DEPLOYQT_EXECUTABLE} ${CMAKE_BINARY_DIR}/bin/QtWithConan.exe
    COMMENT "Deploying qt dependencies after build..."
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  )
endif ()
