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
    # url = "https://www.nektar.info/src/nektar++-5.2.0.tar.bz2"
    # version("5.1.0", sha256="f5fdb729909e4dcd42cb071f06569634fa87fe90384ba0f2f857a9e0e56b6ac5")
    # version("5.2.0", sha256="991e2c2644bd578de15e854861cab378a32f8ba1104a90faf1aa7d46f86c3e08")
    # version("5.0.0", sha256="5c594453fbfaa433f732a55405da9bba27d4a00c32d7b9d7515767925fb4a818")

    git = "https://gitlab.nektar.info/nektar/nektar.git"

    # 12/08/2022 - has fix for external MPI Init/Finalize
    version("5.2.0-f1598d", commit="f1598d5e39f175acf388b90df392f76ff29d7f9d")
    # 27/05/2022
    version("5.2.0-b36964", commit="b36964360503a1a1f7facc3bbe93668ae4474be7")
    # 22/04/2022
    version("5.2.0-3dbd7f", commit="3dbd7f65724bf4a611c942e1e6b692d20e80ba1e")
    # 18/02/2022
    version("5.1.1-8715c9", commit="8715c90f900b4f22d36881ad5e3640afa40d5e39")

    variant("mpi", default=True, description="Builds with mpi support")
    variant("fftw", default=True, description="Builds with fftw support")
    variant("arpack", default=True, description="Builds with arpack support")
    variant("tinyxml", default=True, description="Builds with external tinyxml support")
    variant("hdf5", default=False, description="Builds with hdf5 support (conflicts with builtin?)")
    variant("scotch", default=True, description="Builds with scotch partitioning support")
    variant("demos", default=True, description="Build demonstration codes")
    variant("solvers", default=True, description="Build example solvers")
    variant("mkl", default=False, description="Enable MKL")
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
        args.append("-DNEKTAR_USE_MKL=%s" % hasfeature("+mkl"))
        args.append("-DNEKTAR_USE_OPENBLAS=%s" % hasfeature("^openblas"))
        args.append("-DNEKTAR_BUILD_PYTHON=%s" % hasfeature("+python"))
        args.append("-DNEKTAR_BUILD_UTILITIES=ON")
        args.append("-DNEKTAR_USE_THREAD_SAFETY=ON")
        return args

    def setup_dependent_build_environment(self, env, dependent_spec):
        env.append_path(
            "CMAKE_PREFIX_PATH",
            os.path.join(self.spec.prefix, os.path.join("lib64", os.path.join("nektar++", "cmake"))),
        )

    @run_after("install")
    def copy_cmake_files(self):
        src_path = os.path.join(self.build_directory, "solvers")
        dst_path = os.path.join(self.spec.prefix, "solvers_objects")
        shutil.copytree(src_path, dst_path)
        if "+python" in self.spec:
            src_path = os.path.join(self.build_directory, "NekPy")
            dst_path = os.path.join(self.spec.prefix, "NekPy")
            shutil.copytree(src_path, dst_path)
            src_path = os.path.join(self.build_directory, "setup.py")
            dst_path = os.path.join(self.spec.prefix, "setup.py")
            shutil.copyfile(src_path, dst_path)
