from spack import *
import os
import shutil


class NesoParticles(CMakePackage):
    """NESO-Particles"""

    homepage = "https://excalibur-neptune.github.io/NESO-Particles/"

    git = "https://github.com/ExCALIBUR-NEPTUNE/NESO-Particles"

    # 22/08/2022
    version("0.0.1-f54dc8", commit="f54dc89c57abb31f4a5b742456d69ec5d69cd330", preferred=True)

    variant("hdf5", default=True, description="Builds with HDF5 support")
    # The intel-oneapi-compilers package is missing the "provide('sycl')" that
    # would enable automatic detection that the package provides sycl.
    variant("intel", default=False, description="Assume an intel toolchain installed with spack.")

    depends_on("mpi", type=("build", "link", "run"))

    # Depend on a sycl implementation - with workarounds for intel packaging.
    depends_on("sycl", type=("build", "link", "run"), when="~intel")
    # depends_on("intel-oneapi-compilers", type=("build", "link", "run"), when="+intel")

    depends_on("hdf5 +mpi +hl", type=("build", "link", "run"), when="+hdf5")
    depends_on("cmake@3.14:", type="build")

    def cmake_args(self):
        args = []
        if "+intel" in self.spec:
            args.append("-DCMAKE_CXX_COMPILER=dpcpp")
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

    @property
    def build_directory(self):
        """Returns the directory to use when building the package

        :return: directory where to build the package
        """
        return self.copied_build_dir

    @property
    def archive_files(self):
        """Files to archive for packages based on CMake"""
        # Overridden as the default tries to archive the CMakeCache.txt file
        # and emits a warning that the file is outside the build stage.
        src_path = os.path.join(self.build_directory, "CMakeCache.txt")
        dst_path = os.path.join(self.stage.path, "CMakeCache.txt")
        shutil.copyfile(src_path, dst_path)
        return [dst_path]

    def cmake(self, spec, prefix):
        self.copied_build_dir = os.path.join(prefix, "build_tree")
        assert os.path.abspath(self.copied_build_dir) == os.path.abspath(os.path.join(self.spec.prefix, "build_tree"))
        src_path = os.path.join(self.stage.path, self.stage.source_path)
        dst_path = self.copied_build_dir
        shutil.copytree(src_path, dst_path)
        CMakePackage.cmake(self, spec, prefix)
