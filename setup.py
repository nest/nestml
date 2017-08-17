from setuptools import setup
import sys


setup(
    name='PyNESTML',
    version='0.0.1',
    author='kperun',
    description='NESTML is a domain specific language that supports the specification of neuron models in a'
                ' precise and concise syntax, based on the syntax of Python. Model equations can either be given'
                ' as a simple string of mathematical notation or as an algorithm written in the built-in procedural'
                ' language. The equations are analyzed by NESTML to compute an exact solution if possible or use an '
                'appropriate numeric solver otherwise. PyNESTML represents a toolchain migrated from Java to Python.',
    license='GNU General Public License v2.0',
    url='https://github.com/kperun/nestml/tree/PyNestML',
    packages=['pynestml'],
    install_requires=['numpy >= 1.8.2',
                      'sympy >= 1.0',
                      ('antlr4-python2-runtime' if sys.version_info.major == 2 else
                       'antlr4-python3-runtime')],

)
