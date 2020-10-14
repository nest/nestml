Introduction
------------

The aim of this exercise is to obtain familiarity with NESTML by completing a partial model of the Izhikevich neuron [1]_. In the file `izhikevich_task.nestml`, a subset of the parameters, state equations and update block is implemented. Your task is to complete the model code. For reference, the solution is included as `izhikevich_solution.nestml`.


Start your Python interpreter
-----------------------------

`PYTHONPATH` needs to be set so that PyNEST can be imported (`import nest` in Python). `LD_LIBRARY_PATH` needs to be set to the directory where NESTML will generate the C++ code for the model, and where the dynamic library (`.so`) will be built. I chose `/tmp/nestml-component` here as an example.

Note that on MacOS, `LD_LIBRARY_PATH` is called `DYLD_LIBRARY_PATH`.

.. code-block:: bash

   PYTHONPATH=$PYTHONPATH:/home/johndoe/nest-simulator-build/lib/python3.6/site-packages LD_LIBRARY_PATH=/tmp/nestml-component ipython3


NESTML code generation
----------------------

Assume we have a NESTML input model at `/home/johndoe/nestml-tutorial/izhikevich_solution.nestml`. To generate code, build the module and load the module into the NEST Simulator:

.. code-block:: python

   from pynestml.frontend.pynestml_frontend import to_nest, install_nest
   to_nest(input_path="/home/johndoe/nestml-tutorial/izhikevich_solution.nestml", target_path="/tmp/nestml-component", logging_level="INFO")
   install_nest("/tmp/nestml-component", "/home/johndoe/nest-simulator-build")


Instantiate model in NEST Simulator and run
-------------------------------------------

In the same Python session, continue entering the following code. This performs the instantiation of the model (`nest.Create("izhikevich_tutorial")`), injects a constant current and runs the simulation for 250 ms.

.. code-block:: python

   import nest
   import matplotlib.pyplot as plt

   nest.set_verbosity("M_WARNING")
   nest.ResetKernel()
   nest.Install("nestmlmodule")

   neuron = nest.Create("izhikevich_tutorial")
   voltmeter = nest.Create("voltmeter")

   voltmeter.set({"record_from": ["v"]})
   nest.Connect(voltmeter, neuron)

   cgs = nest.Create('dc_generator')
   cgs.set({"amplitude": 25.})
   nest.Connect(cgs, neuron)

   nest.Simulate(250.)

   plt.plot(voltmeter.get("events")["times"], voltmeter.get("events")["v"])
   plt.show()


References
----------

.. [1] Eugene M. Izhikevich, "Simple Model of Spiking Neurons", IEEE Transactions on Neural Networks, Vol. 14, No. 6, November 2003
