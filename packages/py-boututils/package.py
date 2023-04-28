# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class PyBoututils(PythonPackage):
    """pip-package of what was previously found in
    BOUT-dev/tools/pylib/boututils."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://github.com/boutproject/boututils"
    pypi = "boututils/boututils-0.1.10.tar.gz"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers = ["github_user1", "github_user2"]

    version("0.1.10", sha256="1225a90bd6807508867b1f345d001bf69a36c1f456083e7b618a4238773fc044")

    variant("hdf5", default=False, description="Support for working with HDF5 data")
    variant("mayavi", default=False, description="Support 3D visualisation")

    depends_on("python@3:", type=("build", "run"))
    depends_on("py-setuptools@42:", type="build")
    depends_on("py-setuptools-scm+toml@3.4:", type="build")
    depends_on("py-setuptools-scm-git-archive", type="build")

    depends_on("py-numpy", type=("build", "run"))
    depends_on("py-matplotlib", type=("build", "run"))
    depends_on("py-scipy", type=("build", "run"))
    depends_on("py-netcdf4", type=("build", "run"))
    depends_on("py-importlib-metadata", type=("build", "run"), when="^python@:3.7")
    depends_on("py-h5py", type=("build", "run"), when="+hdf5")
    depends_on("py-mayavi", type=("build", "run"), when="+mayavi")
    depends_on("py-pyqt5", type=("build", "run"), when="+mayavi")
