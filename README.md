[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/) [![Build Status](https://travis-ci.org/nest/nestml.svg?branch=master)](https://travis-ci.org/kperun/nestml)

# PyNestML - The NEST Modelling Language @Python

NestML is a domain specific language that supports the specification of neuron models in a precise and concise syntax, based on the syntax of Python. Model equations can either be given as a simple string of mathematical notation or as an algorithm written in the built-in procedural language. The equations are analyzed by NESTML to compute an exact solution if possible or use an appropriate numeric solver otherwise.

## Directory structure

`models` - Example neuron models in NestML format.

`pynestml` - The source code of PyNestML.

`tests` - A collection of tests for testing of the toolchains behavior.

`doc` - The documentation of the modeling language NestML as well as processing toolchain PyNestML.

## Installing NESTML

In order to execute the language tool-chain, Python in version 2 or 3 is required. A setup file is provided and can be installed by 
```
python2 setup.py install --user
```
For Python in version 3, respectively:
```
python3 setup.py install --user
```
Correct installation can be tested by 
```
python2 setup.py test
\# respectively python3 setup.py test 
```
In order to ensure correct installation and resolving of dependencies, Python's package manager [pip](https://pip.pypa.io/en/stable/installing/), the distribution tool [setuptools](https://packaging.python.org/tutorials/installing-packages/) as well as the python-dev package are required and should be installed in advance. The setup file additionally installs the following components:

* [SymPy in the version >= 1.1.1](http://www.sympy.org/en/index.html)
* [NumPy in the version >=1.8.2](http://www.numpy.org/)
* [Antlr4 runtime environment in the version >= 4.7](https://github.com/antlr/antlr4/blob/master/doc/python-target.md)

In the case that no 'enum' package is found, additionally, enum34 has to be updated by
```
pip install --upgrade pip enum34
```
All requirements are stored in the requirements.txt and can be installed in one step by pip
```
pip install -r requirements.txt
```

## Running NESTML

After the installation, the toolchain can be executed by the following command.
```
python PyNestML.py ARGUMENTS
```
where arguments are:<a name="table_args"></a>

| Command       | Description |
|---            |---          |
| -h or --help  | Print help message.|
| -path         | Path to the source file or directory containing the model.|
| -target       | (Optional) Path to target directory where models will be generated to. Default is `target`.| 
| -dry          | (Optional) Executes the analysis of the model without generating target code. Default is OFF.|
| -logging_level| (Optional) Sets the logging level, i.e., which level of messages should be printed. Default is ERROR, available are [INFO, WARNING, ERROR, NO] |
| -module_name  | (Optional) Sets the name of the module which shall be generated. Default is the name of the directory containing the models. The name has to end in "module". Default is `nestmlmodule`. |
| -store_log    | (Optional) Stores a log.txt containing all messages in JSON notation. Default is OFF.|
| -dev          | (Optional) Executes the toolchain in the development mode where errors in models are ignored. Default is OFF.|

Generated artifacts are copied to the selected target directory (default is `target`). In order to install the models into NEST, the following commands have to be executed from within the target directory:
```
cmake -Dwith-nest=<nest_install_dir>/bin/nest-config .
make all
make install
```
where `<nest_install_dir>` is the installation directory of NEST (e.g. `/home/nest/work/nest-install`). Subsequently, the module can either be linked into NEST (see [Writing an extension module](https://nest.github.io/nest-simulator/extension_modules)), or loaded dynamically using the `Install` API function. For example, to dynamically load a module with `module_name` = `mymodelsmodule` in PyNEST:
```py
nest.Install("mymodelsmodule")
```

PyNestML is also available as a component and can therefore be used from within other Python tools and scripts. After PyNestML has been installed, the following modules have to be imported:
```py
from pynestml.frontend.pynestml_frontend import to_nest, install_nest
```
Subsequently, it is possible to call PyNestML from other Python tools and scripts via:
```py
to_nest(path, target, dry, logging_level, module_name, store_log, dev)    
```
This operation expects the same set of arguments as in the case of command line invocation. The following default values are used, corresponding to the command line defaults. Possible values for `logging_level` are the same as before ('INFO', 'WARNING', 'ERROR', 'NO'). Note that only the `path` argument is mandatory:

| Argument | Type | Default |
|---       |---   | --- |
| path     | string | _no default_ |
| target   | string | None |
| dry      | boolean | False |
| logging_level | string | 'ERROR' |
| module_name | string | `nestmlmodule` |
| store_log | boolean | False |
| dev | boolean | False |

If no errors occur, the output will be generated into the specified target directory. In order to avoid an execution of all required module-installation routines by hand, PyNestML features a function for an installation of NEST models directly into NEST:
```py
install_nest(models_path, nest_path)
```
Here, `models_path` should be set to the `target` directory of `to_nest()`, and `nest_path` points to the directory where NEST is installed (e.g., `/home/nest/work/nest-install`).

A typical script, therefore, could look like the following. For this example, we assume that the name of the generated module is _nestmlmodule_.
```py
from pynestml.frontend.pynestml_frontend import to_nest, install_nest

to_nest(path="/home/nest/work/pynestml/models", target="/home/nest/work/pynestml/target", dev=True)

install_nest("/home/nest/work/pynestml/target", "/home/nest/work/nest-install")

nest.Install("nestmlmodule")
...
nest.Simulate(400.0)
```

For an in-depth introduction to the underlying modeling language NestML, we refer to the following [introduction](doc/lan/doc.md).
For those interested in the implementation of PyNestML or the general structure of a DSL-processing toolchain, a [documentation](doc/impl/doc.md) of all implemented components is provided. 

## Publications

* Inga Blundell, Dimitri Plotnikov, Jochen Martin Eppler and Abigail Morrison (2018) **Automatically selecting a suitable integration scheme for systems of differential equations in neuron models.** Front. Neuroinform. [doi:10.3389/fninf.2018.00050](https://doi.org/10.3389/fninf.2018.00050). Preprint available on [Zenodo](https://zenodo.org/record/1411417).

* Konstantin Perun, Bernhard Rumpe, Dimitri Plotnikov, Guido Trensch, Jochen Martin Eppler, Inga Blundell and Abigail Morrison (2018). **Reengineering NestML with Python and MontiCore** (Version 2.4). Zenodo. [doi:10.5281/zenodo.1319653](http://doi.org/10.5281/zenodo.1319653).

* Dimitri Plotnikov, Bernhard Rumpe, Inga Blundell, Tammo Ippen, Jochen Martin Eppler and Abigail Morrison (2016). **NESTML: a modeling language for spiking neurons.** In Modellierung 2016, March 2-4 2016, Karlsruhe, Germany. 93–108. [doi:10.5281/zenodo.1412345](http://doi.org/10.5281/zenodo.1412345).
