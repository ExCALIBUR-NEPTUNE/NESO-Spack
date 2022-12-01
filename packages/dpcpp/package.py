# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# FIXME: Use os.path and builtin tools instead of pathlib
from os import path
from pathlib import Path

from llnl.util import filesystem
from spack import *

def _increment_version(version_tuple):
    return ".".join(map(str, version_tuple[:-1])) + "." + str(version_tuple[-1] + 1)

def _decrement_version(version_tuple):
    if len(version_tuple) == 0:
        return None
    if version_tuple[-1] == 0:
        return _decrement_version(version_tuple[:-1])
    return ".".join(map(str, version_tuple[:-1])) + "." + str(version_tuple[-1] - 1)

def _restrict_to_version(version):
    """Return a version constraint that only allows the specified version.
    """
    ver = tuple(map(int, version.split(".")))
    lower = _decrement_version(ver)
    upper = _increment_version(ver)
    if lower:
        return ":" + lower + "," + upper + ":"
    else:
        return upper + ":"

class Dpcpp(Package):
    """Dummy package that configures the DPC++ implementation of
    SYCL. This involves setting some extra environment variables for
    the Intel oneAPI compilers."""

    homepage = "https://software.intel.com/content/www/us/en/develop/tools/oneapi.html"
    maintainers = ["cmacmackin"]

    provides("sycl")

    # These are the same as the available versions of OneAPI
    # compilers.
    # TODO: Figure out how to get those versions
    # programmatically from the intel-oneapi-compilers package?
    available_versions = [
        "2022.2.1",
        "2022.2.0",
        "2022.1.0",
        "2022.0.2",
        "2022.0.1",
        "2021.4.0",
        "2021.3.0",
        "2021.2.0",
        "2021.1.2",
    ]
    for v in available_versions:
        version(v)
        # The version of DPC++ must be the same as that of the OneAPI compilers.
        conflicts(
            "%oneapi@" + _restrict_to_version(v), when="@" + v,
            msg="DPC++ version must match that of OneAPI compilers."
        )

    # This is a dummy package for oneAPI, so conflicts with all other compilers
    # FIXME: Is there a list from somewhere I can import to guarantee
    # nothing is forgotten?
    CONFLICTING_COMPILERS = [
        "%aocc",
        "%apple-clang",
        "%arm",
        "%cce",
        "%clang",
        "%dpcpp",
        "%fj",
        "%gcc",
        "%intel",
        "%msvc",
        "%nag",
        "%nvhpc",
        "%pgi",
        "%rocmcc",
        "%xl",
        "%xl-r",
    ]

    for comp in CONFLICTING_COMPILERS:
        conflicts(comp, msg="DPC++ only supported by Intel oneAPI compilers.")

    has_code = False
    phases = []

    @property
    def _compiler_dir(self):
        return Path(self.compiler.cxx).parent

    @property
    def _oneapi_root(self):
        return self._compiler_dir.parent.parent.parent.parent

    @property
    def cmake_prefix_paths(self):
        return [str(self._compiler_dir.parent / 'IntelDPCPP')]

    @property
    def _library_paths(self):
        return [
            self._oneapi_root / "tbb" / "latest" / "lib" / "intel64" / "gcc4.8",
            self._compiler_dir.parent / "lib",
            self._compiler_dir.parent / "lib" / "x64",
            self._compiler_dir.parent / "lib" / "oclfpga" / "host" / "linux64" / "lib",
            self._compiler_dir.parent / "compiler" / "lib" / "intel64_lin",
            self._compiler_dir.parent / "lib" / "emu",
            self._compiler_dir.parent / "lib" / "oclfpga" / "linux64" / "lib",
            self._compiler_dir.parent / "compiler" / "lib",
        ]

    @property
    def libs(self):
        libs = []
        for path in self._library_paths:
            libs += filesystem.find_libraries("*.so*", path)
        return libs
    
    def install(self):
        pass

    def _setup_common_dependent_environment(self, env, dependent_spec):
        env.set("ONEAPI_ROOT", str(self._oneapi_root))
        env.append_path("PATH", str(self._compiler_dir))
        # Need to set this in order to allow DLOPEN to find backend
        # libraries at runtime. Hopefully later releases will render
        # this unnecessary (see
        # https://github.com/intel/llvm/blob/sycl/sycl/doc/design/PluginInterface.md#plugin-discovery).
        for path in self._library_paths:
            #env.append_flags("__INTEL_PRE_CFLAGS", f"-Wl,-rpath,{path}")
            env.append_path("LD_LIBRARY_PATH", str(path))

    def setup_dependent_build_environment(self, env, dependent_spec):
        self._setup_common_dependent_environment(env, dependent_spec)
        env.prepend_path(
            "PKG_CONFIG_PATH", str(self._oneapi_root / "tbb" / "latest" / "lib" / "pkgconfig")
        )
        env.prepend_path(
            "PKG_CONFIG_PATH", str(self._compiler_dir.parent.parent / "lib" / "pkgconfig")
        )
        env.append_path("SYCL_INCLUDE_DIR_HINT", str(self._compiler_dir.parent))
        env.append_path("SYCL_LIBRARY_DIR_HINT", str(self._compiler_dir.parent))

    def setup_dependent_run_environment(self, env, dependent_spec):
        # Not clear which of these I really need, or whether they should be run-time or build-time
        self._setup_common_dependent_environment(env, dependent_spec)
