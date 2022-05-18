# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import json
import os
import platform
import re

import llnl.util.tty as tty
from llnl.util.filesystem import get_filetype, path_contains_subdirectory
from llnl.util.lang import match_predicate

from spack import *
from spack.util.environment import is_system_path
from spack.util.prefix import Prefix


class Stdpython(AutotoolsPackage):
    """The Python programming language."""

    homepage = "https://www.python.org/"
    url      = "https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz"
    list_url = "https://www.python.org/ftp/python/"
    list_depth = 1

    maintainers = ['wrs20',]

    version('3.9.7',  sha256='a838d3f9360d157040142b715db34f0218e535333696a5569dc6f854604eb9d1')
    version('3.9.6',  sha256='d0a35182e19e416fc8eae25a3dcd4d02d4997333e4ad1f2eee6010aadc3fe866')
    version('3.9.5',  sha256='e0fbd5b6e1ee242524430dee3c91baf4cbbaba4a72dd1674b90fda87b713c7ab')
    version('3.9.4',  sha256='66c4de16daa74a825cf9da9ddae1fe020b72c3854b73b1762011cc33f9e4592f')
    version('3.9.2',  sha256='7899e8a6f7946748830d66739f2d8f2b30214dad956e56b9ba216b3de5581519')
    version('3.9.1',  sha256='29cb91ba038346da0bd9ab84a0a55a845d872c341a4da6879f462e94c741f117')
    version('3.9.0',  sha256='df796b2dc8ef085edae2597a41c1c0a63625ebd92487adaef2fed22b567873e8')
    version('3.8.12', sha256='316aa33f3b7707d041e73f246efedb297a70898c4b91f127f66dc8d80c596f1a', preferred=True)
    version('3.8.11', sha256='b77464ea80cec14581b86aeb7fb2ff02830e0abc7bcdc752b7b4bdfcd8f3e393')
    version('3.8.10', sha256='b37ac74d2cbad2590e7cd0dd2b3826c29afe89a734090a87bf8c03c45066cb65')
    version('3.8.9',  sha256='9779ec1df000bf86914cdd40860b88da56c1e61db59d37784beca14a259ac9e9')
    version('3.8.8',  sha256='76c0763f048e4f9b861d24da76b7dd5c7a3ba7ec086f40caedeea359263276f7')
    version('3.8.7',  sha256='20e5a04262f0af2eb9c19240d7ec368f385788bba2d8dfba7e74b20bab4d2bac')
    version('3.8.6',  sha256='313562ee9986dc369cd678011bdfd9800ef62fbf7b1496228a18f86b36428c21')
    version('3.8.5',  sha256='015115023c382eb6ab83d512762fe3c5502fa0c6c52ffebc4831c4e1a06ffc49')
    version('3.8.4',  sha256='32c4d9817ef11793da4d0d95b3191c4db81d2e45544614e8449255ca9ae3cc18')
    version('3.8.3',  sha256='6af6d4d2e010f9655518d0fc6738c7ff7069f10a4d2fbd55509e467f092a8b90')
    version('3.8.2',  sha256='e634a7a74776c2b89516b2e013dda1728c89c8149b9863b8cea21946daf9d561')
    version('3.8.1',  sha256='c7cfa39a43b994621b245e029769e9126caa2a93571cee2e743b213cceac35fb')
    version('3.8.0',  sha256='f1069ad3cae8e7ec467aa98a6565a62a48ef196cb8f1455a245a08db5e1792df')


    extendable = True

    # Variants to avoid cyclical dependencies for concretizer
    variant('libxml2', default=True,
            description='Use a gettext library build with libxml2')

    variant(
        'debug', default=False,
        description="debug build with extra checks (this is high overhead)"
    )

    # --enable-shared is known to cause problems for some users on macOS
    # This is a problem for Python 2.7 only, not Python3
    # See http://bugs.python.org/issue29846
    variant('shared', default=True,
            description='Enable shared libraries')
    # From https://docs.python.org/2/c-api/unicode.html: Python's default
    # builds use a 16-bit type for Py_UNICODE and store Unicode values
    # internally as UCS2. It is also possible to build a UCS4 version of Python
    # (most recent Linux distributions come with UCS4 builds of Python).  These
    # builds then use a 32-bit type for Py_UNICODE and store Unicode data
    # internally as UCS4. Note that UCS2 and UCS4 Python builds are not binary
    # compatible.
    variant('ucs4', default=False,
            description='Enable UCS4 (wide) unicode strings')
    variant('pic', default=True,
            description='Produce position-independent code (for shared libs)')
    variant(
        'optimizations',
        default=False,
        description='Enable expensive build-time optimizations, if available'
    )
    # See https://legacy.python.org/dev/peps/pep-0394/
    variant('pythoncmd', default=True,
            description="Symlink 'python3' executable to 'python' "
            "(not PEP 394 compliant)")

    # Optional Python modules
    variant('readline', default=True,  description='Build readline module')
    variant('ssl',      default=True,  description='Build ssl module')
    variant('sqlite3',  default=True,  description='Build sqlite3 module')
    variant('dbm',      default=True,  description='Build dbm module')
    variant('nis',      default=False, description='Build nis module')
    variant('zlib',     default=True,  description='Build zlib module')
    variant('bz2',      default=True,  description='Build bz2 module')
    variant('lzma',     default=True,  description='Build lzma module')
    variant('pyexpat',  default=True,  description='Build pyexpat module')
    variant('ctypes',   default=True,  description='Build ctypes module')
    variant('tkinter',  default=False, description='Build tkinter module')
    variant('uuid',     default=True,  description='Build uuid module')
    variant('tix',      default=False, description='Build Tix module')

    depends_on('pkgconfig@0.9.0:', type='build')
    depends_on('gettext +libxml2', when='+libxml2')
    depends_on('gettext ~libxml2', when='~libxml2')

    # Optional dependencies
    # See detect_modules() in setup.py for details
    depends_on('readline', when='+readline')
    depends_on('ncurses', when='+readline')
    depends_on('openssl', when='+ssl')
    # https://raw.githubusercontent.com/python/cpython/84471935ed2f62b8c5758fd544c7d37076fe0fa5/Misc/NEWS
    # https://docs.python.org/3.5/whatsnew/changelog.html#python-3-5-4rc1
    depends_on('openssl@:1.0.2z', when='@:2.7.13,3.0.0:3.5.2+ssl')
    depends_on('openssl@1.0.2:', when='@3.7:+ssl')  # https://docs.python.org/3/whatsnew/3.7.html#build-changes
    depends_on('openssl@1.1.1:', when='@3.10:+ssl')  # https://docs.python.org/3.10/whatsnew/3.10.html#build-changes
    depends_on('sqlite@3.0.8:', when='@:3.9+sqlite3')
    depends_on('sqlite@3.7.15:', when='@3.10:+sqlite3')  # https://docs.python.org/3.10/whatsnew/3.10.html#build-changes
    depends_on('gdbm', when='+dbm')  # alternatively ndbm or berkeley-db
    depends_on('libnsl', when='+nis')
    depends_on('zlib@1.1.3:', when='+zlib')
    depends_on('bzip2', when='+bz2')
    depends_on('xz', when='@3.3:+lzma')
    depends_on('expat', when='+pyexpat')
    depends_on('libffi', when='+ctypes')
    depends_on('tk', when='+tkinter')
    depends_on('tcl', when='+tkinter')
    depends_on('uuid', when='+uuid')
    depends_on('tix', when='+tix')


    patch('tkinter.patch', when='@:2.8,3.3:3.7 platform=darwin')
    # Patch the setup script to deny that tcl/x11 exists rather than allowing
    # autodetection of (possibly broken) system components
    patch('tkinter-3.8.patch', when='@3.8: ~tkinter')

    # Ensure that distutils chooses correct compiler option for RPATH on cray:
    patch('cray-rpath-2.3.patch', when='@2.3:3.0.1 platform=cray')
    patch('cray-rpath-3.1.patch', when='@3.1:3  platform=cray')

    # Ensure that distutils chooses correct compiler option for RPATH on fj:
    patch('fj-rpath-2.3.patch', when='@2.3:3.0.1 %fj')
    patch('fj-rpath-3.1.patch', when='@3.1:3  %fj')

    # Fixes build with the Intel compilers
    # https://github.com/python/cpython/pull/16717
    patch('intel-3.6.7.patch', when='@3.6.7:3.6.8,3.7.1:3.7.5 %intel')

    # CPython tries to build an Objective-C file with GCC's C frontend
    # https://github.com/spack/spack/pull/16222
    # https://github.com/python/cpython/pull/13306
    conflicts('%gcc platform=darwin',
              msg='CPython does not compile with GCC on macOS yet, use clang. '
                  'See: https://github.com/python/cpython/pull/13306')
    # For more information refer to this bug report:
    # https://bugs.python.org/issue29712
    conflicts(
        '@:2.8 +shared',
        when='+optimizations',
        msg='+optimizations is incompatible with +shared in python@2.X'
    )
    conflicts('+tix', when='~tkinter',
              msg='python+tix requires python+tix+tkinter')

    conflicts('%nvhpc')

    # Used to cache various attributes that are expensive to compute
    _config_vars = {}

    # An in-source build with --enable-optimizations fails for python@3.X
    build_directory = 'spack-build'

    executables = [r'^python[\d.]*[mw]?$']

    @classmethod
    def determine_version(cls, exe):
        # Newer versions of Python support `--version`,
        # but older versions only support `-V`
        # Python 2 sends to STDERR, while Python 3 sends to STDOUT
        # Output looks like:
        #   Python 3.7.7
        output = Executable(exe)('-V', output=str, error=str)
        match = re.search(r'Python\s+(\S+)', output)
        return match.group(1) if match else None

    @classmethod
    def determine_variants(cls, exes, version_str):
        python = Executable(exes[0])

        variants = ''
        for module in ['readline', 'sqlite3', 'dbm', 'nis',
                       'zlib', 'bz2', 'lzma', 'ctypes', 'uuid']:
            try:
                python('-c', 'import ' + module, error=os.devnull)
                variants += '+' + module
            except ProcessError:
                variants += '~' + module

        # Some variants enable multiple modules
        try:
            python('-c', 'import ssl', error=os.devnull)
            python('-c', 'import hashlib', error=os.devnull)
            variants += '+ssl'
        except ProcessError:
            variants += '~ssl'

        try:
            python('-c', 'import xml.parsers.expat', error=os.devnull)
            python('-c', 'import xml.etree.ElementTree', error=os.devnull)
            variants += '+pyexpat'
        except ProcessError:
            variants += '~pyexpat'

        # Some modules changed names in Python 3
        if Version(version_str) >= Version('3'):
            try:
                python('-c', 'import tkinter', error=os.devnull)
                variants += '+tkinter'
            except ProcessError:
                variants += '~tkinter'

            try:
                python('-c', 'import tkinter.tix', error=os.devnull)
                variants += '+tix'
            except ProcessError:
                variants += '~tix'
        else:
            try:
                python('-c', 'import Tkinter', error=os.devnull)
                variants += '+tkinter'
            except ProcessError:
                variants += '~tkinter'

            try:
                python('-c', 'import Tix', error=os.devnull)
                variants += '+tix'
            except ProcessError:
                variants += '~tix'

        return variants

    def url_for_version(self, version):
        url = "https://www.python.org/ftp/python/{0}/Python-{1}.tgz"
        return url.format(re.split('[a-z]', str(version))[0], version)

    # TODO: Ideally, these patches would be applied as separate '@run_before'
    # functions enabled via '@when', but these two decorators don't work
    # when used together. See: https://github.com/spack/spack/issues/12736
    def patch(self):
        # NOTE: Python's default installation procedure makes it possible for a
        # user's local configurations to change the Spack installation.  In
        # order to prevent this behavior for a full installation, we must
        # modify the installation script so that it ignores user files.
        if self.spec.satisfies('@2.7:2.8,3.4:'):
            ff = FileFilter('Makefile.pre.in')
            ff.filter(
                r'^(.*)setup\.py(.*)((build)|(install))(.*)$',
                r'\1setup.py\2 --no-user-cfg \3\6'
            )

        # NOTE: Older versions of Python do not support the '--with-openssl'
        # configuration option, so the installation's module setup file needs
        # to be modified directly in order to point to the correct SSL path.
        # See: https://stackoverflow.com/a/5939170
        if self.spec.satisfies('@:3.6+ssl'):
            ff = FileFilter(join_path('Modules', 'Setup.dist'))
            ff.filter(r'^#(((SSL=)|(_ssl))(.*))$', r'\1')
            ff.filter(r'^#((.*)(\$\(SSL\))(.*))$', r'\1')
            ff.filter(
                r'^SSL=(.*)$',
                r'SSL={0}'.format(self.spec['openssl'].prefix)
            )
        # Because Python uses compiler system paths during install, it's
        # possible to pick up a system OpenSSL when building 'python~ssl'.
        # To avoid this scenario, we disable the 'ssl' module with patching.
        elif self.spec.satisfies('@:3.6~ssl'):
            ff = FileFilter('setup.py')
            ff.filter(
                r'^(\s+(ssl_((incs)|(libs)))\s+=\s+)(.*)$',
                r'\1 None and \6'
            )
            ff.filter(
                r'^(\s+(opensslv_h)\s+=\s+)(.*)$',
                r'\1 None and \3'
            )

    def setup_build_environment(self, env):
        spec = self.spec

        # TODO: The '--no-user-cfg' option for Python installation is only in
        # Python v2.7 and v3.4+ (see https://bugs.python.org/issue1180) and
        # adding support for ignoring user configuration will require
        # significant changes to this package for other Python versions.
        if not spec.satisfies('@2.7:2.8,3.4:'):
            tty.warn(('Python v{0} may not install properly if Python '
                      'user configurations are present.').format(self.version))

        # TODO: Python has incomplete support for Python modules with mixed
        # C/C++ source, and patches are required to enable building for these
        # modules. All Python versions without a viable patch are installed
        # with a warning message about this potentially erroneous behavior.
        if not spec.satisfies('@2.7.8:2.7.18,3.6.8,3.7.2:'):
            tty.warn(('Python v{0} does not have the C++ "distutils" patch; '
                      'errors may occur when installing Python modules w/ '
                      'mixed C/C++ source files.').format(self.version))

        # Need this to allow python build to find the Python installation.
        env.set('MACOSX_DEPLOYMENT_TARGET', platform.mac_ver()[0])

        env.unset('PYTHONPATH')
        env.unset('PYTHONHOME')

    def flag_handler(self, name, flags):
        # python 3.8 requires -fwrapv when compiled with intel
        if self.spec.satisfies('@3.8: %intel'):
            if name == 'cflags':
                flags.append('-fwrapv')

        # allow flags to be passed through compiler wrapper
        return (flags, None, None)

    def configure_args(self):
        spec = self.spec
        config_args = []
        cflags = []

        # setup.py needs to be able to read the CPPFLAGS and LDFLAGS
        # as it scans for the library and headers to build
        link_deps = spec.dependencies('link')

        if link_deps:
            # Header files are often included assuming they reside in a
            # subdirectory of prefix.include, e.g. #include <openssl/ssl.h>,
            # which is why we don't use HeaderList here. The header files of
            # libffi reside in prefix.lib but the configure script of Python
            # finds them using pkg-config.
            cppflags = ' '.join('-I' + spec[dep.name].prefix.include
                                for dep in link_deps)

            # Currently, the only way to get SpecBuildInterface wrappers of the
            # dependencies (which we need to get their 'libs') is to get them
            # using spec.__getitem__.
            ldflags = ' '.join(spec[dep.name].libs.search_flags
                               for dep in link_deps)

            config_args.extend(['CPPFLAGS=' + cppflags, 'LDFLAGS=' + ldflags])

        # https://docs.python.org/3/whatsnew/3.7.html#build-changes
        if spec.satisfies('@:3.6'):
            config_args.append('--with-threads')

        if spec.satisfies('@2.7.13:2.8,3.5.3:', strict=True) \
                and '+optimizations' in spec:
            config_args.append('--enable-optimizations')

        if spec.satisfies('%gcc platform=darwin'):
            config_args.append('--disable-toolbox-glue')

        if spec.satisfies('%intel', strict=True) and \
                spec.satisfies('@2.7.12:2.8,3.5.2:3.7', strict=True):
            config_args.append('--with-icc={0}'.format(spack_cc))

        if '+debug' in spec:
            config_args.append('--with-pydebug')
        else:
            config_args.append('--without-pydebug')

        if '+shared' in spec:
            config_args.append('--enable-shared')
        else:
            config_args.append('--disable-shared')

        if '+ucs4' in spec:
            if spec.satisfies('@:2.7'):
                config_args.append('--enable-unicode=ucs4')
            elif spec.satisfies('@3.0:3.2'):
                config_args.append('--with-wide-unicode')
            elif spec.satisfies('@3.3:'):
                # https://docs.python.org/3.3/whatsnew/3.3.html#functionality
                raise ValueError(
                    '+ucs4 variant not compatible with Python 3.3 and beyond')

        config_args.append('--with-ensurepip=install')

        if '+pic' in spec:
            cflags.append(self.compiler.cc_pic_flag)

        if '+ssl' in spec:
            if spec.satisfies('@3.7:'):
                config_args.append('--with-openssl={0}'.format(
                    spec['openssl'].prefix))

        if '+dbm' in spec:
            # Default order is ndbm:gdbm:bdb
            config_args.append('--with-dbmliborder=gdbm:bdb:ndbm')
        else:
            config_args.append('--with-dbmliborder=')

        if '+pyexpat' in spec:
            config_args.append('--with-system-expat')
        else:
            config_args.append('--without-system-expat')

        if '+ctypes' in spec:
            config_args.append('--with-system-ffi')
        else:
            config_args.append('--without-system-ffi')

        if '+tkinter' in spec:
            config_args.extend([
                '--with-tcltk-includes=-I{0} -I{1}'.format(
                    spec['tcl'].prefix.include, spec['tk'].prefix.include),
                '--with-tcltk-libs={0} {1}'.format(
                    spec['tcl'].libs.ld_flags, spec['tk'].libs.ld_flags)
            ])

        # https://docs.python.org/3.8/library/sqlite3.html#f1
        if spec.satisfies('@3.2: +sqlite3'):
            config_args.append('--enable-loadable-sqlite-extensions')

        if spec.satisfies('%oneapi'):
            cflags.append('-fp-model=strict')

        if cflags:
            config_args.append('CFLAGS={0}'.format(' '.join(cflags)))

        return config_args

    @run_after('install')
    def filter_compilers(self):
        """Run after install to tell the configuration files and Makefiles
        to use the compilers that Spack built the package with.

        If this isn't done, they'll have CC and CXX set to Spack's generic
        cc and c++. We want them to be bound to whatever compiler
        they were built with."""

        kwargs = {'ignore_absent': True, 'backup': False, 'string': True}

        filenames = [
            self.get_sysconfigdata_name(), self.config_vars['makefile_filename']
        ]

        filter_file(spack_cc,  self.compiler.cc,  *filenames, **kwargs)
        if spack_cxx and self.compiler.cxx:
            filter_file(spack_cxx, self.compiler.cxx, *filenames, **kwargs)

    @run_after('install')
    def symlink(self):
        spec = self.spec
        prefix = self.prefix

        # TODO:
        # On OpenSuse 13, python uses <prefix>/lib64/python2.7/lib-dynload/*.so
        # instead of <prefix>/lib/python2.7/lib-dynload/*.so. Oddly enough the
        # result is that Python can not find modules like cPickle. A workaround
        # for now is to symlink to `lib`:
        src = os.path.join(prefix.lib64,
                           'python{0}'.format(self.version.up_to(2)),
                           'lib-dynload')
        dst = os.path.join(prefix.lib,
                           'python{0}'.format(self.version.up_to(2)),
                           'lib-dynload')
        if os.path.isdir(src) and not os.path.isdir(dst):
            mkdirp(dst)
            for f in os.listdir(src):
                os.symlink(os.path.join(src, f),
                           os.path.join(dst, f))

        if spec.satisfies('@3:') and spec.satisfies('+pythoncmd'):
            os.symlink(os.path.join(prefix.bin, 'python3'),
                       os.path.join(prefix.bin, 'python'))
            os.symlink(os.path.join(prefix.bin, 'python3-config'),
                       os.path.join(prefix.bin, 'python-config'))

    @run_after('install')
    def install_python_gdb(self):
        # https://devguide.python.org/gdb/
        src = os.path.join('Tools', 'gdb', 'libpython.py')
        if os.path.exists(src):
            install(src, self.command.path + '-gdb.py')

    @run_after('install')
    @on_package_attributes(run_tests=True)
    def import_tests(self):
        """Test that basic Python functionality works."""

        spec = self.spec

        with working_dir('spack-test', create=True):
            # Ensure that readline module works
            if '+readline' in spec:
                self.command('-c', 'import readline')

            # Ensure that ssl module works
            if '+ssl' in spec:
                self.command('-c', 'import ssl')
                self.command('-c', 'import hashlib')

            # Ensure that sqlite3 module works
            if '+sqlite3' in spec:
                self.command('-c', 'import sqlite3')

            # Ensure that dbm module works
            if '+dbm' in spec:
                self.command('-c', 'import dbm')

            # Ensure that nis module works
            if '+nis' in spec:
                self.command('-c', 'import nis')

            # Ensure that zlib module works
            if '+zlib' in spec:
                self.command('-c', 'import zlib')

            # Ensure that bz2 module works
            if '+bz2' in spec:
                self.command('-c', 'import bz2')

            # Ensure that lzma module works
            if spec.satisfies('@3.3:'):
                if '+lzma' in spec:
                    self.command('-c', 'import lzma')

            # Ensure that pyexpat module works
            if '+pyexpat' in spec:
                self.command('-c', 'import xml.parsers.expat')
                self.command('-c', 'import xml.etree.ElementTree')

            # Ensure that ctypes module works
            if '+ctypes' in spec:
                self.command('-c', 'import ctypes')

            # Ensure that tkinter module works
            # https://wiki.python.org/moin/TkInter
            if '+tkinter' in spec:
                # Only works if ForwardX11Trusted is enabled, i.e. `ssh -Y`
                if 'DISPLAY' in env:
                    if spec.satisfies('@3:'):
                        self.command('-c', 'import tkinter; tkinter._test()')
                    else:
                        self.command('-c', 'import Tkinter; Tkinter._test()')
                else:
                    if spec.satisfies('@3:'):
                        self.command('-c', 'import tkinter')
                    else:
                        self.command('-c', 'import Tkinter')

            # Ensure that uuid module works
            if '+uuid' in spec:
                self.command('-c', 'import uuid')

            # Ensure that tix module works
            if '+tix' in spec:
                if spec.satisfies('@3:'):
                    self.command('-c', 'import tkinter.tix')
                else:
                    self.command('-c', 'import Tix')

    # ========================================================================
    # Set up environment to make install easy for python extensions.
    # ========================================================================

    @property
    def command(self):
        """Returns the Python command, which may vary depending
        on the version of Python and how it was installed.

        In general, Python 2 comes with ``python`` and ``python2`` commands,
        while Python 3 only comes with a ``python3`` command. However, some
        package managers will symlink ``python`` to ``python3``, while others
        may contain ``python3.6``, ``python3.5``, and ``python3.4`` in the
        same directory.

        Returns:
            Executable: the Python command
        """
        # We need to be careful here. If the user is using an externally
        # installed python, several different commands could be located
        # in the same directory. Be as specific as possible. Search for:
        #
        # * python3.6
        # * python3
        # * python
        #
        # in that order if using python@3.6.5, for example.
        version = self.spec.version
        for ver in [version.up_to(2), version.up_to(1), '']:
            path = os.path.join(self.prefix.bin, 'python{0}'.format(ver))
            if os.path.exists(path):
                return Executable(path)
        else:
            msg = 'Unable to locate {0} command in {1}'
            raise RuntimeError(msg.format(self.name, self.prefix.bin))

    def print_string(self, string):
        """Returns the appropriate print string depending on the
        version of Python.

        Examples:

        * Python 2

          .. code-block:: python

             >>> self.print_string('sys.prefix')
             'print sys.prefix'

        * Python 3

          .. code-block:: python

             >>> self.print_string('sys.prefix')
             'print(sys.prefix)'
        """
        if self.spec.satisfies('@:2'):
            return 'print {0}'.format(string)
        else:
            return 'print({0})'.format(string)

    @property
    def config_vars(self):
        """Return a set of variable definitions associated with a Python installation.

        Wrapper around various ``distutils.sysconfig`` functions.

        Returns:
            dict: variable definitions
        """
        # TODO: distutils is deprecated in Python 3.10 and will be removed in
        # Python 3.12, find a different way to access this information.
        # Also, calling the python executable disallows us from cross-compiling,
        # so we want to try to avoid that if possible.
        cmd = """
import json
from distutils.sysconfig import (
    get_config_vars,
    get_config_h_filename,
    get_makefile_filename,
    get_python_inc,
    get_python_lib,
)

config = get_config_vars()
config['config_h_filename'] = get_config_h_filename()
config['makefile_filename'] = get_makefile_filename()
config['python_inc'] = {}
config['python_lib'] = {}

for plat_specific in [True, False]:
    plat_key = str(plat_specific).lower()
    config['python_inc'][plat_key] = get_python_inc(plat_specific, prefix='')
    config['python_lib'][plat_key] = {}
    for standard_lib in [True, False]:
        lib_key = str(standard_lib).lower()
        config['python_lib'][plat_key][lib_key] = get_python_lib(
            plat_specific, standard_lib, prefix=''
        )

%s
""" % self.print_string("json.dumps(config)")

        dag_hash = self.spec.dag_hash()
        if dag_hash not in self._config_vars:
            try:
                config = json.loads(self.command('-c', cmd, output=str))
            except (ProcessError, RuntimeError):
                config = {}
            self._config_vars[dag_hash] = config
        return self._config_vars[dag_hash]

    def get_sysconfigdata_name(self):
        """Return the full path name of the sysconfigdata file."""

        libdest = self.config_vars['LIBDEST']

        filename = '_sysconfigdata.py'
        if self.spec.satisfies('@3.6:'):
            # Python 3.6.0 renamed the sys config file
            cmd = 'from sysconfig import _get_sysconfigdata_name; '
            cmd += self.print_string('_get_sysconfigdata_name()')
            filename = self.command('-c', cmd, output=str).strip()
            filename += '.py'

        return join_path(libdest, filename)

    @property
    def home(self):
        """Most of the time, ``PYTHONHOME`` is simply
        ``spec['python'].prefix``. However, if the user is using an
        externally installed python, it may be symlinked. For example,
        Homebrew installs python in ``/usr/local/Cellar/python/2.7.12_2``
        and symlinks it to ``/usr/local``. Users may not know the actual
        installation directory and add ``/usr/local`` to their
        ``packages.yaml`` unknowingly. Query the python executable to
        determine exactly where it is installed. Fall back on
        ``spec['python'].prefix`` if that doesn't work."""

        if 'prefix' in self.config_vars:
            prefix = self.config_vars['prefix']
        else:
            prefix = self.prefix
        return Prefix(prefix)

    @property
    def libs(self):
        # Spack installs libraries into lib, except on openSUSE where it
        # installs them into lib64. If the user is using an externally
        # installed package, it may be in either lib or lib64, so we need
        # to ask Python where its LIBDIR is.
        libdir = self.config_vars['LIBDIR']

        # In Ubuntu 16.04.6 and python 2.7.12 from the system, lib could be
        # in LBPL
        # https://mail.python.org/pipermail/python-dev/2013-April/125733.html
        libpl = self.config_vars['LIBPL']

        # The system Python installation on macOS and Homebrew installations
        # install libraries into a Frameworks directory
        frameworkprefix = self.config_vars['PYTHONFRAMEWORKPREFIX']

        # Get the active Xcode environment's Framework location.
        macos_developerdir = os.environ.get('DEVELOPER_DIR')
        if macos_developerdir and os.path.exists(macos_developerdir):
            macos_developerdir = os.path.join(
                macos_developerdir, 'Library', 'Frameworks')
        else:
            macos_developerdir = ''

        if '+shared' in self.spec:
            ldlibrary = self.config_vars['LDLIBRARY']

            if os.path.exists(os.path.join(libdir, ldlibrary)):
                return LibraryList(os.path.join(libdir, ldlibrary))
            elif os.path.exists(os.path.join(libpl, ldlibrary)):
                return LibraryList(os.path.join(libpl, ldlibrary))
            elif os.path.exists(os.path.join(frameworkprefix, ldlibrary)):
                return LibraryList(os.path.join(frameworkprefix, ldlibrary))
            elif macos_developerdir and \
                    os.path.exists(os.path.join(macos_developerdir, ldlibrary)):
                return LibraryList(os.path.join(macos_developerdir, ldlibrary))
            else:
                msg = 'Unable to locate {0} libraries in {1}'
                raise RuntimeError(msg.format(ldlibrary, libdir))
        else:
            library = self.config_vars['LIBRARY']

            if os.path.exists(os.path.join(libdir, library)):
                return LibraryList(os.path.join(libdir, library))
            elif os.path.exists(os.path.join(frameworkprefix, library)):
                return LibraryList(os.path.join(frameworkprefix, library))
            else:
                msg = 'Unable to locate {0} libraries in {1}'
                raise RuntimeError(msg.format(library, libdir))

    @property
    def headers(self):
        if 'config_h_filename' in self.config_vars:
            config_h = self.config_vars['config_h_filename']

            if not os.path.exists(config_h):
                includepy = self.config_vars['INCLUDEPY']
                msg = 'Unable to locate {0} headers in {1}'
                raise RuntimeError(msg.format(self.name, includepy))

            headers = HeaderList(config_h)
        else:
            headers = find_headers(
                'pyconfig', self.prefix.include, recursive=True)
            config_h = headers[0]

        headers.directories = [os.path.dirname(config_h)]
        return headers

    @property
    def python_include_dir(self):
        """Directory for the include files.

        On most systems, and for Spack-installed Python, this will look like:

            ``include/pythonX.Y``

        However, some systems append a ``m`` to the end of this path.

        Returns:
            str: include files directory
        """
        try:
            return self.config_vars['python_inc']['false']
        except KeyError:
            return os.path.join('include', 'python{0}'.format(self.version.up_to(2)))

    @property
    def python_lib_dir(self):
        """Directory for the standard library.

        On most systems, and for Spack-installed Python, this will look like:

            ``lib/pythonX.Y``

        On RHEL/CentOS/Fedora, when using the system Python, this will look like:

            ``lib64/pythonX.Y``

        On Debian/Ubuntu, when using the system Python, this will look like:

            ``lib/pythonX``

        Returns:
            str: standard library directory
        """
        try:
            return self.config_vars['python_lib']['false']['true']
        except KeyError:
            return os.path.join('lib', 'python{0}'.format(self.version.up_to(2)))

    @property
    def site_packages_dir(self):
        """Directory where third-party extensions should be installed.

        On most systems, and for Spack-installed Python, this will look like:

            ``lib/pythonX.Y/site-packages``

        On RHEL/CentOS/Fedora, when using the system Python, this will look like:

            ``lib64/pythonX.Y/site-packages``

        On Debian/Ubuntu, when using the system Python, this will look like:

            ``lib/pythonX/dist-packages``

        Returns:
            str: site-packages directory
        """
        try:
            return self.config_vars['python_lib']['true']['false']
        except KeyError:
            return self.default_site_packages_dir

    @property
    def default_site_packages_dir(self):
        python_dir = 'python{0}'.format(self.version.up_to(2))
        return os.path.join('lib', python_dir, 'site-packages')

    @property
    def easy_install_file(self):
        return join_path(self.site_packages_dir, "easy-install.pth")

    def setup_run_environment(self, env):
        env.prepend_path('CPATH', os.pathsep.join(
            self.spec['stdpython'].headers.directories))

    def setup_dependent_build_environment(self, env, dependent_spec):
        """Set PYTHONPATH to include the site-packages directory for the
        extension and any other python extensions it depends on.
        """
        # If we set PYTHONHOME, we must also ensure that the corresponding
        # python is found in the build environment. This to prevent cases
        # where a system provided python is run against the standard libraries
        # of a Spack built python. See issue #7128
        env.set('PYTHONHOME', self.home)

        path = os.path.dirname(self.command.path)
        if not is_system_path(path):
            env.prepend_path('PATH', path)

        for d in dependent_spec.traverse(deptype=('build', 'run', 'test'), root=True):
            if d.package.extends(self.spec):
                env.prepend_path('PYTHONPATH', join_path(
                    d.prefix, self.site_packages_dir))

        # We need to make sure that the extensions are compiled and linked with
        # the Spack wrapper. Paths to the executables that are used for these
        # operations are normally taken from the sysconfigdata file, which we
        # modify after the installation (see method filter compilers). The
        # modified file contains paths to the real compilers, not the wrappers.
        # The values in the file, however, can be overridden with environment
        # variables. The first variable, CC (CXX), which is used for
        # compilation, is set by Spack for the dependent package by default.
        # That is not 100% correct because the value for CC (CXX) in the
        # sysconfigdata file often contains additional compiler flags (e.g.
        # -pthread), which we lose by simply setting CC (CXX) to the path to the
        # Spack wrapper. Moreover, the user might try to build an extension with
        # a compiler that is different from the one that was used to build
        # Python itself, which might have unexpected side effects. However, the
        # experience shows that none of the above is a real issue and we will
        # not try to change the default behaviour. Given that, we will simply
        # try to modify LDSHARED (LDCXXSHARED), the second variable, which is
        # used for linking, in a consistent manner.

        for compile_var, link_var in [('CC', 'LDSHARED'),
                                      ('CXX', 'LDCXXSHARED')]:
            # First, we get the values from the sysconfigdata:
            config_compile = self.config_vars[compile_var]
            config_link = self.config_vars[link_var]

            # The dependent environment will have the compilation command set to
            # the following:
            new_compile = join_path(
                spack.paths.build_env_path,
                dependent_spec.package.compiler.link_paths[compile_var.lower()])

            # Normally, the link command starts with the compilation command:
            if config_link.startswith(config_compile):
                new_link = new_compile + config_link[len(config_compile):]
            else:
                # Otherwise, we try to replace the compiler command if it
                # appears "in the middle" of the link command; to avoid
                # mistaking some substring of a path for the compiler (e.g. to
                # avoid replacing "gcc" in "-L/path/to/gcc/"), we require that
                # the compiler command be surrounded by spaces. Note this may
                # leave "config_link" unchanged if the compilation command does
                # not appear in the link command at all, for example if "ld" is
                # invoked directly (no change would be required in that case
                # because Spack arranges for the Spack ld wrapper to be the
                # first instance of "ld" in PATH).
                new_link = config_link.replace(" {0} ".format(config_compile),
                                               " {0} ".format(new_compile))

            # There is logic in the sysconfig module that is sensitive to the
            # fact that LDSHARED is set in the environment, therefore we export
            # the variable only if the new value is different from what we got
            # from the sysconfigdata file:
            if config_link != new_link:
                env.set(link_var, new_link)

    def setup_dependent_run_environment(self, env, dependent_spec):
        """Set PYTHONPATH to include the site-packages directory for the
        extension and any other python extensions it depends on.
        """
        for d in dependent_spec.traverse(deptype=('run'), root=True):
            if d.package.extends(self.spec):
                env.prepend_path('PYTHONPATH', join_path(
                    d.prefix, self.site_packages_dir))

    def setup_dependent_package(self, module, dependent_spec):
        """Called before python modules' install() methods."""

        module.python = self.command
        module.setup_py = Executable(
            self.command.path + ' setup.py --no-user-cfg')

        # Add variables for lib/pythonX.Y and lib/pythonX.Y/site-packages dirs.
        module.python_lib_dir = join_path(dependent_spec.prefix,
                                          self.python_lib_dir)
        module.python_include_dir = join_path(dependent_spec.prefix,
                                              self.python_include_dir)
        module.site_packages_dir = join_path(dependent_spec.prefix,
                                             self.site_packages_dir)

        self.spec.home = self.home

        # Make the site packages directory for extensions
        if dependent_spec.package.is_extension:
            mkdirp(module.site_packages_dir)

    # ========================================================================
    # Handle specifics of activating and deactivating python modules.
    # ========================================================================

    def python_ignore(self, ext_pkg, args):
        """Add some ignore files to activate/deactivate args."""
        ignore_arg = args.get('ignore', lambda f: False)

        # Always ignore easy-install.pth, as it needs to be merged.
        patterns = [r'(site|dist)-packages/easy-install\.pth$']

        # Ignore pieces of setuptools installed by other packages.
        # Must include directory name or it will remove all site*.py files.
        if ext_pkg.name != 'py-setuptools':
            patterns.extend([
                r'bin/easy_install[^/]*$',
                r'(site|dist)-packages/setuptools[^/]*\.egg$',
                r'(site|dist)-packages/setuptools\.pth$',
                r'(site|dist)-packages/site[^/]*\.pyc?$',
                r'(site|dist)-packages/__pycache__/site[^/]*\.pyc?$'
            ])
        if ext_pkg.name != 'py-pygments':
            patterns.append(r'bin/pygmentize$')
        if ext_pkg.name != 'py-numpy':
            patterns.append(r'bin/f2py[0-9.]*$')

        return match_predicate(ignore_arg, patterns)

    def write_easy_install_pth(self, exts, prefix=None):
        if not prefix:
            prefix = self.prefix

        paths = []
        unique_paths = set()

        for ext in sorted(exts.values()):
            easy_pth = join_path(ext.prefix, self.easy_install_file)

            if not os.path.isfile(easy_pth):
                continue

            with open(easy_pth) as f:
                for line in f:
                    line = line.rstrip()

                    # Skip lines matching these criteria
                    if not line:
                        continue
                    if re.search(r'^(import|#)', line):
                        continue
                    if (ext.name != 'py-setuptools' and
                            re.search(r'setuptools.*egg$', line)):
                        continue

                    if line not in unique_paths:
                        unique_paths.add(line)
                        paths.append(line)

        main_pth = join_path(prefix, self.easy_install_file)

        if not paths:
            if os.path.isfile(main_pth):
                os.remove(main_pth)

        else:
            with open(main_pth, 'w') as f:
                f.write("import sys; sys.__plen = len(sys.path)\n")
                for path in paths:
                    f.write("{0}\n".format(path))
                f.write("import sys; new=sys.path[sys.__plen:]; "
                        "del sys.path[sys.__plen:]; "
                        "p=getattr(sys,'__egginsert',0); "
                        "sys.path[p:p]=new; "
                        "sys.__egginsert = p+len(new)\n")

    def activate(self, ext_pkg, view, **args):
        ignore = self.python_ignore(ext_pkg, args)
        args.update(ignore=ignore)

        super(Python, self).activate(ext_pkg, view, **args)

        extensions_layout = view.extensions_layout
        exts = extensions_layout.extension_map(self.spec)
        exts[ext_pkg.name] = ext_pkg.spec

        self.write_easy_install_pth(exts, prefix=view.get_projection_for_spec(
            self.spec
        ))

    def deactivate(self, ext_pkg, view, **args):
        args.update(ignore=self.python_ignore(ext_pkg, args))

        super(Python, self).deactivate(ext_pkg, view, **args)

        extensions_layout = view.extensions_layout
        exts = extensions_layout.extension_map(self.spec)
        # Make deactivate idempotent
        if ext_pkg.name in exts:
            del exts[ext_pkg.name]
            self.write_easy_install_pth(exts,
                                        prefix=view.get_projection_for_spec(
                                            self.spec
                                        ))

    def add_files_to_view(self, view, merge_map):
        bin_dir = self.spec.prefix.bin
        for src, dst in merge_map.items():
            if not path_contains_subdirectory(src, bin_dir):
                view.link(src, dst, spec=self.spec)
            elif not os.path.islink(src):
                copy(src, dst)
                if 'script' in get_filetype(src):
                    filter_file(
                        self.spec.prefix,
                        os.path.abspath(
                            view.get_projection_for_spec(self.spec)
                        ),
                        dst,
                        backup=False
                    )
            else:
                # orig_link_target = os.path.realpath(src) is insufficient when
                # the spack install tree is located at a symlink or a
                # descendent of a symlink. What we need here is the real
                # relative path from the python prefix to src
                # TODO: generalize this logic in the link_tree object
                #    add a method to resolve a link relative to the link_tree
                #    object root.
                realpath_src = os.path.realpath(src)
                realpath_prefix = os.path.realpath(self.spec.prefix)
                realpath_rel = os.path.relpath(realpath_src, realpath_prefix)
                orig_link_target = os.path.join(self.spec.prefix, realpath_rel)

                new_link_target = os.path.abspath(merge_map[orig_link_target])
                view.link(new_link_target, dst, spec=self.spec)

    def remove_files_from_view(self, view, merge_map):
        bin_dir = self.spec.prefix.bin
        for src, dst in merge_map.items():
            if not path_contains_subdirectory(src, bin_dir):
                view.remove_file(src, dst)
            else:
                os.remove(dst)

    def test(self):
        # do not use self.command because we are also testing the run env
        exe = self.spec['python'].command.name

        # test hello world
        msg = 'hello world!'
        reason = 'test: running {0}'.format(msg)
        options = ['-c', 'print("{0}")'.format(msg)]
        self.run_test(exe, options=options, expected=[msg], installed=True,
                      purpose=reason)

        # checks import works and executable comes from the spec prefix
        reason = 'test: checking import and executable'
        print_str = self.print_string('sys.executable')
        options = ['-c', 'import sys; {0}'.format(print_str)]
        self.run_test(exe, options=options, expected=[self.spec.prefix],
                      installed=True, purpose=reason)
