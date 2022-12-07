# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *
import os
import shutil


class Nektar(CMakePackage):
    """Nektar++: Spectral/hp Element Framework"""

    homepage = "https://www.nektar.info/"

    git = "https://gitlab.nektar.info/nektar/nektar.git"

    # 03/09/2022
    version("5.3.0-2e0fb8", commit="2e0fb86da236e7e5a3590fcf5e0f608bd8490945", preferred=True)
    # 12/08/2022 - has fix for external MPI Init/Finalize
    version("5.2.0-f1598d", commit="f1598d5e39f175acf388b90df392f76ff29d7f9d")
    # 27/05/2022
    version("5.2.0-b36964", commit="b36964360503a1a1f7facc3bbe93668ae4474be7", deprecated=True)
    # 22/04/2022
    version("5.2.0-3dbd7f", commit="3dbd7f65724bf4a611c942e1e6b692d20e80ba1e", deprecated=True)
    # 18/02/2022
    version("5.1.1-8715c9", commit="8715c90f900b4f22d36881ad5e3640afa40d5e39", deprecated=True)

    variant("mpi", default=True, description="Builds with mpi support")
    variant("fftw", default=True, description="Builds with fftw support")
    variant("arpack", default=True, description="Builds with arpack support")
    variant("tinyxml", default=True, description="Builds with external tinyxml support")
    variant("hdf5", default=False, description="Builds with hdf5 support (conflicts with builtin?)")
    variant("scotch", default=True, description="Builds with scotch partitioning support")
    variant("demos", default=True, description="Build demonstration codes")
    variant("solvers", default=True, description="Build example solvers")
    variant("python", default=True, description="Enable python support")

    depends_on("cmake@2.8.8:", type="build", when="~hdf5")
    depends_on("cmake@3.2:", type="build", when="+hdf5")

    depends_on("blas")
    depends_on("tinyxml", when="+tinyxml")
    depends_on("lapack")
    # Last version supporting C++11
    depends_on(
        "boost@1.74.0: +thread +iostreams +filesystem +system +program_options +regex +pic +python +numpy",
        when="+python",
    )
    depends_on(
        "boost@1.74.0: +thread +iostreams +filesystem +system +program_options +regex +pic",
        when="~python",
    )
    depends_on("tinyxml", when="platform=darwin")

    depends_on("mpi", when="+mpi", type=("build", "link", "run"))
    depends_on("fftw@3.0: +mpi", when="+mpi+fftw")
    depends_on("fftw@3.0: ~mpi", when="~mpi+fftw")
    depends_on("arpack-ng +mpi", when="+arpack+mpi")
    depends_on("arpack-ng ~mpi", when="+arpack~mpi")
    depends_on("hdf5 +mpi +hl", when="+mpi+hdf5")
    depends_on("scotch ~mpi ~metis", when="~mpi+scotch")
    depends_on("scotch +mpi ~metis", when="+mpi+scotch")
    depends_on("python@3:", when="+python", type=("build", "link", "run"))

    conflicts("+hdf5", when="~mpi", msg="Nektar's hdf5 output is for parallel builds only")

    def cmake_args(self):
        args = []

        def hasfeature(feature):
            return "ON" if feature in self.spec else "OFF"

        args.append("-DNEKTAR_BUILD_DEMOS=%s" % hasfeature("+demos"))
        args.append("-DNEKTAR_BUILD_SOLVERS=%s" % hasfeature("+solvers"))
        args.append("-DNEKTAR_USE_MPI=%s" % hasfeature("+mpi"))
        args.append("-DNEKTAR_USE_FFTW=%s" % hasfeature("+fftw"))
        args.append("-DNEKTAR_USE_ARPACK=%s" % hasfeature("+arpack"))
        args.append("-DNEKTAR_USE_HDF5=%s" % hasfeature("+hdf5"))
        args.append("-DNEKTAR_USE_SCOTCH=%s" % hasfeature("+scotch"))
        args.append("-DNEKTAR_USE_PETSC=OFF")
        args.append("-DNEKTAR_ERROR_ON_WARNINGS=OFF")
        args.append("-DNEKTAR_USE_MKL=%s" % hasfeature("^intel-oneapi-mkl"))
        args.append("-DNEKTAR_USE_OPENBLAS=%s" % hasfeature("^openblas"))
        args.append("-DNEKTAR_BUILD_PYTHON=%s" % hasfeature("+python"))
        args.append("-DNEKTAR_BUILD_UTILITIES=ON")
        args.append("-DNEKTAR_USE_THREAD_SAFETY=ON")
        return args

    def setup_run_environment(self, env):
        env.append_path(
            "CMAKE_PREFIX_PATH",
            os.path.join(self.spec.prefix, os.path.join("lib64", os.path.join("nektar++", "cmake"))),
        )
        env.append_path("PYTHONPATH", os.path.abspath(os.path.join(self.spec.prefix, "build_tree")))

    def setup_dependent_run_environment(self, env, dependent_spec):
        self.setup_run_environment(env)

    def setup_dependent_build_environment(self, env, dependent_spec):
        self.setup_run_environment(env)

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
        super(type(self), self).cmake(spec, prefix)

    def add_files_to_view(self, view, merge_map, skip_if_exists=True):
        super(CMakePackage, self).add_files_to_view(view, merge_map, skip_if_exists)
        path = self.view_destination(view)
        print(path)
        view.link(os.path.join(path, "lib64", "nektar++"), os.path.join(path, "lib", "nektar++"))
