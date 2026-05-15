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
    version("main", branch="main", preferred=True)
    version("test", commit="582db42f3f8fdfdee9e0b61cc937b07d65415968")
    version("0.1.0", commit="9fe3d25bd72bab535dba51541a36f1dc14404075")

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
    variant(
        "hiprand",
        default=False,
        description="Enables the hipRAND RNG as a required platform. Disables other platforms.",
    )
    variant(
        "platformsearch",
        default=True,
        description="Explicitly enables searching for platforms which are not C++ stdlib. Disabling this variant will disable searching for an appropriate platform based on SYCL implementation.",
    )
    conflicts("+onemkl", when="+curand")
    conflicts("+onemkl", when="+hiprand")
    conflicts("+curand", when="+hiprand")

    # Depend on a sycl implementation.
    depends_on("c")
    depends_on("cxx")
    depends_on("sycl", type=("build", "link", "run"))
    depends_on("dpcpp", when="+onemkl", type=("build", "link", "run"))
    depends_on("cuda", when="+curand", type=("build", "link", "run"))
    depends_on("hiprand +rocm", when="+hiprand", type=("build", "link", "run"))
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
        when="+platformsearch ^adaptivecpp compilationflow=cudallvm",
        type=("build", "link", "run"),
    )
    depends_on(
        "cuda",
        when="+platformsearch ^adaptivecpp compilationflow=cudanvcxx",
        type=("build", "link", "run"),
    )
    depends_on(
        "cuda",
        when="+platformsearch ^adaptivecpp compilationflow=generic +cuda",
        type=("build", "link", "run"),
    )
    depends_on(
        "hiprand +rocm",
        when="+platformsearch ^adaptivecpp compilationflow=generic +rocm",
        type=("build", "link", "run"),
    )
    depends_on(
        "hiprand +rocm",
        when="+platformsearch ^adaptivecpp compilationflow=hip",
        type=("build", "link", "run"),
    )

    def cmake_args(self):
        args = []

        platformsearch = ("+platformsearch" in self.spec) and not (
            "^adaptivecpp compilationflow=omplibraryonly" in self.spec
            or "^adaptivecpp compilationflow=ompaccelerated" in self.spec
        )

        use_onemkl = ("+onemkl" in self.spec) or (
            platformsearch and ("^dpcpp" in self.spec)
        )

        use_curand = ("+curand" in self.spec) or (
            platformsearch
            and (
                "^adaptivecpp compilationflow=cudanvcxx" in self.spec
                or "^adaptivecpp compilationflow=cudallvm" in self.spec
                or "^adaptivecpp compilationflow=generic +cuda" in self.spec
            )
        )
        use_hiprand = ("+hiprand" in self.spec) or (
            platformsearch
            and (
                "^adaptivecpp compilationflow=generic +rocm" in self.spec
                or "^adaptivecpp compilationflow=hip" in self.spec
            )
        )

        # If these variants were explicitly specified or expected then we add
        # the CMake flags which make the discovery of the corresponding
        # platform mandatory and disable the other platforms.
        if use_onemkl:
            args.append("-DNESO_RNG_TOOLKIT_REQUIRE_ONEMKL=ON")
            args.append("-DNESO_RNG_TOOLKIT_ENABLE_CURAND=OFF")
            args.append("-DNESO_RNG_TOOLKIT_ENABLE_HIPRAND=OFF")

        elif use_curand:
            args.append("-DNESO_RNG_TOOLKIT_ENABLE_ONEMKL=OFF")
            args.append("-DNESO_RNG_TOOLKIT_REQUIRE_CURAND=ON")
            args.append("-DNESO_RNG_TOOLKIT_ENABLE_HIPRAND=OFF")

        elif use_hiprand:
            args.append("-DNESO_RNG_TOOLKIT_ENABLE_ONEMKL=OFF")
            args.append("-DNESO_RNG_TOOLKIT_REQUIRE_CURAND=OFF")
            args.append("-DNESO_RNG_TOOLKIT_ENABLE_HIPRAND=ON")

        if not platformsearch:
            args.append("-DNESO_RNG_TOOLKIT_ENABLE_ONEMKL=OFF")
            args.append("-DNESO_RNG_TOOLKIT_ENABLE_CURAND=OFF")
            args.append("-DNESO_RNG_TOOLKIT_ENABLE_HIPRAND=OFF")

        return args
