[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/) [![Build Status](https://travis-ci.org/nest/nestml.svg?branch=master)](https://travis-ci.org/nest/nestml)

# NESTML: The NEST Modelling Language

NESTML is a domain-specific language that supports the specification of neuron models in a precise and concise syntax, based on the syntax of Python. Model equations can either be given as a simple string of mathematical notation or as an algorithm written in the built-in procedural language. The equations are analyzed by the associated toolchain, written in Python, to compute an exact solution if possible or use an appropriate numeric solver otherwise.

## Directory structure

`models` - Example neuron models in NESTML format.

`pynestml` - The source code of the PyNESTML toolchain.

`tests` - A collection of tests for testing of the toolchain's behavior.

`doc` - The documentation of the modeling language NESTML as well as processing toolchain PyNESTML.

`extras` - Miscellaneous development tools, editor syntax highlighting rules, etc.

## Installing NESTML

Please note that only Python 3 is supported. The instructions below assume that `python` is aliased to or refers to `python3`, and `pip` to `pip3`.

### Installing the latest release from PyPI

The easiest way to install NESTML is to use the [Python Package Index (PyPI)](https://pypi.org). This requires the Python package management system `pip` to be installed. In Ubuntu, Mint and Debian Linux you can install `pip` as follows:

```
sudo apt install python3-pip
```

NESTML can then be installed into your local user directory via:

```
pip install nestml --user
```

### Installing the latest development version from GitHub

To obtain the latest development version, clone directly from the master branch of the GitHub repository:

```
git clone https://github.com/nest/nestml
```

Install into your local user directory using:

```
cd nestml
python setup.py install --user
```

### Testing

After installation, correct operation can be tested by:

```
python setup.py test
```

## Running NESTML

After the installation, the toolchain can be executed by the following command.
```
nestml ARGUMENTS
```
where arguments are:<a name="table_args"></a>

| Command        | Description |
|---             |---          |
| -h or --help   | Print help message.|
| --input_path   | Path to the source file or directory containing the model.|
| --target_path  | (Optional) Path to target directory where generated code will be written into. Default is `target`, which will be created in the current working directory if it does not yet exist.| 
| --target       | (Optional) The name of the target platform to generate code for. Default is NEST.|
| --logging_level| (Optional) Sets the logging level, i.e., which level of messages should be printed. Default is ERROR, available are [INFO, WARNING, ERROR, NO] |
| --module_name  | (Optional) Sets the name of the module which shall be generated. Default is the name of the directory containing the models. The name has to end in "module". Default is `nestmlmodule`. |
| --store_log    | (Optional) Stores a log.txt containing all messages in JSON notation. Default is OFF.|
| --suffix       | (Optional) A suffix string that will be appended to the name of all generated models.|
| --dev          | (Optional) Enable development mode: code generation is attempted even for models that contain errors, and extra information is rendered in the generated code. Default is OFF.|

Generated artifacts are copied to the selected target directory (default is `target`). In order to install the models into NEST, the following commands have to be executed from within the target directory:

```
cmake -Dwith-nest=<nest_install_dir>/bin/nest-config .
make all
make install
```

where `<nest_install_dir>` is the installation directory of NEST (e.g. `/home/nest/work/nest-install`). Subsequently, the module can either be linked into NEST (see [Writing an extension module](https://nest.github.io/nest-simulator/extension_modules)), or loaded dynamically using the `Install` API function. For example, to dynamically load a module with `module_name` = `nestmlmodule` in PyNEST:

```py
nest.Install("nestmlmodule")
```
PyNESTML is also available as a component and can therefore be used from within other Python tools and scripts. After PyNESTML has been installed, the following modules have to be imported:
```py
from pynestml.frontend.pynestml_frontend import to_nest, install_nest
```
Subsequently, it is possible to call PyNESTML from other Python tools and scripts via:
```py
to_nest(input_path, target_path, logging_level, module_name, store_log, dev)    
```
This operation expects the same set of arguments as in the case of command line invocation. The following default values are used, corresponding to the command line defaults. Possible values for `logging_level` are the same as before ('INFO', 'WARNING', 'ERROR', 'NO'). Note that only the `path` argument is mandatory:

| Argument      | Type    | Default |
|---            |---      | ---     |
| input_path    | string  | _no default_ |
| target_path   | string  | None |
| logging_level | string  | 'ERROR' |
| module_name   | string  | `nestmlmodule` |
| store_log     | boolean | False |
| dev           | boolean | False |

If no errors occur, the output will be generated into the specified target directory. In order to avoid an execution of all required module-installation routines by hand, PyNESTML features a function for an installation of NEST models directly into NEST:
```py
install_nest(models_path, nest_path)
```
Here, `models_path` should be set to the `target` directory of `to_nest()`, and `nest_path` points to the directory where NEST is installed (e.g., `/home/nest/work/nest-install`).

A typical script, therefore, could look like the following. For this example, we assume that the name of the generated module is _nestmlmodule_.
```py
from pynestml.frontend.pynestml_frontend import to_nest, install_nest

to_nest(input_path="/home/nest/work/pynestml/models", target_path="/home/nest/work/pynestml/target")

install_nest("/home/nest/work/pynestml/target", "/home/nest/work/nest-install")

nest.Install("nestmlmodule")
...
nest.Simulate(400.0)
```

## Further reading

For an in-depth introduction to the underlying modeling language NESTML, please refer to the [NESTML language documentation](doc/nestml_language.md).

For those interested in the implementation of PyNESTML or the general structure of a DSL-processing toolchain, please refer to the [PyNESTML documentation](doc/pynestml/index.md).

## Publications

* Inga Blundell, Dimitri Plotnikov, Jochen Martin Eppler and Abigail Morrison (2018) **Automatically selecting a suitable integration scheme for systems of differential equations in neuron models.** Front. Neuroinform. [doi:10.3389/fninf.2018.00050](https://doi.org/10.3389/fninf.2018.00050). Preprint available on [Zenodo](https://zenodo.org/record/1411417).

* Konstantin Perun, Bernhard Rumpe, Dimitri Plotnikov, Guido Trensch, Jochen Martin Eppler, Inga Blundell and Abigail Morrison (2018). **Reengineering NestML with Python and MontiCore** (Version 2.4). Zenodo. [doi:10.5281/zenodo.1319653](http://doi.org/10.5281/zenodo.1319653).

* Dimitri Plotnikov, Bernhard Rumpe, Inga Blundell, Tammo Ippen, Jochen Martin Eppler and Abigail Morrison (2016). **NESTML: a modeling language for spiking neurons.** In Modellierung 2016, March 2-4 2016, Karlsruhe, Germany. 93–108. [doi:10.5281/zenodo.1412345](http://doi.org/10.5281/zenodo.1412345).
