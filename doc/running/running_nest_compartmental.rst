NEST Simulator compartmental target
###################################

Generate code for neuron models with complex dendritic structure.

Introduction
------------

NEST Simulator implements compartmental neuron models. The structure of the neuron -- soma, dendrites, axon -- is user-defined at runtime by adding compartments through ``nest.SetStatus()``. Each compartment can be assigned receptors, also through ``nest.SetStatus()``.

The default model is passive, but sodium and potassium currents can be added by passing non-zero conductances ``g_Na`` and ``g_K`` with the parameter dictionary when adding compartments. Receptors can be AMPA and/or NMDA (excitatory), and GABA (inhibitory). Ion channel and receptor currents to the compartments can be customized through NESTML.

For usage information and more details, see the NEST Simulator documentation on compartmental models at https://nest-simulator.readthedocs.io/en/stable/models/cm_default.html.


Writing a compartmental NESTML model
------------------------------------

Defining the membrane potential variable
----------------------------------------

One variable in the model represents the local membrane potential in a compartment. By default, it is called ``v_comp``. (This name is defined in the compartmental code generator options as the ``compartmental_variable_name`` option.). This variable needs to be defined as a state in any compartmental model to be referenced in the equations describing channels and synapses.

.. code-block:: nestml
    
   model <neuron_name>:
       state:
           v_comp real = 0   # rhs value is irrelevant


Channel description
-------------------

Next, define one or more channels. An ion-channel is described in the following way:

.. code-block:: nestml
    
   model <neuron_name>:
        equations:
            inline <current_equation_name> real = \
                <some equation based on state variables, parameters, membrane potential and other equation names> \
                @mechanism::channel

This equation is meant to describe the contribution to the compartmental current of the described ion-channel. It can reference states of which the evolution is described by an ODE, parameters, the membrane potential and the name of other equations. The latter should be used to describe interactions between different mechanisms.

The explicit ``@mechanism::<type>`` descriptor has been added which we thought enhances overview over the NESTML code for the user but also makes the code-generation a bit better organised.

As an example for a HH-type channel:

.. code-block:: nestml
    
   model <neuron_name>:
       parameters:
          gbar_Ca_HVA real = 0.00
          e_Ca_HVA real = 50.00

       state:
          v_comp real = 0.00

          h_Ca_HVA real = 0.69823671
          m_Ca_HVA real = 0.00000918

       equations:
          inline Ca_HVA real = gbar_Ca_HVA * (h_Ca_HVA*m_Ca_HVA**2) * (e_Ca_HVA - v_comp) @mechanism::channel
          m_Ca_HVA' = ( m_inf_Ca_HVA(v_comp) - m_Ca_HVA ) / (tau_m_Ca_HVA(v_comp)*1s)
          h_Ca_HVA' = ( h_inf_Ca_HVA(v_comp) - h_Ca_HVA ) / (tau_h_Ca_HVA(v_comp)*1s)

       function h_inf_Ca_HVA (v_comp real) real:
          ...

       function tau_h_Ca_HVA (v_comp real) real:
          ...

       function m_inf_Ca_HVA (v_comp real) real:
          ...

       function tau_m_Ca_HVA (v_comp real) real:
          ...

All of the currents within a compartment (marked by ``@mechanism::channel``) are added up within a compartment.

For a complete example, please see `cm_default.nestml <https://github.com/nest/nestml/blob/master/tests/nest_compartmental_tests/resources/concmech.nestml>`_ and its associated unit test, `test__compartmental_model.py <https://github.com/nest/nestml/blob/master/tests/nest_compartmental_tests/test__concmech_model.py>`_.


Concentration description
-------------------------

The concentration-model description looks very similar:

.. code-block:: nestml
    
   model <neuron_name>:
       equations:
           <some_state_variable>' = <ODE right-hand-side for some_state_variable> @mechanism::concentration

As an example a description of a calcium concentration model where we pretend that we have the Ca_HVA and the Ca_LVAst ion-channels defined:

.. code-block:: nestml

    model <neuron_name>:
        state:
            c_Ca real = 0.0001

        parameters:
            gamma_Ca real = 0.04627
            tau_Ca real = 605.03
            inf_Ca real = 0.0001

        equations:
            c_Ca' = (inf_Ca - c_Ca) / (tau_Ca*1s) + (gamma_Ca * (Ca_HVA + Ca_LVAst)) / 1s @mechanism::concentration

