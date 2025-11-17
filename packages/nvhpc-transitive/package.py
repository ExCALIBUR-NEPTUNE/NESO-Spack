import spack
from spack import *
from spack.package import *


def _get_pkg_versions(pkg_name):
    """Get a list of 'safe' (already checksummed) available versions of a Spack package
    Equivalent to 'spack versions <pkg_name>' on the command line"""
    pkg_spec = spack.spec.Spec(pkg_name)
    spack_version = spack.spack_version_info

    if spack_version[0] < 1 and spack_version[1] <= 20:
        pkg_cls = spack.repo.path.get_pkg_class(pkg_name)
    else:
        pkg_cls = spack.repo.PATH.get_pkg_class(pkg_name)
    pkg = pkg_cls(pkg_spec)
    return [vkey.string for vkey in pkg.versions.keys()]


class NvhpcTransitive(Package):
    """
    The AdaptiveCpp package depends on nvhpc however if the dependency type is
    "build" then nvhpc is loaded at cmake time which breaks the cmake stage of
    AdaptiveCpp as it finds nvhpc components as dependencies. If we set nvhpc
    as a link or run dependency then spack loads nvhpc whenever AdaptiveCpp is
    loaded and now downstream cmake breaks as it finds nvhpc components. If a
    method exists to install nvhpc alongside AdaptiveCpp as a "dependency"
    that is none of the current build, link or run types then this package can
    be removed.

    What this package does is to depend on nvhpc as "build" which ensures that
    nvhpc is installed but not loaded at build time or runtime of AdaptiveCpp.
    The downside is that a "spack gc" call might remove nvhpc as it is could be
    treated as a ephemeral dependency.
    """

    # Make a one-to-one correspondance between nvhpc versions and versions of
    # this package.
    available_versions = _get_pkg_versions("nvhpc")
    for idx, v in enumerate(available_versions):
        version(v)
        version_suffix = "@" + v
        # Not ideal as a spack gc may remove nvhpc but link and run will both
        # add nvhpc to the runtime environment.
        depends_on("nvhpc" + version_suffix, when=version_suffix, type="build")

    # These two lines prevent spack actually trying to install/build this
    # package.
    has_code = False
    phases = []
