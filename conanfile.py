import os
import subprocess

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake


class CamouflageTLS(ConanFile):
    name = "camouflage-tls"
    version = "1.0.0"
    settings = (
        "os",
        "arch",
        "compiler",
        "build_type",
    )
    generators = ("CMakeDeps",)

    default_options = {
        # -- depends --
        "*:fPIC": True,
        "*:shared": False,
    }
    exports_sources = (
        "CMakeLists.txt",
        "src/*",
        "include/*",
        "tests/*",
    )

    def build_requirements(self):
        self.test_requires("gtest/1.17.0")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