The only difference here is that the equation that is marked with the ``@mechanism::concentration`` descriptor is not an inline equation but an ODE. This is because in case of the ion-channel what we want to simulate is the current which relies on the evolution of some state variables like gating variables in case of the HH-models, and the compartment voltage. The concentration though can be more simply described by an evolving state directly.

For a complete example, please see `concmech.nestml <https://github.com/nest/nestml/blob/master/tests/nest_compartmental_tests/resources/concmech.nestml>`_ and its associated unit test, `test__concmech_model.py <https://github.com/nest/nestml/blob/master/tests/nest_compartmental_tests/test__concmech_model.py>`_.

Synapse description
-------------------

Here synapse models are based on convolutions over a buffer of incoming spikes. This means that the equation for the
current-contribution must contain a convolve() call and a description of the kernel used for that convolution is needed.
The descriptor for synapses is ``@mechanism::receptor``.

.. code-block:: nestml

    model <neuron_name>:
        equations:
            inline <current_equation_name> real = \
                <some equation based on state variables, parameters, membrane potential and other equation names \
                and MUST contain at least one convolve(<kernel_name>, <spike_name>) call> \
                @mechanism::receptor

            # kernel(s) to be passed to the convolve call(s):
            kernel <kernel_name> = <some kernel description>

        input:
            <spike_name> <- spike

For a complete example, please see `concmech.nestml <https://github.com/nest/nestml/blob/master/tests/nest_compartmental_tests/resources/concmech.nestml>`_ and its associated unit test, `test__concmech_model.py <https://github.com/nest/nestml/blob/master/tests/nest_compartmental_tests/test__concmech_model.py>`_.

Continuous input description
----------------------------

The continuous inputs are defined by an inline with the descriptor @mechanism::continuous_input. This inline needs to
include one input of type continuous and may include any states, parameters and functions.

.. code-block:: nestml

    model <neuron_name>:
            equations:
                inline <current_equation_name> real = \
                    <some equation based on state variables, parameters, membrane potential and other equation names \
                    and MUST contain at least one reference to a continuous input port like <continuous_name>> \
                    @mechanism::continuous_input

            input:
                <continuous_name> real <- continuous

For a complete example, please see `continuous_test.nestml <https://github.com/nest/nestml/blob/master/tests/nest_compartmental_tests/resources/continuous_test.nestml>`_ and its associated unit test, `test__continuous_input.py <https://github.com/nest/nestml/blob/master/tests/nest_compartmental_tests/test__continuous_input.py>`_.

Mechanism interdependence
-------------------------

Above examples of explicit interdependence inbetween concentration and channel models where already described. Note that it is not necessary to describe the basic interaction inherent through the contribution to the overall current of the compartment. During a simulation step all currents of channels and synapses are added up and contribute to the change of the membrane potential (v_comp) in the next timestep. Thereby one must only express a dependence explicitly if the mechanism depends on the activity of a specific channel- or synapse-type amongst multiple in a given compartment or some concentration.

Technical Notes
---------------

We have put an emphasis on delivering good performance for neurons with high spatial complexity. We utilize vectorization, therefore, you should compile NEST with the OpenMP flag enabled. This, of course, can only be utilized if your hardware supports SIMD instructions. In that case, you can expect a performance improvement of about 3/4th of the theoretical maximum.

Let's say you have an AVX2 SIMD instruction set available, which can fit 4 doubles (4*64-bit) into its vector register. In this case you can expect about a 3x performance improvement as long as your neuron has enough compartments. We vectorize the simulation steps of all instances of the same mechanism you have defined in your NESTML model, meaning that you will get a better complexity/performance ratio the more instances of the same mechanism are used.

Here is a small benchmark example that shows the performance ratio (y-axis) as the number of compartments per neuron (x-axis) increases.

.. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/fig/performance_ratio_nonVec_vs_vec_compartmental.png
   :width: 326px
   :height: 203px
   :align: left
   :target: #

Be aware that we are using the -ffast-math flag when compiling the model by default. This can potentially lead to precision problems and inconsistencies across different systems. If you encounter unexpected results or want to be on the safe side, you can disable this by removing the flag from the CMakeLists.txt, which is part of the generated code. Note, however, that this may inhibit the compiler's ability to vectorize parts of the code in some cases.

See also
--------

`convert_cm_default_to_template.py <https://github.com/nest/nestml/blob/master/extras/convert_cm_default_to_template.py>`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script converts the generic parts (cm_default.* and cm_tree.*) of the default compartmental model in NEST to a .jinja template.

It is a helper tool for developers working concurrently on the compartmental models in NEST and NESTML. It should however be used with extreme caution, as it doesn't automatically update the compartmentcurrents.
