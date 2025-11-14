from spack import *
from spack.package import *
from pathlib import Path

if spack_version_info[0] >= 1:
    from spack_repo.builtin.build_systems.cmake import CMakePackage


class NesoRngToolkit(CMakePackage):
    """NESO-RNG-Toolkit provides an abstract SYCL interface to vendor supplied
    RNG implementations. The variants allow particular RNG implementations to
    be explicitly enabled. If the spec contains ^dpcpp then this package should
    automatically enable the oneMKL platform. If the NESO adaptivecpp package
    is in the spec then this package should enable the vendor platform that
    corresponds to the specified compilation flow."""

    homepage = "https://github.com/ExCALIBUR-NEPTUNE/NESO-RNG-Toolkit.git"

    git = "https://github.com/ExCALIBUR-NEPTUNE/NESO-RNG-Toolkit.git"

    version("working", branch="main")
    version("main", branch="main")

    variant(
        "onemkl",
        default=False,
        description="Enables the oneMKL RNG as a required platform. Disables other platforms.",
    )
    variant(
        "curand",
        default=False,
        description="Enables the cuRAND RNG as a required platform. Disables other platforms.",
    )
    conflicts("+onemkl", when="+curand")

    # Depend on a sycl implementation.
    depends_on("c")
    depends_on("cxx")
    depends_on("sycl", type=("build", "link", "run"))
    depends_on("dpcpp", when="+onemkl", type=("build", "link", "run"))
    depends_on("cuda", when="+curand", type=("build", "link", "run"))
    depends_on("googletest@1.10.0:", type=("build", "link", "run"))
    depends_on("cmake@3.24:", type="build")

    # Add the corresponding RNG backend when we detect particular SYCL
    # implementations. The default CMake variables of NESO-RNG-Toolkit will
    # search for these backends and enable them if found in a non-fatal manner.

    # intel-oneapi-mkl depends on tbb as a virtual dependency. As tbb is a
    # virtual dependency spack may satisfy that dependency with a different
    # tbb package other than the intel-oneapi-tbb package. If the
    # intel-oneapi-tbb package isn't used, or a compatible TBB otherwise made
    # available, you may see cmake errors along the lines of unable to find the
    # MKL::MKL_DPCPP target.
    depends_on(
        "intel-oneapi-mkl%intel-oneapi-tbb",
        when="^dpcpp",
        type=("build", "link", "run"),
    )

    depends_on(
        "cuda",
        when="^adaptivecpp compilationflow=cudallvm",
        type=("build", "link", "run"),
    )
    depends_on(
        "cuda",
        when="^adaptivecpp compilationflow=cudanvcxx",
        type=("build", "link", "run"),
    )

    def cmake_args(self):
        args = []

        # If these variants were explicitly specified then we add the CMake
        # flags which make the discovery of the corresponding platform
        # mandatory and disable the other platforms.
        if "+onemkl" in self.spec:
            args.append("-DNESO_RNG_TOOLKIT_REQUIRE_ONEMKL=ON")
            args.append("-DNESO_RNG_TOOLKIT_ENABLE_CURAND=OFF")

        if "+curand" in self.spec:
            args.append("-DNESO_RNG_TOOLKIT_REQUIRE_CURAND=ON")
            args.append("-DNESO_RNG_TOOLKIT_ENABLE_ONEMKL=OFF")

        return args
