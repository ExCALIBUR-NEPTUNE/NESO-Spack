# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install neso
#
# You can edit this file again by typing:
#
#     spack edit neso
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

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
    """FIXME: Put a proper description of your package here."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://github.com/ExCALIBUR-NEPTUNE"
    git = "https://github.com/ExCALIBUR-NEPTUNE/NESO"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    maintainers = ["jwscook", "will-saunders-ukaea", "cmacmackin"]

    version('working', branch='main')
    version('main', branch='main')

    variant(
        "sanitizer",
        description="The sanitizers to compile with",
        values=("address", "leak", "thread", "memory", "undefined_behaviour"),
        default="none",
        multi=True,
        validator=_validate_sanitizer_variant,
    )
    variant(
        "coverage", default=False, description="Enable coverage reporting for GCC/Clang"
    )

    depends_on("sycl", type=("build", "link", "run"))
    depends_on("intel-oneapi-dpl", when="^dpcpp")
    depends_on("fftw-api")
    depends_on("nektar")
    depends_on("cmake@3.14:", type="build")
    depends_on("boost@1.78:", type="test")

    conflicts("%dpcpp", msg="Use oneapi compilers instead of dpcpp itself.")
    # This should really be set in teh MKL package itself...
    conflicts("^intel-oneapi-mkl@2022.2", when="%oneapi@:2022.1", msg="Use the same version of MKL and OneAPI compilers.")

    # Should these go here? In principle these may be buildable on
    # some systems or with some versions.
    conflicts("^py-numpy%oneapi", msg="Requires too much RAM to build Numpy with OneAPI compilers.")
    conflicts("^boost%oneapi", msg="Requires too much RAM to build Boost with OneAPI compilers.")

    def cmake_args(self):
        args = []
        for value in self.spec.variants['sanitizer'].value:
            if value != "none":
                args.append(f"-DENABLE_SANITIZER_{value.toupper()}=ON")
        if "+coverage" in self.spec:
            args.append("-DENABLE_COVERAGE=ON")
        return args
