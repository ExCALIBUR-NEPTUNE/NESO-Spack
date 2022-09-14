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
        "fft",
        default="fftw",
        description="Library to use for FFTs",
        values=("fftw", "mkl"),
    )
    # FIXME: This should be a virtual package dependency, but Spack
    # doesn't seem to realise that intel-oneapi-compilers provides it
    # yet.
    variant(
        "sycl",
        default="hipsycl",
        description="SYCL implementation to compile with",
        values=("hipsycl", "oneapi"),
    )
    # variant(
    #     "sanitizer",
    #     description="The sanitizers to compile with",
    #     values=spack.variant.disjoint_sets(
    #         ("address", "leak", "undefined_behaviour"),
    #         ("thread", "undefined_behaviour"),
    #         ("memory", "undefined_behaviour"),
    #     ).with_default("none").with_error(
    #         "'thread' and 'memory' can not be combined with each other or with "
    #         "'address' or 'leak'"
    #     ),
    # )
    variant(
        "coverage", default=False, description="Enable coverage reporting for GCC/Clang"
    )

    # FIXME: Use virtual SYCL package
    depends_on("hipsycl", when="sycl=hipsycl")
    # FIXME: the onapi packages don't seem to configure the run
    # environment at all, meaning the computer can't find anything in
    # Intel's non-standard places. Also, should probably treat this as
    # a _compiler_ choice rather than a normal dependency.
    depends_on("intel-oneapi-compilers", when="sycl=oneapi", type="build")
    depends_on("intel-oneapi-dpl", when="sycl=oneapi")
    depends_on("intel-oneapi-tbb", when="sycl=oneapi")
    depends_on("fftw", when="fft=fftw")
    depends_on("intel-oneapi-mkl", when="fft=mkl")
    depends_on("nektar")
    depends_on("cmake@3.14:", type="build")
    depends_on("boost@1.78:", type="test")

    def cmake_args(self):
        args = []
        # for value in self.spec.variants['sanitizer'].value:
        #     if value != "none":
        #         args.append(f"-DENABLE_SANITIZER_{value.toupper()}=ON")
        if "+coverage" in self.spec:
            args.append("-DENABLE_COVERAGE=ON")
        # if "sycl=oneapi" in self.spec:
        #     args.append(f"-DIntelDPCPP_DIR={self.spec['intel-oneapi-compilers'].prefix}/compiler/latest/linux/IntelDPCPP")
        #     args.append(f"-DCMAKE_CXX_COMPILER={self.spec['intel-oneapi-compilers'].prefix}/compiler/latest/linux/bin/icpx")
        return args
