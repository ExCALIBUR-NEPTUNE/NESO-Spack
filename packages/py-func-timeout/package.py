# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class PyFuncTimeout(PythonPackage):
    """Python module to support running any existing function with a given timeout."""

    homepage = "https://github.com/kata198/func_timeout"
    pypi = "func_timeout/func_timeout-4.3.5.tar.gz"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers = ["github_user1", "github_user2"]

    version("4.3.5", sha256="74cd3c428ec94f4edfba81f9b2f14904846d5ffccc27c92433b8b5939b5575dd")
    depends_on("py-setuptools", type="build")
