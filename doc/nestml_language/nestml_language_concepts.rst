NESTML language concepts
========================

Data types and physical units
-----------------------------

Data types define types of variables as well as parameters and return values of functions. NESTML provides the following primitive types and physical data types:

Primitive data types
~~~~~~~~~~~~~~~~~~~~

-  ``real`` corresponds to the ``double`` data type in C++. Example literals are: ``42.0``, ``-0.42``, ``.44``
-  ``integer`` corresponds to the ``long`` data type in C++. Example literals are: ``42``, ``-7``
-  ``boolean`` corresponds to the ``bool`` data type in C++. Its only literals are ``true`` and ``false``
-  ``string`` corresponds to the ``std::string`` data type in C++. Example literals are: ``"Bob"``, ``""``, ``"Hello World!"``
-  ``void`` corresponds to the ``void`` data type in C++. No literals are possible and this can only be used in the declaration of a function without a return value.

Physical units
~~~~~~~~~~~~~~

A physical unit in NESTML can be either a simple physical unit or a complex physical unit. A simple physical unit is composed of an optional magnitude prefix and the name of the unit.

The following table lists seven base units, which can be used to specify any physical unit. This idea is based on `the SI units <https://en.wikipedia.org/wiki/International_System_of_Units>`__.

+-----------------------+-------------+------------------+
| Quantity              | Unit Name   | NESTML/SI unit   |
+=======================+=============+==================+
| length                | meter       | m                |
+-----------------------+-------------+------------------+
| mass                  | kilogram    | kg               |
+-----------------------+-------------+------------------+
| time                  | second      | s                |
+-----------------------+-------------+------------------+
| electric current      | ampere      | A                |
+-----------------------+-------------+------------------+
| temperature           | kelvin      | K                |
+-----------------------+-------------+------------------+
| amount of substance   | mole        | mol              |
+-----------------------+-------------+------------------+
| luminous intensity    | candela     | cd               |
+-----------------------+-------------+------------------+

Any other physical unit can be expressed as a combination of these seven units. These other units are called derived units. NESTML provides a concept for the derivation of new physical units, i.e., by combining simple units (consisting of a prefix and an SI unit), the user is able to create arbitrary physical units.

Units can have at most one of the following magnitude prefixes:

+----------+-----------+-----------------+----------+-----------+-----------------+
| Factor   | SI Name   | NESTML prefix   | Factor   | SI Name   | NESTML prefix   |
+==========+===========+=================+==========+===========+=================+
| 10^-1    | deci      | d               | 10^1     | deca      | da              |
+----------+-----------+-----------------+----------+-----------+-----------------+
| 10^-2    | centi     | c               | 10^2     | hecto     | h               |
+----------+-----------+-----------------+----------+-----------+-----------------+
| 10^-3    | milli     | m               | 10^3     | kilo      | k               |
+----------+-----------+-----------------+----------+-----------+-----------------+
| 10^-6    | micro     | mu              | 10^6     | mega      | M               |
+----------+-----------+-----------------+----------+-----------+-----------------+
| 10^-9    | nano      | n               | 10^9     | giga      | G               |
+----------+-----------+-----------------+----------+-----------+-----------------+
| 10^-12   | pico      | p               | 10^12    | tera      | T               |
+----------+-----------+-----------------+----------+-----------+-----------------+
| 10^-15   | femto     | f               | 10^15    | peta      | P               |
+----------+-----------+-----------------+----------+-----------+-----------------+
| 10^-18   | atto      | a               | 10^18    | exa       | E               |
+----------+-----------+-----------------+----------+-----------+-----------------+
| 10^-21   | zepto     | z               | 10^21    | zetta     | Z               |
+----------+-----------+-----------------+----------+-----------+-----------------+
| 10^-24   | yocto     | y               | 10^24    | yotta     | Y               |
+----------+-----------+-----------------+----------+-----------+-----------------+

