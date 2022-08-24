# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *
import os
import shutil


class CmakeMovedBuild(CMakePackage):
    """Test cmake package"""

    homepage = ""

    git = "/home/js0259/git-ukaea/cmake_hello_world"

    version("0.0.1", commit="64e75fa0c6b5ac90f6b5c0c532155328ccf59c06")

    @property
    def build_directory(self):
        """Returns the directory to use when building the package

        :return: directory where to build the package
        """
        return self.copied_build_dir

    def cmake(self, spec, prefix):
        self.copied_build_dir = os.path.join(prefix, "build_tree")
        src_path = os.path.join(self.stage.path, self.stage.source_path)
        dst_path = self.copied_build_dir
        shutil.copytree(src_path, dst_path)
        CMakePackage.cmake(self, spec, prefix)


