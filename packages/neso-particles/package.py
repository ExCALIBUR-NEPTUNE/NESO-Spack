from spack import *
import os
import shutil


class NesoParticles(CMakePackage):
    """NESO-Particles"""

    homepage = "https://excalibur-neptune.github.io/NESO-Particles/"

    git = "/home/js0259/git-ukaea/NESO-Particles"

    # 22/08/2022
    version("0.0.1-f54dc8", commit="10a54a410ddd0eb5d1debc702f415dd798eb89ee", preferred=True)

    variant("hdf5", default=True, description="Builds with HDF5 support.")
    # The intel-oneapi-compilers package is missing the "provide('sycl')" that
    # would enable automatic detection that the package provides sycl.
    variant("intel", default=False, description="Assume an intel toolchain installed with spack.")
    variant("intel", default=True, description="Assume an intel toolchain installed with spack.", when="%oneapi")

    variant(
        'sycl_target', default='none', description='SYCL target selection.',
        values=(
            'hipsycl_omp', 
            'hipsycl_cuda', 
            'hipsycl_nvcxx',
        ), multi=False
    )

    variant("cpu", default=True, description="Build for CPU like architectures.")
    variant("gpu", default=False, description="Build for GPU like architectures.")

    depends_on("mpi", type=("build", "link", "run"))

    # Depend on a sycl implementation - with workarounds for intel packaging.
    depends_on("sycl", type=("build", "link", "run"), when="~intel")

    depends_on("hdf5 +mpi +hl", type=("build", "link", "run"), when="+hdf5")
    depends_on("cmake@3.21:", type="build")
    depends_on("googletest@1.10.0:", type=("build", "link", "run"))

    def cmake_args(self):

        args = []
        if "+intel" in self.spec:
            args.append("-DCMAKE_CXX_COMPILER=dpcpp")

        if self.spec.variants['sycl_target'].value == 'none':
            if "+cpu" in self.spec:
                args.append("-DNESO_PARTICLES_DEVICE_TYPE=CPU")
            elif "+gpu" in self.spec:
                args.append("-DNESO_PARTICLES_DEVICE_TYPE=GPU")
        elif self.spec.variants['sycl_target'].value == 'hipsycl_omp':
            args.append("-DNESO_PARTICLES_DEVICE_TYPE=CPU")
            args.append("-DHIPSYCL_TARGETS=omp")
        elif self.spec.variants['sycl_target'].value == 'hipsycl_cuda':
            args.append("-DNESO_PARTICLES_DEVICE_TYPE=GPU")
            args.append("-DHIPSYCL_TARGETS=cuda")
        elif self.spec.variants['sycl_target'].value == 'hipsycl_nvcxx':
            args.append("-DNESO_PARTICLES_DEVICE_TYPE=GPU")
            args.append("-DHIPSYCL_TARGETS=cuda-nvcxx")

        return args

    def setup_run_environment(self, env):
        env.append_path(
            "CMAKE_PREFIX_PATH",
            os.path.join(self.spec.prefix, os.path.join("build_tree", "cmake")),
        )

    def setup_dependent_run_environment(self, env, dependent_spec):
        self.setup_run_environment(env)

    def setup_build_environment(self, env):
        pass

