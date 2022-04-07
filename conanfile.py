from conans import ConanFile, tools
import platform


class ModuleConan(ConanFile):
    name = "QtConanExample"
    description = "An example for Qt with Conan"
    settings = "os", "compiler", "build_type", "arch"
    generators = "qt", "cmake", "cmake_find_package_multi", "cmake_paths"
    default_options = "qt:shared=True"

    def configure(self):
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("qt/6.2.4")
        self.requires("openssl/1.1.1m")
        self.requires("harfbuzz/4.2.0")
