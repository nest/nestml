stdp_triplet
############


XXX: NAIVE VERSION: unclear about relative timing of pre and post trace updates due to incoming pre and post spikes



Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "the_delay", "ms", "1ms", "!!! cannot have a variable called ""delay"""    
    "tau_plus", "ms", "16.8ms", "time constant for tr_r1"    
    "tau_x", "ms", "101ms", "time constant for tr_r2"    
    "tau_minus", "ms", "33.7ms", "time constant for tr_o1"    
    "tau_y", "ms", "125ms", "time constant for tr_o2"    
    "A2_plus", "real", "7.5e-10", ""    
    "A3_plus", "real", "0.0093", ""    
    "A2_minus", "real", "0.007", ""    
    "A3_minus", "real", "0.00023", ""    
    "Wmax", "nS", "100nS", ""    
    "Wmin", "nS", "0nS", ""



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "w", "nS", "1nS", ""
Source code
+++++++++++

.. code-block:: nestml

   synapse stdp_triplet:
     state:
       w nS = 1nS
     end
     parameters:
       the_delay ms = 1ms # !!! cannot have a variable called "delay"
       tau_plus ms = 16.8ms # time constant for tr_r1
       tau_x ms = 101ms # time constant for tr_r2
       tau_minus ms = 33.7ms # time constant for tr_o1
       tau_y ms = 125ms # time constant for tr_o2
       A2_plus real = 7.5e-10
       A3_plus real = 0.0093
       A2_minus real = 0.007
       A3_minus real = 0.00023
       Wmax nS = 100nS
       Wmin nS = 0nS
     end
     equations:
       kernel tr_r1_kernel = exp(-t / tau_plus)
       inline tr_r1 real = convolve(tr_r1_kernel,pre_spikes)
       kernel tr_r2_kernel = exp(-t / tau_x)
       inline tr_r2 real = convolve(tr_r2_kernel,pre_spikes)
       kernel tr_o1_kernel = exp(-t / tau_minus)
       inline tr_o1 real = convolve(tr_o1_kernel,post_spikes)
       kernel tr_o2_kernel = exp(-t / tau_y)
       inline tr_o2 real = convolve(tr_o2_kernel,post_spikes)
     end

     input:
       pre_spikes nS <-spike
       post_spikes nS <-spike
     end

     output: spike

     onReceive(post_spikes):
       # potentiate synapse
       #w_ nS = Wmax * ( w / Wmax + tr_r1 * ( A2_plus + A3_plus * tr_o2 ) )
       w_ nS = w + tr_r1 * (A2_plus + A3_plus * tr_o2)
       w = min(Wmax,w_)
     end

     onReceive(pre_spikes):
       # depress synapse
       #w_ nS = Wmax * ( w / Wmax  -  tr_o1 * ( A2_minus + A3_minus * tr_r2 ) )
       w_ nS = w - tr_o1 * (A2_minus + A3_minus * tr_r2)
       w = max(Wmin,w_)
       # deliver spike to postsynaptic partner
       deliver_spike(w,the_delay)
     end

   end



Characterisation
++++++++++++++++

.. include:: stdp_triplet_characterisation.rst


.. footer::

   Generated at 2021-12-09 08:22:33.021181