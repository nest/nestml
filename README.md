# NESTML - The NEST Modelling Language

NESTML is a domain specific language that supports the specification of neuron models
in a precise and concise syntax, based on the syntax of Python. Model equations
can either be given as a simple string of mathematical notation or as an algorithm written
in the built-in procedural language. The equations are analyzed by NESTML to compute
an exact solution if possible or use an appropriate numeric solver otherwise.

## Directory structure

`docker` - A docker containers with the complete NESTML software pipeline installed. Once based on the latest release of NESTML. One that builds the latest development version of NESTML.

`models` - Example neuron models in NESTML format

`src` - The source code of NESTML

## Docker
The docker files can be find in the `docker` folder.

For the usage:
Docker must be installed on the machine. See the follwing resource for the installation instructions https://docs.docker.com/engine/installation
Clone the github repository locally. Switch to the docker-folder in the nestml repository.

```
sh nestml_docker.sh provision
```
If everything goes well, then command 'docker images' container should list a 'nestml_release' container.

Currently, the container is built in the way, that is automatically processes a volume that is mounted at start up. E.g. a NESTML model (https://github.com/nest/nestml/blob/master/models/iaf_cond_alpha_implicit.nestml) can be placed into a folder called 'testing' in the home-folder. Then, the following command will execute model analysis and codegeneration for NEST target (currently, only the NEST master is supported, for earlier version use releases prio 0.1.0):
```
sh nestml_docker.sh run ~/testing
```

It creates a subfolder 'build' in the 'testing' folder that contains the generated code. Per default, the module for the generated stuff is called 'testing', e.g. the name of the input folder. In order to integrate the model into nest, use the following commands (assumption, you switched to the 'testing/result'):
```
cmake -Dwith-nest=${NEST_INSTALL_DIR}/bin/nest-config .
make install
```
Again, if everything goes well, you can use the generated module with neuron models in NEST and PyNEST Scripts. E.g.
```
nest.Install("testing")
neuron=nest.Create ("iaf_cond_alpha_implicit")
```
