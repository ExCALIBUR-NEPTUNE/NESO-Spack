# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from os import environ
from spack import *
from spack.package import *
from spack.error import SpecError
import spack
from warnings import warn

if spack_version_info[0] >= 1:
    from spack_repo.builtin.build_systems.cmake import CMakePackage


def _validate_sanitizer_variant(pkg_name, variant_name, values):
    """Checks that the combination of sanitizer types is valid."""
    if "none" in values and len(values) > 1:
        raise SpecError(
            "sanitizer variant value 'none' can not be combined with any other values."
        )
    if "thread" in values and (
        "address" in values or "leak" in values or "memory" in values
    ):
        raise SpecError(
            "'thread' sanitizer can not be combined with 'address', 'leak', or 'memory' sanitizers"
        )
    if "memory" in values and ("address" in values or "leak" in values):
        raise SpecError(
            "'memory' sanitizer can not be combined with 'address' or 'leak' sanitizers"
        )


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


AVAILABLE_ONEAPI_VERSIONS = _get_pkg_versions("intel-oneapi-compilers")


class Neso(CMakePackage):
    """This is a test implmentation of a PIC solver for 1+1D Vlasov
    Poisson, written in C++/DPC++. This is primarily designed to test
    the use of multiple repos/workflows for different code
    components."""

    homepage = "https://github.com/ExCALIBUR-NEPTUNE"
    git = "https://github.com/ExCALIBUR-NEPTUNE/NESO"

    maintainers = ["jwscook", "will-saunders-ukaea", "cmacmackin"]

    version("working", branch="main")
    version("main", branch="main")

    variant(
        "sanitizer",
        description="The sanitizers to compile with",
        values=(
            "none",
            "address",
            "leak",
            "thread",
            "memory",
            "undefined_behaviour",
        ),
        default="none",
        multi=True,
        validator=_validate_sanitizer_variant,
    )
    variant(
        "coverage",
        default=False,
        description="Enable coverage reporting for GCC/Clang",
    )
    variant(
        "nvcxx",
        default=False,
        description="Deprecated, please use '^neso.adaptivecpp compilationflow=cudanvcxx' instead. Enable compilation using nvcxx",
    )
    variant(
        "cwipi",
        default=False,
        description="Enables CWIPI support in Nektar++ and builds CWIPI-dependent examples",
    )
    variant(
        "nvcxx", default=False, description="Enable compilation using nvcxx"
    )
    variant(
        "libonly",
        default=False,
        description="Only compiles the library elements and not the solvers or tests",
    )

    depends_on("c")
    depends_on("cxx")
    # Some SYCL packages require a specific run-time environment to be set
    depends_on("sycl", type=("build", "link"))
    depends_on("intel-oneapi-dpl", when="^dpcpp", type="link")
    depends_on("fftw-api", type="link")
    depends_on("cmake@3.24:", type="build")
    depends_on("boost@1.74:", type="test")
    depends_on("googletest+gmock", type="link")
    depends_on("neso-particles")
    depends_on("mpi", type=("build", "run"))

    # backwards compatibility and workarounds for intel packaging
    depends_on("neso.adaptivecpp compilationflow=cudanvcxx", when="+nvcxx")

    # Nektar++ dependency
    nektar_base_spec = "nektar@5.3.0-2022-09-03:+compflow_solver"
    depends_on(nektar_base_spec, when="~cwipi", type="link")
    depends_on(nektar_base_spec + "+cwipi", when="+cwipi", type="link")

    conflicts("%dpcpp", msg="Use oneapi compilers instead of dpcpp driver.")
    conflicts(
        "^dpcpp",
        when="%gcc",
        msg="DPC++ can only be used with Intel oneAPI compilers.",
    )
    conflicts(
        "+nvcxx",
        when="%oneapi",
        msg="Nvidia compilation option can only be used with gcc compilers",
    )
    # Should only use MKL with the same release of OneAPI
    # compilers. Ideally this would have been set in the MKL package
    # itself.
    for idx, v in enumerate(AVAILABLE_ONEAPI_VERSIONS):
        conflicts(
            "^intel-oneapi-mkl@"
            + _restrict_to_version(AVAILABLE_ONEAPI_VERSIONS, idx),
            when="%oneapi@" + v,
            msg="OneAPI compilers and MKL must be from the same release.",
        )

    def cmake_args(self):
        # Ideally we would only build the tests when Spack is going to
        # run them. However, Spack's testing is currently broken in
        # environments (see
        # https://github.com/spack/spack/issues/29447), so we we will
        # build the tests unconditionally until that is resolved.
        #
        # TODO: Fix, issue NESO#128
        args = [
            # self.define("ENABLE_NESO_TESTS", self.run_tests),
            self.define_from_variant("ENABLE_COVERAGE", "coverage"),
        ]

        for value in self.spec.variants["sanitizer"].value:
            if value != "none":
                args.append(f"-DENABLE_SANITIZER_{value.upper()}=ON")
        if "intel" in self.spec["mpi"].name:
            if "I_MPI_FABRICS" not in environ:
                warn(
                    "The intel mpi specific environment variable, I_MPI_FABRICS, has not been set. This environment variable should be set on certain platforms, e.g. Docker, where `export I_MPI_FABRICS=shm` may prevent issues. Information can be found on the intel documentation pages https://tinyurl.com/33w8x8wp.",
                    UserWarning,
                    stacklevel=1,
                )

        if "+cwipi" in self.spec:
            args.append("-DNESO_BUILD_CWIPI_EXAMPLES=ON")

        if "+libonly" in self.spec:
            args.append("-DNESO_BUILD_SOLVERS=OFF")
            args.append("-DNESO_BUILD_TESTS=OFF")

        return args
