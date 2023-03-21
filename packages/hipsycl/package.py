# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import json
from os import path
from glob import glob

from llnl.util import filesystem

from spack import *

"""
Install nvc++ version with soemthing like

    spack install neso.hipsycl -cuda +nvcxx ^cuda@11.7

# openmp only
    spack install neso.hipsycl -cuda -nvcxx
to avoid llvm build
"""


class Hipsycl(CMakePackage):
    """hipSYCL is an implementation of the SYCL standard programming model
    over NVIDIA CUDA/AMD HIP"""

    homepage = "https://github.com/illuhad/hipSYCL"
    url = "https://github.com/illuhad/hipSYCL/archive/v0.8.0.tar.gz"
    git = "https://github.com/illuhad/hipSYCL.git"

    maintainers = ["nazavode"]

    provides("sycl")

    version("stable", branch="stable", submodules=True)
    version(
        "0.9.4",
        commit="99d9e24d462b35e815e0e59c1b611936c70464ae",
        submodules=True)
    version(
        "0.9.3",
        commit="51507bad524c33afe8b124804091b10fa25618dc",
        submodules=True)
    version(
        "0.9.2",
        commit="49fd02499841ae884c61c738610e58c27ab51fdb",
        submodules=True)

    variant(
        "cuda",
        default=False,
        description="Enable CUDA backend for SYCL kernels using llvm+cuda",
    )
    variant(
        "nvcxx",
        default=False,
        description="Enable CUDA backend for SYCL kernels using nvcxx",
    )
    variant(
        "omp_llvm",
        default=False,
        description="Enable accelerated OMP backend for SYCL kernels using LLVM",
    )

    depends_on("cmake@3.5:", type="build")
    depends_on("boost +filesystem", when="@:0.8")
    depends_on("boost@1.60.0: +filesystem +fiber +context cxxstd=17", when='@0.9.1:')
    depends_on("python@3:")
    # depends_on("llvm@8: +clang", when="~cuda")
    depends_on("llvm@9: +clang", when="+cuda")
    depends_on("llvm@9: +clang", when="+omp_llvm")
    # LLVM PTX backend requires cuda7:10.1 (https://tinyurl.com/v82k5qq)
    depends_on("cuda@9:10.1", when="@0.8.1: +cuda")
    # hipSYCL@:0.8.0 requires cuda@9:10.0 due to a known bug
    depends_on("cuda@9:10.0", when="@:0.8.0 +cuda")

    depends_on("cuda", when="+nvcxx")
    depends_on("nvhpc@22.9:", when="+nvcxx", type="run")

    conflicts(
        "%gcc@:4",
        when='@:0.9.0',
        msg="hipSYCL needs proper C++14 support to be built, %gcc is too old",
    )
    conflicts(
        "%gcc@:8",
        when='@0.9.1:',
        msg="hipSYCL needs proper C++17 support to be built, %gcc is too old")
    conflicts(
        "^llvm build_type=Debug",
        when="+cuda",
        msg="LLVM debug builds don't work with hipSYCL CUDA backend; for "
        "further info please refer to: "
        "https://github.com/illuhad/hipSYCL/blob/master/doc/install-cuda.md",
    )

    def cmake_args(self):

        spec = self.spec
        args = [
            "-DWITH_CPU_BACKEND:Bool=TRUE",
            # TODO: no ROCm stuff available in spack yet
            "-DWITH_ROCM_BACKEND:Bool=FALSE",
        ]
        
        if 'llvm' in spec:
            # prevent hipSYCL's cmake to look for other LLVM installations
            # if the specified one isn't compatible
            args += [
                "-DDISABLE_LLVM_VERSION_CHECK:Bool=TRUE",
            ]

            # LLVM directory containing all installed CMake files
            # (e.g.: configs consumed by client projects)
            llvm_cmake_dirs = filesystem.find(
                spec["llvm"].prefix, "LLVMExports.cmake"
            )
            if len(llvm_cmake_dirs) != 1:
                raise InstallError(
                    "concretized llvm dependency must provide "
                    "a unique directory containing CMake client "
                    "files, found: {0}".format(llvm_cmake_dirs)
                )
            args.append(
                "-DLLVM_DIR:String={0}".format(path.dirname(llvm_cmake_dirs[0]))
            )
            # clang internal headers directory
            llvm_clang_include_dirs = filesystem.find(
                spec["llvm"].prefix, "__clang_cuda_runtime_wrapper.h"
            )
            if len(llvm_clang_include_dirs) != 1:
                raise InstallError(
                    "concretized llvm dependency must provide a "
                    "unique directory containing clang internal "
                    "headers, found: {0}".format(llvm_clang_include_dirs)
                )
            args.append(
                "-DCLANG_INCLUDE_PATH:String={0}".format(
                    path.dirname(llvm_clang_include_dirs[0])
                )
            )
            # target clang++ executable
            llvm_clang_bin = path.join(spec["llvm"].prefix.bin, "clang++")
            if not filesystem.is_exe(llvm_clang_bin):
                raise InstallError(
                    "concretized llvm dependency must provide a "
                    "valid clang++ executable, found invalid: "
                    "{0}".format(llvm_clang_bin)
                )
            args.append(
                "-DCLANG_EXECUTABLE_PATH:String={0}".format(llvm_clang_bin)
            )

        else:
            args += [
                "-DCMAKE_C_FLAGS=-fopenmp",
                "-DCMAKE_CXX_FLAGS=-fopenmp",
            ]

        if ("+cuda" in spec) or ("+nvcxx" in spec):
            args += [
                "-DCUDA_TOOLKIT_ROOT_DIR:String={0}".format(
                    spec["cuda"].prefix
                ),
                "-DWITH_CUDA_BACKEND:Bool=TRUE"
            ]
        else:
            args += [
                "-DWITH_CUDA_BACKEND:Bool=FALSE",
            ]

        if "+nvcxx" in spec:
            nvcpp_cands = glob(path.join(spec["nvhpc"].prefix, "**/nvc++"), recursive=True)
            if len(nvcpp_cands) < 1:
                raise InstallError(
                    "Failed to find nvc++ executable"
                )
            args.append(
                "-DNVCXX_COMPILER={0}".format(nvcpp_cands[0])
            )

            if not ("llvm" in spec):
                args.append(
                    "-DWITH_CUDA_NVCXX_ONLY=ON"
                )

        if not ("llvm" in spec):
            args += [
                "-DWITH_ACCELERATED_CPU=OFF",
                "-DBUILD_CLANG_PLUGIN=OFF",
            ]

        return args

    @run_after("install")
    def filter_config_file(self):

        config_file_paths = filesystem.find(self.prefix, "syclcc.json")
        if len(config_file_paths) != 1:
            raise InstallError(
                "installed hipSYCL must provide a unique compiler driver "
                "configuration file, found: {0}".format(config_file_paths)
            )
        config_file_path = config_file_paths[0]
        with open(config_file_path) as f:
            config = json.load(f)
        # 1. Fix compiler: use the real one in place of the Spack wrapper
        config["default-cpu-cxx"] = self.compiler.cxx
        # 2. Fix stdlib: we need to make sure cuda-enabled binaries find
        #    the libc++.so and libc++abi.so dyn linked to the sycl
        #    ptx backend

        if "llvm" in self.spec:
            rpaths = set()
            so_paths = filesystem.find(self.spec["llvm"].prefix, "libc++.so")
            if len(so_paths) != 1:
                raise InstallError(
                    "concretized llvm dependency must provide a "
                    "unique directory containing libc++.so, "
                    "found: {0}".format(so_paths)
                )
            rpaths.add(path.dirname(so_paths[0]))
            so_paths = filesystem.find(self.spec["llvm"].prefix, "libc++abi.so")
            if len(so_paths) != 1:
                raise InstallError(
                    "concretized llvm dependency must provide a "
                    "unique directory containing libc++abi.so, "
                    "found: {0}".format(so_paths)
                )
            rpaths.add(path.dirname(so_paths[0]))
            config["default-cuda-link-line"] += " " + " ".join(
                "-rpath {0}".format(p) for p in rpaths
            )

        # Replace the installed config file
        with open(config_file_path, "w") as f:
            json.dump(config, f, indent=2)
