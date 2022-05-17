# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *
import os


class Nektar(CMakePackage):
    """Nektar++: Spectral/hp Element Framework"""

    homepage = "https://www.nektar.info/"
    url = "https://www.nektar.info/src/nektar++-5.2.0.tar.bz2"

    version("5.2.0", sha256="f273a45cc2cde24b6f2c8efd89448c677a2ee300819f6c4e975446508f4281ba")
    version("5.0.0", sha256="5c594453fbfaa433f732a55405da9bba27d4a00c32d7b9d7515767925fb4a818")

    variant("mpi", default=True, description="Builds with mpi support")
    variant("fftw", default=True, description="Builds with fftw support")
    variant("arpack", default=True, description="Builds with arpack support")
    variant("tinyxml", default=True, description="Builds with external tinyxml support")
    variant("hdf5", default=False, description="Builds with hdf5 support (conflicts with builtin?)")
    variant("scotch", default=True, description="Builds with scotch partitioning support")
    variant("demos", default=True, description="Build demonstration codes")
    variant("solvers", default=True, description="Build example solvers")

    depends_on("cmake@2.8.8:", type="build", when="~hdf5")
    depends_on("cmake@3.2:", type="build", when="+hdf5")

    depends_on("blas")
    depends_on("tinyxml", when="+tinyxml")
    depends_on("lapack")
    depends_on("boost@1.74.0 +iostreams")
    depends_on("tinyxml", when="platform=darwin")

    depends_on("mpi", when="+mpi")
    depends_on("fftw@3.0: +mpi", when="+mpi+fftw")
    depends_on("fftw@3.0: ~mpi", when="~mpi+fftw")
    depends_on("arpack-ng +mpi", when="+arpack+mpi")
    depends_on("arpack-ng ~mpi", when="+arpack~mpi")
    depends_on("hdf5 +mpi +hl", when="+mpi+hdf5")
    depends_on("scotch ~mpi ~metis", when="~mpi+scotch")
    depends_on("scotch +mpi ~metis", when="+mpi+scotch")

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
        return args

    def setup_run_environment(self, env):
        env.append_path(
            "CMAKE_PREFIX_PATH",
            os.path.join(self.spec.prefix, os.path.join("lib64", os.path.join("nektar++", "cmake"))),
        )

    def setup_dependent_run_environment(self, env, dependent_spec):
        self.setup_run_environment(env)
