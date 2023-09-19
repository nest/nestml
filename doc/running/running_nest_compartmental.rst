NEST Simulator compartmental target
###################################

Introduction
------------

Generate code for a compartmental model simulated in NEST.

The structure of the neuron -- soma, dendrites, axon -- is user-defined at runtime by adding compartments through ``nest.SetStatus()``. Each compartment can be assigned receptors, also through ``nest.SetStatus()``.


Writing a compartmental NESTML model
------------------------------------

Defining the membrane potential variable
----------------------------------------

One variable in the model represents the local membrane potential in a compartment. By default, it is called ``v_comp``. (This name is defined in the compartmental code generator options as the ``compartmental_variable_name`` option.)

.. code-block:: nestml
    
   neuron <neuron_name>:
       state:
           v_comp real = 0   # rhs value is irrelevant


Channel description
-------------------

Next, define one or more channels. An ion-channel is described in the following way:

.. code-block:: nestml
    
   neuron <neuron_name>:
        equations:
            inline <current_equation> real = \
                <some equation based on state variables, parameters and compartment current> \
                @mechanism::channel

The user can describe Hodgkin-Huxley (HH) models in the same way as before by just adding the ODE describing the evolution of the gating-variable but may also describe any other type of model. Additionally the explicit ``@mechanism::<type>`` descriptor has been added which we thought enhances overview over the NESTML code for the user but also makes the code-generation a bit better organised because it decouples the context condition checks from differentiating what kind of mechanism is described by a section of code.

As an example for a HH-type channel:

.. code-block:: nestml
    
   neuron <neuron_name>:
       state:
           m_Na real = 0.0
           h_Na real = 0.0

       equations:
           h_Na'= (h_inf_Na(v_comp) - h_Na) / (tau_h_Na(v_comp) * 1 s)
           m_Na'= (m_inf_Na(v_comp) - m_Na) / (tau_m_Na(v_comp) * 1 s)

           inline Na real = gbar_Na * m_Na**3 * h_Na * (e_Na - v_comp) @mechanism::channel

All of the currents within a compartment (marked by ``@mechanism::channel``) are added up within a compartment.

For a complete example, please see `cm_default.nestml <https://github.com/nest/nestml/blob/master/tests/nest_compartmental_tests/resources/cm_default.nestml>`_ and its associated unit test, `compartmental_model_test.py <https://github.com/nest/nestml/blob/master/tests/nest_compartmental_tests/compartmental_model_test.py>`_.


Concentration description
-------------------------

The concentration-model description looks very similar:

.. code-block:: nestml
    
   neuron <neuron_name>:
       equations:
           <some_state_variable>' = <ODE right-hand-side for some_state_variable> @mechanism::concentration

The only difference here is that the equation that is marked with the ``@mechanism::concentration`` descriptor is not an inline equation but an ODE. This is because in case of the ion-channel what we want to simulate is the current which relies on the evolution of some state variables like gating variables in case of the HH-models, and the compartment voltage. The concentration though can be more simply described by an evolving state directly.

For a complete example, please see `concmech.nestml <https://github.com/nest/nestml/blob/master/tests/nest_compartmental_tests/resources/concmech.nestml>`_ and its associated unit test, `compartmental_model_test.py <https://github.com/nest/nestml/blob/master/tests/nest_compartmental_tests/concmech_model_test.py>`_.

