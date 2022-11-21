from os import environ
from spack.package import *
from spack.error import SpecError
from warnings import warn


class NesoParticles(CMakePackage):
    """
    Framework for particle data existing on an unstructured meshes with domain
    decomposed parallelisation.
    """

    homepage = "https://github.com/ExCALIBUR-NEPTUNE"

    git = "https://github.com/ExCALIBUR-NEPTUNE/NESO-Particles"

    maintainers = ["jwscook", "will-saunders-ukaea", "cmacmackin"]

    version("0.0.1-346756", commit="346756144fa893903bdb064597b6fc39dab5d39c", preferred=True)

    variant("build_tests", default=False, description="Builds the tests otherwise only the headers are installed.")
    
    # If the tests are not built, i.e. header only, then we do not install
    # dependencies as the dependencies should be on the software that uses this
    # header only library (as this makes a choice of sycl/mpi implementation
    # which is not required when installing just the headers).

    # Some SYCL packages require a specific run-time environment to be set
    depends_on("mpi", type=("build", "link", "run"), when="+build_tests")
    depends_on("sycl", type=("build", "link"), when="+build_tests")
    depends_on("intel-oneapi-dpl", when="+build_tests ^dpcpp", type="link")
    depends_on("cmake@3.21:", type="build")
    depends_on("googletest", type="link", when="+build_tests")
    depends_on("hdf5", when="+build_tests", type="link")

    conflicts("%dpcpp", msg="Use oneapi compilers instead of dpcpp driver.")
    # This should really be set in the MKL package itself...
    conflicts(
        "^intel-oneapi-mkl@2022.2", when="%oneapi@:2022.1", msg="Use the same version of MKL and OneAPI compilers."
    )
    conflicts("^dpcpp", when="%gcc", msg="DPC++ can only be used with Intel oneAPI compilers.")

    def cmake_args(self):
        args = [
            self.define("ENABLE_NESO_PARTICLES_TESTS", "+build_tests" in self.spec),
        ]

        if "+build_tests" in self.spec and "intel" in self.spec["mpi"].name:
            if "I_MPI_FABRICS" not in environ:
                warn(
                    "The intel mpi specific environment variable, I_MPI_FABRICS, has not been set and an intel-MPI build will fail. If you are developing on an unmanaged-HPC machine, i.e. locally on your workstation, a sensible default `export I_MPI_FABRICS=shm`. Information can be found on the intel documentation pages https://tinyurl.com/33w8x8wp.",
                    UserWarning,
                    stacklevel=1,
                )
        for depspec in self.spec.dependencies():
            for dep in depspec.dependents():
                if "sycl" in dep:
                    if "SYCL_DEVICE_FILTER" not in environ:
                        warn(
                            "The environment variable SYCL_DEVICE_FILTER is not set and the code may not run as intended in this environment. A sensible default for running on the cpu is `export SYCL_DEVICE_FILTER=host`. For more information please see e.g. https://tinyurl.com/y37672as.",
                            UserWarning,
                            stacklevel=1,
                        )

                    break

        return args
