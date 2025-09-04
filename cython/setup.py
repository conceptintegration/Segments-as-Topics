from distutils.core import Extension, setup
from Cython.Build import cythonize
import numpy

# define an extension that will be cythonized and compiled
ext = Extension(name="angular_distance", sources=["angular_distance.pyx"],
                include_dirs=[numpy.get_include()],
                define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')])
setup(ext_modules=cythonize(ext, language_level = "3"))

