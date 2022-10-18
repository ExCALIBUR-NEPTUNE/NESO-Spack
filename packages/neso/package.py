# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
from spack.error import SpecError

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

    # Some SYCL packages require a specific run-time environment to be set
    depends_on("sycl", type=("build", "link"))
    depends_on("intel-oneapi-dpl", when="^dpcpp", type="link")
    depends_on("fftw-api", type="link")
    depends_on("nektar", type="link")
    depends_on("cmake@3.14:", type="build")
    depends_on("boost@1.78:", type="test")

    conflicts("%dpcpp", msg="Use oneapi compilers instead of dpcpp driver.")
    # This should really be set in the MKL package itself...
    conflicts("^intel-oneapi-mkl@2022.2", when="%oneapi@:2022.1", msg="Use the same version of MKL and OneAPI compilers.")
    conflicts("^dpcpp", when="%gcc", msg="DPC++ can only be used with Intel oneAPI compilers.")

    def cmake_args(self):
        args = []
        for value in self.spec.variants['sanitizer'].value:
            if value != "none":
                args.append(f"-DENABLE_SANITIZER_{value.upper()}=ON")
        if "+coverage" in self.spec:
            args.append("-DENABLE_COVERAGE=ON")
        return args
