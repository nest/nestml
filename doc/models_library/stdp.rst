stdp
####


stdp - Synapse model for spike-timing dependent plasticity

Description
+++++++++++

stdp_synapse is a synapse with spike-timing dependent plasticity (as defined in [1]_). Here the weight dependence exponent can be set separately for potentiation and depression. Examples:

=================== ==== =============================
Multiplicative STDP [2]_ mu_plus = mu_minus = 1
Additive STDP       [3]_ mu_plus = mu_minus = 0
Guetig STDP         [1]_ mu_plus, mu_minus in [0, 1]
Van Rossum STDP     [4]_ mu_plus = 0 mu_minus = 1
=================== ==== =============================


References
++++++++++

.. [1] Guetig et al. (2003) Learning Input Correlations through Nonlinear
       Temporally Asymmetric Hebbian Plasticity. Journal of Neuroscience

.. [2] Rubin, J., Lee, D. and Sompolinsky, H. (2001). Equilibrium
       properties of temporally asymmetric Hebbian plasticity, PRL
       86,364-367

.. [3] Song, S., Miller, K. D. and Abbott, L. F. (2000). Competitive
       Hebbian learning through spike-timing-dependent synaptic
       plasticity,Nature Neuroscience 3:9,919--926

.. [4] van Rossum, M. C. W., Bi, G-Q and Turrigiano, G. G. (2000).
       Stable Hebbian learning from spike timing-dependent
       plasticity, Journal of Neuroscience, 20:23,8812--8821



Parameters
++++++++++


.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "d", "ms", "1ms", "Synaptic transmission delay"    
    "lambda", "real", "0.01", ""    
    "tau_tr_pre", "ms", "20ms", ""    
    "tau_tr_post", "ms", "20ms", ""    
    "alpha", "real", "1", ""    
    "mu_plus", "real", "1", ""    
    "mu_minus", "real", "1", ""    
    "Wmax", "real", "100.0", ""    
    "Wmin", "real", "0.0", ""


State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "w", "real", "1.0", "Synaptic weight"    
    "pre_trace", "real", "0.0", ""    
    "post_trace", "real", "0.0", ""
Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `stdp <https://github.com/nest/nestml/tree/master/models/synapses/stdp_synapse.nestml>`_.


Characterisation
++++++++++++++++

.. include:: stdp_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.906792