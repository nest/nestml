ignore_and_fire
###############


ignore_and_fire - Neuron generating spikes at fixed intervals irrespective of inputs  

Description
+++++++++++

The ``ignore_and_fire`` neuron is a neuron model generating spikes at a predefined ``firing_rate`` with a constant inter-spike interval ("fire"), irrespective of its inputs ("ignore"). In this simplest version of the ``ignore_and_fire`` neuron, the inputs from other neurons or devices are not processed at all (*). The ``ignore_and_fire`` neuron is primarily used for neuronal-network model verification and validation purposes, in particular, to evaluate the correctness and performance of connectivity generation and inter-neuron communication. It permits an easy scaling of the network size and/or connectivity without affecting the output spike statistics. The amount of network traffic is predefined by the user, and therefore fully controllable and predictable, irrespective of the network size and structure. 

To create asynchronous activity for a population of ``ignore_and_fire`` neurons, the firing ``phase``s can be randomly initialised. Note that the firing ``phase`` is a real number, defined as the time to the next spike relative to the firing period.

(*) The model can easily be extended and equipped with any arbitrary input processing (such as calculating input currents with alpha-function shaped PSC kernels or updating the gating variables in the Hodgkin-Huxley model) or (after-) spike generation dynamics to make it more similar and comparable to other non-ignorant neuron models. In such extended ignore_and_fire models, the spike emission process would still be decoupled from the intrinsic neuron dynamics.

Authors
+++++++

Tetzlaff (February 2021; January 2022)




Parameters
++++++++++
.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "firing_rate", "Bq", "10.0Bq", "# firing rate"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "phase", "real", "1.0", "# relative time to next spike (in (0,1])"




Equations
+++++++++





Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `ignore_and_fire <https://github.com/nest/nestml/tree/master/models/neurons/ignore_and_fire.nestml>`_.

Characterisation
++++++++++++++++

.. include:: ignore_and_fire_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.764699