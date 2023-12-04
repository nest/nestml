SpiNNaker target
----------------

*NESTML features supported:* :doc:`neurons </nestml_language/neurons_in_nestml>`

Introduction
~~~~~~~~~~~~

SpiNNaker [FB20]_ was first publicly mentioned in 1998. It is a neuromorphic architecture based on ARM microprocessors connected into a network. The project emerged from the research question of efficiently integrating associative memory in Very Large Scale Integration (VLSI) architectures. After some research, it was clear that the architecture would come down to a neuromorphic architecture. Earlier implementations mainly focused on analog implementations of neurons and synapses combined with digital communication, However, Furber's previous involvement with ARM and asynchronous digital circuits led to a design based on ARM microprocessors implementing the model and network details in software. As mentioned in the introduction to neuromorphic computing, handling many communication messages is a challenge. Following the biological example is hard to achieve, as to be generally applicable would mean building a physical connection between each neuron, which apart from spatial problems also hinders scalability. This was previously solved by using a bus system with, compared to biological spikes, short digital messages encoding a unique address of the source neuron as the spike. Because of the short pulse, spikes generated simultaneously can be serialized without breaking the concepts found in nature. This protocol is called Address Event Representation (AER [Mah92]_). Each spike is a broadcast message on the bus, where
each neuron determines if it should receive the spike through the address of the source neuron [Mah92]_.

As this solution uses a single bus, the scalability of the system is dependent on the bus throughput. This let the team around SpiNNaker to switch from a bus system to a packet-switched network, where packets can be routed to specified targets. Instead of being bound to the fixed specification of bus throughput, this now also allows scaling the network capacity by adding more routers. They call this Multicast Packet-Switched AER. With this architecture, they were able to achieve a system with 1 million processors called SpiNNaker1M. All information about SpiNNaker presented in this chapter comes from the book "SpiNNaker: A Spiking Neural Network Architecture" [FB20]_.


Generating code
~~~~~~~~~~~~~~~

1. Build the Apptainer image from https://github.com/nest/nestml/blob/master/extras/spinnaker-apptainer.def

2. Run the Apptainer image:

   .. code-block:: bash

      apptainer shell --overlay ~/spinnaker_overlay.img ~/spinnaker_apptainer.sif

3. Install NESTML in ``$HOME/nestml``.

4. Create the installation directory:

   .. code-block:: bash

      # need to create this directory first, otherwise it gets ignored in the PYTHONPATH!
      mkdir $HOME/nestml/spinnaker-install

5. Run the test

   .. code-block:: bash

      PYTHONPATH=$HOME/nestml/spinnaker-install python3 -m pytest -s --pdb ./tests/spinnaker_tests/test_spinnaker_iaf_psc_exp.py



Further reading
~~~~~~~~~~~~~~~

Levin Schmidt, "Extension of the NEST Modelling Language to the SpiNNaker Architecture". Master's thesis, RWTH Aachen University (2023) :download:`PDF <Schmidt_SpiNNaker_NESTML_Masters_thesis_2023.pdf>`


References
~~~~~~~~~~

.. [Mah92] M. Mahowald. VLSI analogs of neuronal visual processing: a synthesis of form and function. 1992

.. [FB20] S. Furber and P. Bogdan. SpiNNaker: A Spiking Neural Network Architecture. Boston-Delft: now publishers, 2020
