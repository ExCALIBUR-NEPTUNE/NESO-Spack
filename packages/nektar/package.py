# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Nektar(CMakePackage):
    """Nektar++: Spectral/hp Element Framework"""

    homepage = "https://www.nektar.info/"
    url      = "https://www.nektar.info/src/nektar++-5.2.0.tar.bz2"
    

    version('5.2.0', sha256='3242ac2e14dfa0193bc3141b1eac0177be27d9ba418b764449fa051ed9c3eed0')
    version('5.0.0', sha256='5c594453fbfaa433f732a55405da9bba27d4a00c32d7b9d7515767925fb4a818')

    variant('mpi', default=True, description='Builds with mpi support')
    variant('fftw', default=True, description='Builds with fftw support')
    variant('arpack', default=True, description='Builds with arpack support')
    variant('tinyxml', default=False, description='Builds with external tinyxml support')
    variant('hdf5', default=False, description='Builds with hdf5 support')
    variant('scotch', default=False,
            description='Builds with scotch partitioning support')

    depends_on('cmake@2.8.8:', type='build', when="~hdf5")
    depends_on('cmake@3.2:', type='build', when="+hdf5")

    depends_on('blas')
    depends_on('tinyxml', when="+tinyxml")
    depends_on('lapack')
    depends_on('boost@1.74.0 +iostreams')
    depends_on('tinyxml', when='platform=darwin')

    depends_on('mpi', when='+mpi')
    depends_on('fftw@3.0: +mpi', when="+mpi+fftw")
    depends_on('fftw@3.0: ~mpi', when="~mpi+fftw")
    depends_on('arpack-ng +mpi', when="+arpack+mpi")
    depends_on('arpack-ng ~mpi', when="+arpack~mpi")
    depends_on('hdf5 +mpi +hl', when="+mpi+hdf5")
    depends_on('scotch ~mpi ~metis', when="~mpi+scotch")
    depends_on('scotch +mpi ~metis', when="+mpi+scotch")

    conflicts("+hdf5", when="~mpi",
              msg="Nektar's hdf5 output is for parallel builds only")

    def cmake_args(self):
        args = []

        def hasfeature(feature):
            return 'ON' if feature in self.spec else 'OFF'

        args.append('-DNEKTAR_USE_MPI=%s' % hasfeature('+mpi'))
        args.append('-DNEKTAR_USE_FFTW=%s' % hasfeature('+fftw'))
        args.append('-DNEKTAR_USE_ARPACK=%s' % hasfeature('+arpack'))
        args.append('-DNEKTAR_USE_HDF5=%s' % hasfeature('+hdf5'))
        args.append('-DNEKTAR_USE_SCOTCH=%s' % hasfeature('+scotch'))
        args.append('-DNEKTAR_USE_PETSC=OFF')
        return args