Simple physical units can be combined to complex units. For this, the operators , ``*`` (multiplication), ``/`` (division), ``**`` (power) and ``()`` (parenthesis) can be used. An example could be

.. code-block:: nestml

   mV*mV*nS**2/(mS*pA)

Units of the form ``<unit> ** -1`` can also be expressed as ``1/<unit>``. For example

.. code-block:: nestml

   (ms*mV)**-1

is equivalent to

.. code-block:: nestml

   1/(ms*mV)

NESTML also supports the usage of named derived-units such as Newton, Henry or lux:

.. list-table::
   :header-rows: 1
   :widths: 10 5 20 20 20

   * - Name
     - Symbol
     - Quantity
     - In other SI units
     - In base SI units
   * - radian
     - rad
     - angle
     - 
     - m⋅m\ :sup:`-1`
   * - steradian
     - sr
     - solid angle
     - 
     - m\ :sup:`2`\ ⋅m\ :sup:`−2`
   * - Hertz
     - Hz
     - frequency
     -
     - s\ :sup:`−1`
   * - Newton      
     - N        
     - force, weight                                
     -
     - kg⋅m⋅s\ :sup:`−2`
   * - Pascal      
     - Pa       
     - pressure, stress                             
     - N/m\ :sup:`2`                                                                                                        
     - kg⋅m\ :sup:`−1`\ ⋅s\ :sup:`−2`
   * - Joule       
     - J        
     - energy, work, heat                           
     - N⋅m=Pa⋅m\ :sup:`3`
     - kg⋅m\ :sup:`2`\ ⋅s\ :sup:`−2`                                                                       
   * - Watt        
     - W        
     - power, radiant flux                          
     - J/s                                                                                                         
     - kg⋅m\ :sup:`2`\ ⋅s\ :sup:`−3`                                                                                         
   * - Coulomb     
     - C        
     - electric charge or quantity of electricity   
     -                                                                                                             
     - s⋅A                                                                                                    
   * - Volt        
     - V        
     - voltage (electrical potential), emf          
     - W/A                                                                                                         
     - kg⋅m\ :sup:`2`\ ⋅s\ :sup:`−3`\ ⋅ A\ :sup:`−1`
   * - Farad
     - F
     - capacitance
     - C/V
     - kg\ :sup:`−1`\ ⋅ m\ :sup:`−2`\ ⋅ s\ :sup:`4`\ ⋅ A\ :sup:`2`
   * - Ohm         
     - Ω        
     - resistance, impedance, reactance             
     - V/A                                                                                                         
     - kg⋅(m\ :sup:`2`\ ) ⋅ (s\ :sup:`−3`\ ) ⋅(A\ :sup:`−2`\ )                                                                           
   * - Siemens     
     - S        
     - electrical conductance                       
     - Ω\ :sup:`−1`
     - (kg\ :sup:`−1`\ ) ⋅(m\ :sup:`−2`\ ) ⋅(s\ :sup:`3`\ ) ⋅ A\ :sup:`2`
   * - Weber       
     - Wb       
     - magnetic flux                                
     - V⋅s                                                                                                         
     - kg⋅(m\ :sup:`2`\ ) ⋅(s\ :sup:`−2`\ ) ⋅(A\ :sup:`−1`\ )                                                                         
   * - Tesla       
     - T        
     - magnetic flux density                        
     - Wb/m\ :sup:`2`
     - kg⋅(s\ :sup:`−2`\ ) ⋅(A\ :sup:`−1`\ )
   * - Henry
     - H
     - inductance
     - Wb/A
     - kg⋅(m\ :sup:`2`\ ) ⋅(s\ :sup:`−2`\ ) ⋅(A\ :sup:`−2`\ )
   * - lumen       
     - lm       
     - luminous flux                                
     - cd⋅sr
     - cd
   * - lux
     - lx
     - illuminance
     - lm/m\ :sup:`2`
     - m\ :sup:`−2`\ ⋅ cd                                                 
   * - Becquerel   
     - Bq       
     - radioactivity (decays per unit time)         
     -                                                                                                             
     - s\ :sup:`−1`
   * - Gray        
     - Gy       
     - absorbed dose (of ionizing radiation)        
     - J/kg                                                                                                        
     - (m\ :sup:`2`\ )⋅(s\ :sup:`−2`\ )                                                                                      
   * - Sievert     
     - Sv       
     - equivalent dose (of ionizing radiation)      
     - J/kg                                                                                                        
     - (m\ :sup:`2`\ )⋅ (s\ :sup:`−2`\ )                                                                                      
   * - katal       
     - kat      
     - catalytic activity                           
     -                                                                                                             
     - mol⋅(s\ :sup:`−1`\ )                                                                                            


