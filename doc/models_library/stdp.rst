stdp
####


stdp - Synapse model for spike-timing dependent plasticity

Description
+++++++++++

stdp_synapse is a synapse with spike time dependent plasticity (as defined in [1]_). Here the weight dependence exponent can be set separately for potentiation and depression. Examples:

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

pre_trace real = 0.


Parameters
++++++++++


  !!! cannot have a variable called "delay".. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "the_delay", "ms", "1ms", "!!! cannot have a variable called ""delay"""    
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

    
    "w", "real", "1.0", "pre_trace real = 0."
Source code
+++++++++++

.. code-block:: nestml

   synapse stdp: # pre_trace real = 0.
       state: # pre_trace real = 0.
           w real = 1.0 @nest::weight # pre_trace real = 0.
       parameters: # !!! cannot have a variable called "delay"
           the_delay ms = 1ms @nest::delay # !!! cannot have a variable called "delay"
           lambda real = 0.01
           tau_tr_pre ms = 20ms
           tau_tr_post ms = 20ms
           alpha real = 1
           mu_plus real = 1
           mu_minus real = 1
           Wmax real = 100.0
           Wmin real = 0.0
       equations:
           kernel pre_trace_kernel = exp(-t / tau_tr_pre)
           inline pre_trace real = convolve(pre_trace_kernel,pre_spikes)
           # all-to-all trace of postsynaptic neuron
           kernel post_trace_kernel = exp(-t / tau_tr_post)
           inline post_trace real = convolve(post_trace_kernel,post_spikes)
       input:
           pre_spikes nS <-spike
           post_spikes nS <-spike
       output: spike
       onReceive(post_spikes): # post_trace += 1
           # potentiate synapse
           w_ real = Wmax * (w / Wmax + (lambda * (1.0 - (w / Wmax)) ** mu_plus * pre_trace))
           w = min(Wmax,w_)
    
       onReceive(pre_spikes): # pre_trace += 1
           # depress synapse
           w_ real = Wmax * (w / Wmax - (alpha * lambda * (w / Wmax) ** mu_minus * post_trace))
           w = max(Wmin,w_)
           # deliver spike to postsynaptic partner
           deliver_spike(w,the_delay)
    




Characterisation
++++++++++++++++

.. include:: stdp_characterisation.rst


.. footer::

   Generated at 2023-03-09 09:14:34.951278