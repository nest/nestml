lorenz_attractor
################




Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "sigma", "real", "10", ""    
    "beta", "real", "8 / 3", ""    
    "rho", "real", "28", ""




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "x", "real", "1", ""    
    "y", "real", "1", ""    
    "z", "real", "1", ""




Equations
+++++++++




.. math::
   \frac{ dx } { dt }= \frac{ \sigma \cdot (y - x) } { \mathrm{s} }


.. math::
   \frac{ dy } { dt }= \frac{ (x \cdot (\rho - z) - y) } { \mathrm{s} }


.. math::
   \frac{ dz } { dt }= \frac{ (x \cdot y - \beta \cdot z) } { \mathrm{s} }





Source code
+++++++++++

.. code-block:: nestml

   neuron lorenz_attractor:
       state:
           x real = 1
           y real = 1
           z real = 1
       equations:
           x'=sigma * (y - x) / s
           y'=(x * (rho - z) - y) / s
           z'=(x * y - beta * z) / s

       update:
           integrate_odes()

       parameters:
           sigma real = 10
           beta real = 8 / 3
           rho real = 28



Characterisation
++++++++++++++++

.. include:: lorenz_attractor_characterisation.rst


.. footer::

   Generated at 2021-12-09 08:22:32.491153