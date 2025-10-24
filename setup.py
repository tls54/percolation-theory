from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import pybind11

class get_pybind_include:
    def __str__(self):
        return pybind11.get_include()

class BuildExtInPlace(build_ext):
    """Build extension directly in the Search/ folder"""
    def build_extension(self, ext):
        # Build normally first
        build_ext.build_extension(self, ext)
        
        # Move to Search/ folder
        build_lib = self.build_lib
        fullname = self.get_ext_fullname(ext.name)
        modpath = fullname.split('.')
        filename = self.get_ext_filename(fullname)
        
        # Source location (default build)
        src = os.path.join(build_lib, filename)
        if not os.path.exists(src):
            # If --inplace, it's in project root
            src = self.get_ext_fullpath(ext.name)
        
        # Destination in Search/
        dest = os.path.join('Search', os.path.basename(filename))
        
        # Move (not copy) to Search/
        if os.path.exists(src) and src != dest:
            os.makedirs('Search', exist_ok=True)
            if os.path.exists(dest):
                os.remove(dest)
            os.rename(src, dest)
            print(f"Moved {src} -> {dest}")

# Compiler args based on platform
extra_compile_args = ['-std=c++17', '-O3']
extra_link_args = []

if sys.platform == 'darwin':  # macOSpython 
    extra_link_args = ['-undefined', 'dynamic_lookup']

ext_modules = [
    Extension(
        'percolation_cpp',
        ['cpp/src/bindings.cpp'],
        include_dirs=[
            get_pybind_include(),
            'cpp/src',
        ],
        language='c++',
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
]

setup(
    name='percolation_cpp',
    version='0.1.0',
    description='Fast C++ percolation algorithms',
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExtInPlace},
    zip_safe=False,
    python_requires='>=3.7',
)
