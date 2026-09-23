from spack.package import *


class ProvidesSyclWrapper(Package):
    """Provides the SYCL virtual dependency. This only makes sense if the
    compiler used is a SYCL compiler but for some reason the corresponding
    package for the compiler does not provide the SYCL virtual dependency.

    Users should add
        %%compiler-provides-sycl +enable

    to the spec. The +enable is a default false sticky variant such that Spack
    may not use this package without the user explicitly setting the variant.
    """

    variant(
        "enable",
        default=False,
        description="By specifying +compiler_provides_sycl the user guarantees that the spack cxx compiler is a SYCL compiler.",
        sticky=True,
    )

    provides("sycl", when="+enable")
    depends_on("cxx")
    version("1.0.0")
    has_code = False
    phases = []

    def install(self):
        pass
