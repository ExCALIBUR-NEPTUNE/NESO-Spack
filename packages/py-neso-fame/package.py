# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class PyNesoFame(PythonPackage):
    """FIXME: Put a proper description of your package here."""

    homepage = "https://github.com/ExCALIBUR-NEPTUNE/NESO-fame"

    # FIXME: Update this URL once a release has been made
    url = "https://github.com/ExCALIBUR-NEPTUNE/NESO-fame/archive/refs/heads/main.zip"
    git = "https://github.com/ExCALIBUR-NEPTUNE/NESO-fame.git"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers = ["github_user1", "github_user2"]

    version("main", branch="main")

    depends_on("python@3.10:", type=("build", "run"))
    depends_on("py-setuptools", type="build")
    depends_on("py-hypnotoad", type=("build", "run"))
    depends_on("nektar+python", type=("build", "run"))
    depends_on("py-click", type=("build", "run"))
    depends_on("py-pytest", type="test")
    depends_on("py-hypothesis", type="test")
