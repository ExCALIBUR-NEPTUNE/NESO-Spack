# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class PyOptionsfactory(PythonPackage):
    """OptionsFactory allows you to define a set of options"""

    homepage = "https://github.com/johnomotani/optionsfactory"
    pypi = "optionsfactory/optionsfactory-1.0.11.tar.gz"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers = ["github_user1", "github_user2"]

    version("1.0.11", sha256="dc5e316b2734ed210bcff333c800ec06d97c7cf75f41d79d7a0a7c6fa608d403")

    variant("yaml", default=False, description="Support loading configurations from YAML")
    
    depends_on("python@3.6:", type=("build", "run"))
    depends_on("py-setuptools", type="build")
    depends_on("py-pyyaml@5.1:", type=("build", "run"))
    depends_on("py-dill@0.3:", type=("test"))
