"""
Notes
=====

This file contains a Spack package to handle building with the IntelSYCL
implementation.

Compiler
--------

The IntelSYCL compiler, and a runtime, is packaged within the
intel-oneapi-compilers Spack package. However in spack the package which
"provides sycl" is the intel-oneapi-runtime package. The intel-oneapi-runtime
package may or may not, depending on when you are reading this, load all the
required environment variables to use the IntelSYCL implementation. Note that
we make this package "provide sycl" such that it is included in the dependency
tree.

IntelSYCL Runtime
-----------------

The easiest way to test if the IntelSYCL runtime is successfully loaded is to
run the sycl-ls tool. This tool is packaged in the intel-oneapi-compilers Spack
package. This utility is a SYCL program itself, hence if it does successfully
find an expected SYCL backend in a given environment then the environment is
usually setup correctly to run IntelSYCL applications. For example,

    ~$ sycl-ls
    [opencl:cpu][opencl:0] Intel(R) OpenCL, AMD Ryzen Threadripper 7970X 32-Cores

The IntelSYCL runtime is OpenCL based and assumes that the OCL_ICD_FILENAMES
environment variable contains an Intel OpenCL library, e.g.

    OCL_ICD_FILENAMES=/opt/spack-v1.0.1/linux-zen4/intel-oneapi-compilers-2025.2.0-7jirzirkyx3xvispmd375dtw6ieu6gt5/compiler/2025.2/lib/libintelocl.so

The OCL_ICD_FILENAMES variable does seem to be correctly set on loading
intel-oneapi-compilers either via spack load or modules at the time of writing.

The IntelSYCL CPU runtime depends, at the time of writing, on a compatible set
of TBB libraries being available. In this context "available" means that the
LD_LIBRARY_PATH contains paths which contain the compatible TBB libraries. If
sycl-ls returns no CPU backends then check TBB has been loaded. This package
attempts to make available the TBB shipped with intel-oneapi-compilers at build
time and runtime.

If TBB is still not loaded correctly navigate to the intel-oneapi-compilers
directory, e.g. find the install directory with

    $ spack find --paths intel-oneapi-compilers
    # or, if intel-oneapi-compilers is loaded
    $ which icpx

then source the file as follows

    source <intel-oneapi-compilers-install-prefix>/tbb/latest/env/vars.sh

If you are attempting to modify this package to fix TBB related issues, see the
end of the above file to investigate what should be set.

TBB Runtimes
------------

Many of the intel-oneapi-* packages come with a vendored copy of TBB as part of
the package. It seems that for each release of intel-oneapi-* there is a
corresponding TBB release in intel-oneapi-tbb. We source the TBB shipped in the
intel-oneapi-compilers package as we definitely depend on 
intel-oneapi-compilers and the copy shipped with intel-oneapi-compilers
contains the cmake files as well as the runtime libraries and header files.

MKL TBB Dependency
------------------

The intel-oneapi-mkl package has a virtual dependency on TBB. The
intel-oneapi-mkl package also contains a copy of TBB as discussed in the
previous paragraph. If your downstream package depends on intel-oneapi-mkl it
is recommended that you specify MKL as 

    ^intel-oneapi-mkl@version %intel-oneapi-tbb@compatible-version

Failure to specify a intel-oneapi-tbb package may cause Spack to satisfy the
TBB dependency with a different, non-oneapi, TBB package.
"""

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
        # We depend on intel-oneapi-compilers explicitly at build time such
        # that this package can inspect the prefix to create the envrionment
        # variables. We depend on intel-oneapi-compilers at runtime to ensure
        # that intel-oneapi-compilers is loaded as a runtime dependency for
        # downstream packages built with dpcpp.
        depends_on(
            "intel-oneapi-compilers@" + v,
            when="@" + v,
            type=("build", "link", "run"),
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
        conflicts(
            comp,
            msg=f"DPC++ only supported by Intel oneAPI compilers. Compiler is {comp}.",
        )

    has_code = False
    phases = []

    # For some reason the spack package wrapper will not find or run these
    # methods if they are marked with @property.
    def _compiler_dir(self):
        return self._oneapi_root() / "compiler" / "latest" / "bin"

    def _oneapi_root(self):
        return Path(self.spec["intel-oneapi-compilers"].prefix)

    def _oneapi_tbb_root(self):
        return self._oneapi_root() / "tbb" / "latest"

    def _library_paths(self):
        # WRS note: I've trimmed this list to remove the paths that mention
        # emulation or fpgas.
        return [
            self._compiler_dir().parent / "lib",
            self._compiler_dir().parent / "lib" / "x64",
            self._compiler_dir().parent / "compiler" / "lib" / "intel64_lin",
            self._compiler_dir().parent / "compiler" / "lib",
        ]

    def install(self):
        pass

    def _setup_common_dependent_environment(self, env):
        env.set("ONEAPI_ROOT", str(self._oneapi_root()))
        env.append_path("PATH", str(self._compiler_dir()))
        # Need to set this in order to allow DLOPEN to find backend
        # libraries at runtime. Hopefully later releases will render
        # this unnecessary (see
        # https://github.com/intel/llvm/blob/sycl/sycl/doc/design/PluginInterface.md#plugin-discovery).
        for path in self._library_paths():
            # env.append_flags("__INTEL_PRE_CFLAGS", f"-Wl,-rpath,{path}")
            env.append_path("LD_LIBRARY_PATH", str(path))
            env.append_path("LIBRARY_PATH", str(path))

        env.prepend_path(
            "PKG_CONFIG_PATH",
            str(self._compiler_dir().parent.parent / "lib" / "pkgconfig"),
        )

        # IntelSYCL does not behave well if these are a list rather than a
        # single path.
        for var in ("SYCL_INCLUDE_DIR_HINT", "SYCL_LIBRARY_DIR_HINT"):
            if not var in env:
                env.set(var, str(self._compiler_dir().parent))

        # If this env var is not set sycl-ls will work with spack load but not
        # modules?
        env.append_path(
            "OCL_ICD_FILENAMES",
            str(self._compiler_dir().parent / "lib" / "libintelocl.so"),
        )

        # Make available the TBB that is shipped with intel-oneapi-compilers.
        # IntelSYCL needs this at runtime to run hence if something else is
        # going to try and find a TBB install it should find the same install
        # that will be loaded at runtime. Packages that do require TBB should
        # specifiy ^intel-oneapi-tbb with a version that matches the TBB
        # shipped with the corresponding intel-oneapi-compilers.
        env.set("TBBROOT", str(self._oneapi_tbb_root()))
        tbb_library_path = (
            self._oneapi_tbb_root() / "lib" / "intel64" / "gcc4.8"
        )
        env.append_path("LD_LIBRARY_PATH", str(tbb_library_path))
        env.append_path("LIBRARY_PATH", str(tbb_library_path))
        env.append_path(
            "C_INCLUDE_PATH", str(self._oneapi_tbb_root() / "include")
        )
        env.append_path(
            "CPLUS_INCLUDE_PATH", str(self._oneapi_tbb_root() / "include")
        )
        env.append_path("CMAKE_PREFIX_PATH", str(self._oneapi_tbb_root()))
        env.append_path(
            "PKG_CONFIG_PATH",
            str(self._oneapi_tbb_root() / "lib" / "pkgconfig"),
        )

    def setup_dependent_build_environment(self, env, dependent_spec):
        self._setup_common_dependent_environment(env)

    def setup_dependent_run_environment(self, env, dependent_spec):
        # Not clear which of these I really need, or whether they should be
        # run-time or build-time
        self._setup_common_dependent_environment(env)

    def setup_run_environment(self, env):
        # We set these such that sycl-ls should work with "spack load dpcpp"
        self._setup_common_dependent_environment(env)
