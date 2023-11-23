# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from os import environ
from spack.package import *
from spack.error import SpecError
from warnings import warn

def _validate_sanitizer_variant(pkg_name, variant_name, values):
    """Checks that the combination of sanitizer types is valid."""
    if "none" in values and len(values) > 1:
        raise SpecError(
            "sanitizer variant value 'none' can not be combined with any other values."
        )
    if "thread" in values and ("address" in values or "leak" in values or "memory" in values):
        raise SpecError(
            "'thread' sanitizer can not be combined with 'address', 'leak', or 'memory' sanitizers"
        )
    if "memory" in values and ("address" in values or "leak" in values):
        raise SpecError(
            "'memory' sanitizer can not be combined with 'address' or 'leak' sanitizers"
        )
    

class Neso(CMakePackage):
    """This is a test implmentation of a PIC solver for 1+1D Vlasov
    Poisson, written in C++/DPC++. This is primarily designed to test
    the use of multiple repos/workflows for different code
    components."""

    homepage = "https://github.com/ExCALIBUR-NEPTUNE"
    git = "https://github.com/ExCALIBUR-NEPTUNE/NESO"

    maintainers = ["jwscook", "will-saunders-ukaea", "cmacmackin"]

    version('working', branch='main')
    version('main', branch='main')

    variant(
        "sanitizer",
        description="The sanitizers to compile with",
        values=("none", "address", "leak", "thread", "memory", "undefined_behaviour"),
        default="none",
        multi=True,
        validator=_validate_sanitizer_variant,
    )
    variant(
        "coverage", default=False, description="Enable coverage reporting for GCC/Clang"
    )
    variant(
        "nvcxx", default=False, description="Enable compilation using nvcxx"
    )

    # Some SYCL packages require a specific run-time environment to be set
    depends_on("sycl", type=("build", "link"))
    depends_on("intel-oneapi-dpl", when="^dpcpp", type="link")
    depends_on("fftw-api", type="link")
    depends_on("nektar+compflow_solver", type="link")
    depends_on("cmake@3.14:", type="build")
    depends_on("boost@1.74:", type="test")
    depends_on("googletest+gmock", type="link")
    depends_on("neso-particles")

    conflicts("%dpcpp", msg="Use oneapi compilers instead of dpcpp driver.")
    # This should really be set in the MKL package itself...
    conflicts("^intel-oneapi-mkl@2022.2", when="%oneapi@:2022.1", msg="Use the same version of MKL and OneAPI compilers.")
    conflicts("^dpcpp", when="%gcc", msg="DPC++ can only be used with Intel oneAPI compilers.")

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
        
        for value in self.spec.variants['sanitizer'].value:
            if value != "none":
                args.append(f"-DENABLE_SANITIZER_{value.upper()}=ON")
        if "intel" in self.spec["mpi"].name:
            if "I_MPI_FABRICS" not in environ:
                warn("The intel mpi specific environment variable, I_MPI_FABRICS, has not been set and an intel-MPI build will fail. If you are developing on an unmanaged-HPC machine, i.e. locally on your workstation, a sensible default `export I_MPI_FABRICS=shm`. Information can be found on the intel documentation pages https://tinyurl.com/33w8x8wp.", UserWarning, stacklevel=1)
        for depspec in  self.spec.dependencies():
            for dep in depspec.dependents():
                if "sycl" in dep:
                    if "SYCL_DEVICE_FILTER" not in environ:
                        warn("The environment variable SYCL_DEVICE_FILTER is not set and the code may not run as intended in this environment. A sensible default for running on the cpu is `export SYCL_DEVICE_FILTER=host`. For more information please see e.g. https://tinyurl.com/y37672as.", UserWarning, stacklevel=1)

                    break

        if "+nvcxx" in self.spec:
            args.append("-DHIPSYCL_TARGETS=cuda-nvcxx")
            args.append("-DSYCL_DEVICE_FILTER=GPU")

        return args
