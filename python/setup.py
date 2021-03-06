import codecs
import os.path
import platform

from setuptools import Extension
from setuptools import setup
from setuptools.command.build_ext import build_ext


IS_WINDOWS = platform.system() == "Windows"


# Obscure magic required to allow numpy be used as a 'setup_requires'.
# Based on https://stackoverflow.com/questions/19919905
class local_build_ext(build_ext):
    def finalize_options(self):
        build_ext.finalize_options(self)
        import builtins

        # Prevent numpy from thinking it is still in its setup process:
        builtins.__NUMPY_SETUP__ = False
        import numpy

        self.include_dirs.append(numpy.get_include())


libdir = "lib"
kastore_dir = os.path.join(libdir, "subprojects", "kastore")
tsk_source_files = [
    "core.c",
    "tables.c",
    "trees.c",
    "genotypes.c",
    "stats.c",
    "convert.c",
    "haplotype_matching.c",
]
sources = (
    ["_tskitmodule.c"]
    + [os.path.join(libdir, "tskit", f) for f in tsk_source_files]
    + [os.path.join(kastore_dir, "kastore.c")]
)

defines = []
libraries = []
if IS_WINDOWS:
    # Needed for generating UUIDs
    libraries.append("Advapi32")
    defines.append(("WIN32", None))

_tskit_module = Extension(
    "_tskit",
    sources=sources,
    extra_compile_args=["-std=c99"],
    libraries=libraries,
    define_macros=defines,
    # Enable asserts
    undef_macros=["NDEBUG"],
    include_dirs=[libdir, kastore_dir],
)

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

# After exec'ing this file we have tskit_version defined.
tskit_version = None  # Keep PEP8 happy.
version_file = os.path.join("tskit", "_version.py")
with open(version_file) as f:
    exec(f.read())

numpy_ver = "numpy>=1.7"

setup(
    name="tskit",
    description="The tree sequence toolkit.",
    long_description=long_description,
    url="https://github.com/tskit-dev/tskit",
    author="tskit developers",
    version=tskit_version,
    author_email="admin@tskit.dev",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="tree sequence",
    packages=["tskit"],
    include_package_data=True,
    ext_modules=[_tskit_module],
    install_requires=[
        "attrs>=19.2.0",
        "h5py>=2.6.0",
        "jsonschema>=3.0.0",
        numpy_ver,
        "svgwrite>=1.1.10",
    ],
    entry_points={"console_scripts": ["tskit=tskit.cli:tskit_main"]},
    project_urls={
        "Bug Reports": "https://github.com/tskit-dev/tskit/issues",
        "Source": "https://github.com/tskit-dev/tskit",
    },
    setup_requires=[numpy_ver],
    cmdclass={"build_ext": local_build_ext},
    license="MIT",
    platforms=["POSIX", "Windows", "MacOS X"],
)
