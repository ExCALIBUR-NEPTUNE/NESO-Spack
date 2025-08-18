# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# FIXME: Use os.path and builtin tools instead of pathlib
from os import path
from pathlib import Path

import spack
from spack import *
from spack.package import *

if spack_version_info[0] >= 1:
    from spack_repo.builtin.build_systems.generic import Package
    from spack.llnl.util import filesystem
else:
    from llnl.util import filesystem


def _get_pkg_versions(pkg_name):
    """Get a list of 'safe' (already checksummed) available versions of a Spack package
    Equivalent to 'spack versions <pkg_name>' on the command line"""
    pkg_spec = spack.spec.Spec(pkg_name)
    spack_version = spack.spack_version_info
    if spack_version[0] < 1 and spack_version[1] <= 20:
        pkg_cls = spack.repo.path.get_pkg_class(pkg_name)
    else:
        pkg_cls = spack.repo.PATH.get_pkg_class(pkg_name)
    pkg = pkg_cls(pkg_spec)
    return [vkey.string for vkey in pkg.versions.keys()]


def _restrict_to_version(versions, idx):
    """Return a version constraint that excludes all but
    versions[idx]. Requires versions to be sorted in descending
    order."""
    if idx == 0:
        return ":" + versions[1]
    elif idx == len(versions) - 1:
        return versions[-2] + ":"
    else:
        return ":" + versions[idx + 1] + "," + versions[idx - 1] + ":"


class Dpcpp(Package):
    """Dummy package that configures the DPC++ implementation of
    SYCL. This involves setting some extra environment variables for
    the Intel oneAPI compilers."""

    homepage = (
        "https://software.intel.com/content/www/us/en/develop/tools/oneapi.html"
    )
    maintainers = ["cmacmackin"]

    # These are the same as the available versions of OneAPI
    # compilers.
    available_versions = _get_pkg_versions("intel-oneapi-compilers")
    for idx, v in enumerate(available_versions):
        version(v)
        # The version of DPC++ must be the same as that of the OneAPI compilers.
        conflicts(
            "%oneapi@" + _restrict_to_version(available_versions, idx),
            when="@" + v,
            msg="DPC++ version must match that of OneAPI compilers.",
        )

    # This has to come after the versions (only became an issue after
    # automatically identifying oneAPI versions, for some reason)
    provides("sycl")

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
        return [str(self._compiler_dir.parent / "IntelDPCPP")]

    @property
    def _library_paths(self):
        return [
            self._oneapi_root / "tbb" / "latest" / "lib" / "intel64" / "gcc4.8",
            self._compiler_dir.parent / "lib",
            self._compiler_dir.parent / "lib" / "x64",
            self._compiler_dir.parent
            / "lib"
            / "oclfpga"
            / "host"
            / "linux64"
            / "lib",
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
            # env.append_flags("__INTEL_PRE_CFLAGS", f"-Wl,-rpath,{path}")
            env.append_path("LD_LIBRARY_PATH", str(path))

    def setup_dependent_build_environment(self, env, dependent_spec):
        self._setup_common_dependent_environment(env, dependent_spec)
        env.prepend_path(
            "PKG_CONFIG_PATH",
            str(self._oneapi_root / "tbb" / "latest" / "lib" / "pkgconfig"),
        )
        env.prepend_path(
            "PKG_CONFIG_PATH",
            str(self._compiler_dir.parent.parent / "lib" / "pkgconfig"),
        )
        env.append_path("SYCL_INCLUDE_DIR_HINT", str(self._compiler_dir.parent))
        env.append_path("SYCL_LIBRARY_DIR_HINT", str(self._compiler_dir.parent))

    def setup_dependent_run_environment(self, env, dependent_spec):
        # Not clear which of these I really need, or whether they should be run-time or build-time
        self._setup_common_dependent_environment(env, dependent_spec)
