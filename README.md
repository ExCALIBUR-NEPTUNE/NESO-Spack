# NESO-Spack

This repository provides Spack packages for NESO and some of its
dependencies. To enable your installation of Spack to use this repo do:

```
git clone git@github.com:ExCALIBUR-NEPTUNE/NESO-spack.git
cd NESO-spack
spack repo add .
```

You can then use `spack install` to build various packages. For
example, you can build Nektar++ using GCC and OpenBLAS by running
```
spack install neso.nektar%gcc ^openblas
```
If instead you want to build it using the Intel oneAPI compilers and
Intel MKL, you can run
```
spack install neso.nektar%oneapi ^intel-oneapi-mkl
```
These installations can coexist side-by-side.

Note that the oneAPI compilers (and Clang, on which they are based)
struggle to compile some dependencies like NumPy and Boost. You may
need to specify those to be built using another compiler, such as the
classic Intel compilers:
```
spack isntall neso.nektar%oneapi ^intel-oneapi-mkl ^py-numpy%intel ^boost%intel
```

For more information on using this Spack repo to develop NESO, see the
[README for that
repository](https://github.com/ExCALIBUR-NEPTUNE/NESO).
