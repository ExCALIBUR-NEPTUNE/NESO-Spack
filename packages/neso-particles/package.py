from spack import *
import os
import shutil


class NesoParticles(CMakePackage):
    """NESO-Particles"""

    homepage = "https://excalibur-neptune.github.io/NESO-Particles/"

    git = "https://github.com/ExCALIBUR-NEPTUNE/NESO-Particles.git"

    version("0.1.0", commit="2e1b1aac6f4f9c22b31787cf300fcc2b4914cbe1", preferred=True)
    version("working", branch="main")
    version("main", branch="main")

    variant("build_tests", default=True, description="Builds the NESO-Particles tests.")
    variant("nvcxx", default=False, description="Builds with CUDA CMake flags.")

    depends_on("mpi", type=("build", "link", "run"))

    # Non-SYCL dependencies
    depends_on("hdf5 +mpi +hl", type=("build", "link", "run"))
    depends_on("cmake@3.21:", type="build")
    depends_on("googletest@1.10.0: +gmock", type=("build", "link", "run"))

    # Depend on a sycl implementation - with workarounds for intel packaging.
    depends_on("sycl", type=("build", "link", "run"))
    depends_on("intel-oneapi-dpl", when="^dpcpp", type="link")
    conflicts("%dpcpp", msg="Use oneapi compilers instead of dpcpp driver.")
    conflicts("^dpcpp", when="%gcc", msg="DPC++ can only be used with Intel oneAPI compilers.")

    def cmake_args(self):
        args = []
        if not "+build_tests" in self.spec:
            args.append("-DENABLE_NESO_PARTICLES_TESTS=off")
        if "+nvcxx" in self.spec:
            args.append("-DNESO_PARTICLES_DEVICE_TYPE=GPU")
            args.append("-DHIPSYCL_TARGETS=cuda-nvcxx")

        return args
