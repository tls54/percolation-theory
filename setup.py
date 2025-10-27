from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import shutil
from pathlib import Path
import pybind11  # Add this import


class BuildExtWithCopy(build_ext):
    """Custom build_ext that copies .so files to Search/ directory."""
    
    def run(self):
        # Run the normal build
        build_ext.run(self)
        
        # Copy the built extension to Search/
        if self.extensions:
            for ext in self.extensions:
                self.copy_extension_to_source(ext)
    
    def copy_extension_to_source(self, ext):
        """Copy built extension from build dir to source dir."""
        build_py = self.get_finalized_command('build_py')
        package_dir = Path('Search')
        
        # Get the built extension path
        fullname = self.get_ext_fullname(ext.name)
        filename = self.get_ext_filename(fullname)
        
        # Source: build/lib.../filename
        src = Path(self.build_lib) / filename
        
        # Destination: Search/filename
        dest = package_dir / Path(filename).name
        
        if src.exists():
            print(f"Copying {src} -> {dest}")
            shutil.copy2(src, dest)
        else:
            print(f"Warning: Built extension not found at {src}")


ext_modules = [
    Extension(
        'percolation_cpp',
        ['cpp/src/bindings.cpp'],
        include_dirs=[
            pybind11.get_include(),  # ← ADD THIS
            'cpp/src',
        ],
        language='c++',
        extra_compile_args=['-std=c++17', '-O3'],
    ),
]

setup(
    name='percolation_cpp',
    version='0.1.0',
    description='Fast C++ percolation algorithms',
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExtWithCopy},
    zip_safe=False,
    python_requires='>=3.9',
)