Here, except for Ohm, the symbol of the unit has to be used in the model, e.g.:

.. code-block:: nestml

   x = 10 N * 22 Ohm / 0.5 V

Physical unit literals
~~~~~~~~~~~~~~~~~~~~~~

Simple unit literals are composed of a number and a type name (with or without a whitespace inbetween the two):

::

   <number> <unit_type>

e.g.:

.. code-block:: nestml

   V_m mV = 1 mV

Complex unit literals can be composed according to the common arithmetic rules, i.e., by using operators to combine simple units:

.. code-block:: nestml

   V_rest = -55 mV/s**2

Type and unit checks
~~~~~~~~~~~~~~~~~~~~

NESTML checks type correctness of all expressions. This also applies to assignments, declarations with an initialization and function calls. NESTML supports conversion of ``integer``\ s to ``real``\ s. A conversion between ``unit``-typed and ``real``-typed variables is also possible. However, these conversions are reported as warnings. Finally, there is no conversion between numeric types and boolean or string types.

Basic elements of the embedded programming language
---------------------------------------------------

The basic elements of the language are declarations, assignments, function calls and return statements.

Declarations
~~~~~~~~~~~~

Declarations are composed of a non-empty list of comma separated names. A valid name starts with a letter, an underscore or the dollar character. Furthermore, it can contain an arbitrary number of letters, numbers, underscores and dollar characters. Formally, a valid name satisfies the following regular expression:

::

    ( 'a'..'z' | 'A'..'Z' | '_' | '$' )( 'a'..'z' | 'A'..'Z' | '_' | '0'..'9' | '$' )*

Names of functions and input ports must also satisfy this pattern. The type of the declaration can be any of the valid NESTML types. The type of the initialization expression must be compatible with the type of the declaration.


::

    <list_of_comma_separated_names> <type> (= initialization_expression)?

--

Setting and retrieving model properties
---------------------------------------

-  All variables in the ``state`` and ``parameters`` blocks are added to the status dictionary of the neuron.
-  Values can be set using ``nest.SetStatus(<gid>, <variable>, <value>)`` where ``<variable>`` is the name of the corresponding NESTML variable.
-  Values can be read using ``nest.GetStatus(<gid>, <variable>)``. This call will return the value of the corresponding NESTML variable.


Recording values with devices
-----------------------------

-  All values in the ``state`` block are recordable by a ``multimeter`` in NEST.
-  The ``recordable`` keyword can be used to also make ``inline`` expressions in the ``equations`` block available to recording devices.

.. code-block:: nestml

   equations:
     ...
     recordable inline V_m mV = V_abs + V_reset
   end


Guards
------

Variables which are defined in the ``state`` and ``parameters`` blocks can optionally be secured through guards. These guards are checked during the call to ``nest.SetStatus()`` in NEST.

::

   block:
     <declaration> [[<boolean_expression>]]
   end


e.g.:

.. code-block:: nestml

   parameters:
     t_ref ms = 5 ms [[t_ref >= 0 ms]] # refractory period cannot be negative
   end
