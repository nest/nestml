#
# setup.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
import sys

setup(
    name='PyNESTML',
    version='0.0.2',
    author='kperun',
    description='NESTML is a domain specific language that supports the specification of neuron models in a'
                ' precise and concise syntax, based on the syntax of Python. Model equations can either be given'
                ' as a simple string of mathematical notation or as an algorithm written in the built-in procedural'
                ' language. The equations are analyzed by NESTML to compute an exact solution if possible or use an '
                'appropriate numeric solver otherwise. PyNESTML represents a toolchain migrated from Java to Python.',
    license='GNU General Public License v2.0',
    url='https://github.com/kperun/nestml/tree/PyNestML',
    packages=find_packages(),
    install_requires=['numpy >= 1.8.2',
                      'sympy >= 1.0',
                      ('antlr4-python2-runtime' if sys.version_info.major == 2 else
                       'antlr4-python3-runtime')],
    test_suite='pynestml.src.test.python',
)
