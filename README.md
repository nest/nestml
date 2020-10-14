[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/) [![Build Status](https://travis-ci.org/nest/nestml.svg?branch=master)](https://travis-ci.org/nest/nestml)

# NESTML: The NEST Modelling Language

NESTML is a domain-specific language that supports the specification of neuron models in a precise and concise syntax, based on the syntax of Python. Model equations can either be given as a simple string of mathematical notation or as an algorithm written in the built-in procedural language. The equations are analyzed by the associated toolchain, written in Python, to compute an exact solution if possible or use an appropriate numeric solver otherwise.

## Documentation

Full documentation can be found at:

<pre><p align="center"><a href="https://nestml.readthedocs.io/">https://nestml.readthedocs.io/</a></p></pre>

## Directory structure

`models` - Example neuron models in NESTML format.

`pynestml` - The source code of the PyNESTML toolchain.

`tests` - A collection of tests for testing of the toolchain's behavior.

`doc` - The documentation of the modeling language NESTML as well as processing toolchain PyNESTML.

`extras` - Miscellaneous development tools, editor syntax highlighting rules, etc.

## License

Copyright (C) 2017 The NEST Initiative

NESTML is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 2 of the License, or (at your option) any later version.

NESTML is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with NESTML. If not, see <http://www.gnu.org/licenses/>.
