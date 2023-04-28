# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import inspect
from contextlib import contextmanager
from tempfile import TemporaryDirectory
import shutil
import os
import os.path

import llnl.util.filesystem as fs
from spack.error import SpecError
from spack.version import Version

from spack.package import *
import spack.builder
import spack.build_systems.python

class PythonPipBuilder(spack.build_systems.python.PythonPipBuilder):
    """Hack to install Hypnotoad with a recent version of setuptools,
    even though it depends on Numpy which uses an old version."""

    @staticmethod
    @contextmanager
    def temporarily_replace_setuptools(pip, spec, version_requirement=''):
        """Context manager that will temporarily move the installed
        version of setuptools out of the PYTHONPATH, install a different
        version, and then return everything to its original state."""
        with TemporaryDirectory() as dirname:
            setuptools_dir = spec.prefix.lib.join("python{}".format(spec["python"].package.version.up_to(2))).join("site-packages")
            setup_tmp_dir = os.path.join(dirname, 'setuptools')
            shutil.move(setuptools_dir, setup_tmp_dir)
            pip("install", "setuptools" + version_requirement)
            try:
                yield setup_tmp_dir
            finally:
                pip("--no-input", "uninstall", "-y", "setuptools")
                shutil.move(setup_tmp_dir, setuptools_dir)

    def install(self, pkg, spec, prefix):
        pip = inspect.getmodule(pkg).pip
        with self.temporarily_replace_setuptools(pip, spec["py-setuptools"], ">=65"):
            super(PythonPipBuilder, self).install(pkg, spec, prefix)
        if spec.satisfies("~gui"):
            os.remove(self.spec.prefix.bin.join("hypnotoad-gui"))


class PyHypnotoad(PythonPackage):
    """Hypnotoad is the grid generator for BOUT++."""

    homepage = "https://hypnotoad.readthedocs.io/en/latest/"
    pypi = "hypnotoad/hypnotoad-0.5.2.tar.gz"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers = ["github_user1", "github_user2"]

    version("0.5.2", sha256="597177879abff9fb678f376db4053068971c94565c14c06953ccd65773ca30da")

    variant("gui", default=False, description="Install libraries necessary for using the GUI")

    # Should really specify "py-setuptools@65:", but that causes
    # conflicts with Numpy, so working around it
    depends_on("py-setuptools", type="build")
    depends_on("py-wheel@0.29.0:", type="build")
    depends_on("py-versioneer+toml", type="build")

    depends_on("py-boututils@0.1.7:0.1", type=("build", "run"))
    depends_on("py-dill@0.3.0:0.3.4,0.3.5.2:0", type=("build", "run"))
    depends_on("py-func-timeout@4.3.0:4.3", type=("build", "run"))
    depends_on("py-matplotlib@3.2.0:3", type=("build", "run"))
    depends_on("py-netcdf4@1.5.0:1", type=("build", "run"))
    depends_on("py-numpy@1.18.0:1", type=("build", "run"))
    depends_on("py-optionsfactory@1.0.11:1.0", type=("build", "run"))
    depends_on("py-pyyaml@5.1:5", type=("build", "run"))
    depends_on("py-qtpy@1.2.0:1", type=("build", "run"), when="+gui")
    depends_on("py-scipy@1.6.0:1", type=("build", "run"))

    depends_on("py-pytest", type="test")
