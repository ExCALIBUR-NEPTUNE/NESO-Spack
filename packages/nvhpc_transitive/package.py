from spack import *


def _get_pkg_versions(pkg_name):
    """Get a list of 'safe' (already checksummed) available versions of a Spack package
    Equivalent to 'spack versions <pkg_name>' on the command line"""
    pkg_spec = spack.spec.Spec(pkg_name)
    spack_version = spack.spack_version_info
    if spack_version[1] <= 20:
        pkg_cls = spack.repo.path.get_pkg_class(pkg_name)
    else:
        pkg_cls = spack.repo.PATH.get_pkg_class(pkg_name)
    pkg = pkg_cls(pkg_spec)
    return [vkey.string for vkey in pkg.versions.keys()]


class NvhpcTransitive(Package):
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
