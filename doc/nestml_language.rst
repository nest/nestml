NESTML language documentation
=============================

NESTML is a domain specific language for the specification of models for the neuronal simulator `NEST <http://www.nest-simulator.org>`__. It has a concise syntax based on that of Python which avoids clutter in the form of semicolons, curly braces or tags as known from other programming and description languages. Instead, it concentrates on domain concepts that help to efficiently write neuron models and their equations.

NESTML files are expected to have the filename extension ``.nestml``. Each file may contain one or more neuron models. This means that there is no forced direct correspondence between model and file name. Models that shall be compiled into one extension module for NEST have to reside in the same directory. The name of the directory will be used as the name of the corresponding module.

In order to give users complete freedom in implementing neuron model dynamics, NESTML has a full procedural programming language built in. This programming language is used to define the model's time update and functions.

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

.. code-block:: nestml

    a, b, c real = -0.42
    d integer = 1
    n integer # default value is 0
    e string = "foo"
    f mV = -2e12 mV

It is legal to define a variable (or kernel, or parameter) with the same name as a physical unit, but this could lead to confusion. For example, defining a variable with name ``b`` creates an ambiguity with the physical unit ``b``, a unit of surface area. In these cases, a warning is issued when the model is processed. The variable (or kernel, and parameter) definitions will then take precedence when resolving symbols: all occurrences of the symbol in the model will be resolved to the variable rather than the unit.

For example, the following model will result in one warning and one error:

.. code-block:: nestml

   neuron test:
     state:
       ms mA = 42 mA   # redefine "ms" (from milliseconds unit to variable name)
       foo s = 0 s     # foo has units of time (seconds)
     end

     update:
       ms = 1 mA    # WARNING: Variable 'ms' has the same name as a physical unit!
       foo = 42 ms  # ERROR: Actual type different from expected. Expected: 's', got: 'mA'!
     end
   end


Documentation strings
~~~~~~~~~~~~~~~~~~~~~

Declarations can be enriched with special comments which are then taken into generated NEST code. To do so, ``#`` is used to introduce a single line comment. For multi-line comments, Python style comments (``"""..."""``) or Java-style comments (``/* ... */``) can be used.

.. code-block:: nestml

   var1 real # single line comment

   /* This is 
   *  a comment
   *  over several lines.
   */
   var2 real
   """
   This is a multiline comment in Python syntax.
   """

To enable NESTML to recognize the commented element uniquely, the following approach has to be used: there should be no white line separating the comment and its target. For example:

.. code-block:: nestml

   V_m mV = -55 mV # I am a comment of the membrane potential

   /* I am not a comment of the membrane potential. A white line separates us. */ 

If a comment shall be attached to an element, no white lines are allowed.

.. code-block:: nestml

   V_m mV = -55mV # I am a comment of the membrane potential
   /* I am a comment of the membrane potential.*/ 

Whitelines are therefore used to separate comment targets:

.. code-block:: nestml

   V_m mV = -55mV
   /* I am a comment of the membrane potential.*/ 

   /* I am a comment of the resting potential.*/
   V_rest mV = -60mV

Assignments
~~~~~~~~~~~

NESTML supports simple or compound assignments. The left-hand side of the assignment is always a variable. The right-hand side can be an arbitrary expression of a type which is compatible with the left-hand side.

Examples for valid assignments for a numeric variable ``n`` are

* simple assignment: ``n = 10`` 
* compound sum: ``n += 10`` which corresponds to ``n = n + 10`` 
* compound difference: ``n -= 10`` which corresponds to ``n = n - 10``
* compound product: ``n *= 10`` which corresponds to ``n = n * 10``
* compound quotient: ``n /= 10`` which corresponds to ``n = n / 10``

Functions
~~~~~~~~~

Functions can be used to write repeatedly used code blocks only once. They consist of the function name, the list of parameters and an optional return type, if the function returns a value to the caller. The function declaration ends with the keyword ``end``.

::

    function <name>(<list_of_arguments>) <return_type>?:
      <statements>
    end

e.g.:

.. code-block:: nestml

   function divide(a real, b real) real:
     return a/b
   end

To use a function, it has to be called. A function call is composed of the function name and the list of required parameters. The returned value (if any) can be directly assigned to a variable of the corresponding type.

::

    <function_name>(<list_of_arguments>)

e.g.

.. code-block:: nestml

   x = max(a*2, b/2)

Predefined functions
^^^^^^^^^^^^^^^^^^^^

The following functions are predefined in NESTML and can be used out of the box:

.. list-table::
   :header-rows: 1
   :widths: 10 10 30

   * - Name
     - Parameters
     - Description
   * - ``min``
     - x, y
     - Returns the minimum of x and y. Both parameters should be of the same type. The return type is equal to the type of the parameters.
   * - ``max``
     - x, y
     - Returns the maximum of x and y. Both parameters should be of the same type. The return type is equal to the type of the parameters.
   * - ``clip``
     - x, y, z
     - Returns x if it is in [y, z], y if x < y and z if x > z. All parameter types should be the same and equal to the return type.
   * - ``exp``
     - x
     - Returns the exponential of x. The type of x and the return type are Real.
   * - ``log10``
     - x
     - Returns the base 10 logarithm of x. The type of x and the return type are Real.
   * - ``ln``
     - x
     - Returns the base :math:`e` logarithm of x. The type of x and the return type are Real.
   * - ``expm1``
     - x
     - Returns the exponential of x minus 1. The type of x and the return type are Real.
   * - ``sinh``
     - x
     - Returns the hyperbolic sine of x. The type of x and the return type are Real.
   * - ``cosh``
     - x
     - Returns the hyperbolic cosine of x. The type of x and the return type are Real.
   * - ``tanh``
     - x
     - Returns the hyperbolic tangent of x. The type of x and the return type are Real.
   * - ``random_normal``
     - mean, std
     - Returns a sample from a normal (Gaussian) distribution with parameters "mean" and "standard deviation"
   * - ``random_uniform``
     - offset, scale
     - Returns a sample from a uniform distribution in the interval [offset, offset + scale)
   * - ``delta``
     - t
     - A Dirac delta impulse function at time t.
   * - ``convolve``
     - f, g
     - The convolution of kernel f with spike input port g.
   * - ``info``
     - s
     - Log the string s with logging level "info".
   * - ``warning``
     - s
     - Log the string s with logging level "warning".
   * - ``print``
     - s
     - Print the string s to stdout (no line break at the end).
   * - ``println``
     - s
     - Print the string s to stdout (with a line break at the end).
   * - ``integrate_odes``
     -
     - This function can be used to integrate all stated differential equations of the equations block.
   * - ``emit_spike``
     -
     - Calling this function in the `update` block results in firing a spike to all target neurons and devices time stamped with the current simulation time.
   * - ``steps``
     - t
     - Convert a time into a number of simulation steps. See the section :ref:`Handling of time` for more information.
   * - ``resolution``
     -
     - Returns the current resolution of the simulation in ms. See the section :ref:`Handling of time` for more information.

Return statement
^^^^^^^^^^^^^^^^

The ``return`` keyword can only be used inside of the ``function`` block. Depending on the return type (if any), it is followed by an expression of that type.

::

    return (<expression>)?

e.g.

.. code-block:: nestml

   if a > b:
     return a
   else:
     return b
   end

Control structures
~~~~~~~~~~~~~~~~~~

To control the flow of execution, NESTML supports loops and conditionals.

Loops
^^^^^

The start of the ``while`` loop is composed of the keyword ``while`` followed by a boolean condition and a colon. It is closed with the keyword ``end``. It executes the statements inside the block as long as the given boolean expression evaluates to ``true``.

::

    while <boolean_expression>:
      <statements>
    end

e.g.:

.. code-block:: nestml

   x integer = 0
   while x <= 10:
     y = max(3, x)
   end

The ``for`` loop starts with the keyword ``for`` followed by the name of a previously defined variable of type ``integer`` or ``real``. The fist variant uses an ``integer`` stepper variable which iterates over the half-open interval [``lower_bound``, ``upper_bound``) in steps of 1.

::

    for <existing_variable_name> in <lower_bound> ... <upper_bound>:
      <statements>
    end

e.g.:

.. code-block:: nestml

   x integer = 0
   for x in 1 ... 5:
     # <statements>
   end

The second variant uses an ``integer`` or ``real`` iterator variable and iterates over the half-open interval ``[lower_bound, upper_bound)`` with a positive ``integer`` or ``real`` step of size ``step``. It is advisable to choose the type of the iterator variable and the step size to be the same.

::

    for <existing_variable_name> in <lower_bound> ... <upper_bound> step <step>:
      <statements>
    end

e.g.:

.. code-block:: nestml

   x integer
   for x in 1 ... 5 step 2:
     # <statements>
   end

   x real
   for x in 0.1 ... 0.5 step 0.1:
     # <statements>
   end

Conditionals
^^^^^^^^^^^^

NESTML supports different variants of the if-else conditional. The first example shows the ``if`` conditional composed of a single ``if`` block:

::

    if <boolean_expression>:
      <statements>
    end

e.g.:

.. code-block:: nestml

   if 2 < 3:
     # <statements>
   end

The second example shows an if-else block, which executes the ``if_statements`` in case the boolean expression evaluates to true and the ``else_statements`` else.

::

    if <boolean_expression>:
      <if_statements>
    else:
      <else_statements>
    end

e.g.:

.. code-block:: nestml

   if 2 < 3:
     # <if_statements>
   else:
     # <else_statements>
   end

In order to allow grouping a sequence of related ``if`` conditions, NESTML also supports the ``elif``-conditionals. An ``if`` condition can be followed by an arbitrary number of ``elif`` conditions. Optionally, this variant also supports the ``else`` keyword for a catch-all statement. The whole conditional always concludes with an ``end`` keyword.

::

    if <boolean_expression>:
      <if_statements>
    elif <boolean_expression>:
      <elif_statements>
    else:
      <else_statements>
    end

e.g.:

.. code-block:: nestml

   if 2 < 3:
     # <if_statements>
   elif 4 > 6:
     # <elif_statements>
   else:
     # <else_statements>
   end

   if 2 < 3:
     # <if_statements>
   elif 4>6:
     # <elif_statements>
   end

Conditionals can also be nested inside of each other.

.. code-block:: nestml

   if 1 < 4:
     # <statements>
     if 2 < 3:
       # <statements>
     end
   end

Expressions and operators
-------------------------

Expressions in NESTML can be specified in a recursive fashion.

Terms
~~~~~

All variables, literals, and function calls are valid terms. Variables are names of user-defined or predefined variables (``t``, ``e``).

List of operators
~~~~~~~~~~~~~~~~~

For any two valid numeric expressions ``a``, ``b``, boolean expressions ``c``,\ ``c1``,\ ``c2``, and an integer expression ``n`` the following operators produce valid expressions.

+------------------------------------------------+--------------------------------------------------------------------+---------------------------+
| Operator                                       | Description                                                        | Examples                  |
+================================================+====================================================================+===========================+
| ``()``                                         | Expressions with parentheses                                       | ``(a)``                   |
+------------------------------------------------+--------------------------------------------------------------------+---------------------------+
| ``**``                                         | Power operator.                                                    | ``a ** b``                |
+------------------------------------------------+--------------------------------------------------------------------+---------------------------+
| ``+``, ``-``, ``~``                            | unary plus, unary minus, bitwise negation                          | ``-a``, ``~c``            |
+------------------------------------------------+--------------------------------------------------------------------+---------------------------+
| ``*``, ``/``, ``%``                            | Multiplication, Division and Modulo-Operator                       | ``a * b``, ``a % b``      |
+------------------------------------------------+--------------------------------------------------------------------+---------------------------+
| ``+``, ``-``                                   | Addition and Subtraction                                           | ``a + b``, ``a - b``      |
+------------------------------------------------+--------------------------------------------------------------------+---------------------------+
| ``<<``, ``>>``                                 | Left and right bit shifts                                          | ``a << n``, ``a >> n``    |
+------------------------------------------------+--------------------------------------------------------------------+---------------------------+
| ``&``, ``|``, ``^``                            | Bitwise ``and``, ``or`` and ``xor``                                | ``a&b``, ``|``, ``a~b``   |
+------------------------------------------------+--------------------------------------------------------------------+---------------------------+
| ``<``, ``<=``, ``==``, ``!=``, ``>=``, ``>``   | Comparison operators                                               | ``a <= b``, ``a != b``    |
+------------------------------------------------+--------------------------------------------------------------------+---------------------------+
| ``not``, ``and``, ``or``                       | Logical conjunction, disjunction and negation                      | ``not c``, ``c1 or c2``   |
+------------------------------------------------+--------------------------------------------------------------------+---------------------------+
| ``?:``                                         | Ternary operator (return ``a`` if ``c`` is ``true``, ``b`` else)   | ``c ? a : b``             |
+------------------------------------------------+--------------------------------------------------------------------+---------------------------+

Blocks
------

To structure NESTML files, all content is structured in blocks. Blocks begin with a keyword specifying the type of the block followed by a colon. They are closed with the keyword ``end``. Indentation inside a block is not mandatory but recommended for better readability. Each of the following blocks must only occur at most once on each level. Some of the blocks are required to occur in every neuron model. The general syntax looks like this:

::

    <block_type> [<args>]:
      ...
    end

Block types
~~~~~~~~~~~

``neuron <name>`` - The top-level block of a neuron model called ``<name>``. The content will be translated into a single neuron model that can be instantiated in PyNEST using ``nest.Create("<name>")``. All following blocks are contained in this block.

Within the top-level block, the following blocks may be defined:

-  ``parameters`` - This block is composed of a list of variable declarations that are supposed to contain all parameters which remain constant during the simulation, but can vary among different simulations or instantiations of the same neuron. These variables can be set and read by the user using ``nest.SetStatus(<gid>, <variable>, <value>)`` and ``nest.GetStatus(<gid>, <variable>)``.
-  ``state`` - This block is composed of a list of variable declarations that are supposed to describe parts of the neuron which may change over time.
-  ``initial_values`` - This block describes the initial values of all stated differential equations. Only variables from this block can be further defined with differential equations. The variables in this block can be recorded using a ``multimeter``.
-  ``internals`` - This block is composed of a list of implementation-dependent helper variables that supposed to be constant during the simulation run. Therefore, their initialization expression can only reference parameters or other internal variables.
-  ``equations`` - This block contains kernel definitions and differential equations. It will be explained in further detail `later on in the manual <#equations>`__.
-  ``input`` - This block is composed of one or more input ports. It will be explained in further detail `later on in the manual <#input>`__.
-  ``output`` *``<event_type>``* - Defines which type of event the neuron can send. Currently, only ``spike`` is supported. No ``end`` is necessary at the end of this block.
-  ``update`` - Inside this block arbitrary code can be implemented using the internal programming language. The ``update`` block defines the runtime behavior of the neuron. It contains the logic for state
   and equation `updates <#equations>`__ and `refractoriness <#concepts-for-refractoriness>`__. This block is translated into the ``update`` method in NEST.


Neuronal interactions
---------------------

Input
~~~~~

A neuron model written in NESTML can be configured to receive two distinct types of input: spikes and currents. For either of them, the modeler has to decide if inhibitory and excitatory inputs are lumped together into a single named buffer, or if they should be separated into differently named buffers based on their sign. The `input` block is composed of one or more lines to express the exact combinations desired. Each line has the following general form:

::

    port_name <- inhibitory? excitatory? (spike | current)

This way, a flexible combination of the inputs is possible. If, for example, current input should be lumped together, but spike input should be separated for inhibitory and excitatory incoming spikes, the following `input` block would be appropriate:

.. code-block:: nestml

   input:
     I_stim pA <- current
     inh_spikes pA <- inhibitory spike
     exc_spikes pA <- excitatory spike
   end

Please note that it is equivalent if either both `inhibitory` and `excitatory` are given or none of them at all. If only a single one of them is given, another line has to be present and specify the inverse keyword. Failure to do so will result in a translation error.

Integrating current input
^^^^^^^^^^^^^^^^^^^^^^^^^

The current port symbol (here, `I_stim`) is available as a variable and can be used in expressions, e.g.:

.. code-block:: nestml

   V_m' = -V_m/tau_m + ... + I_stim


Integrating spiking input
^^^^^^^^^^^^^^^^^^^^^^^^^

Spikes arriving at the input port of a neuron can be written as a spike train *s(t)*:

.. math::

   \large s(t) = \sum_{i=1}^N \delta(t - t_i)

To model the effect that an arriving spike has on the state of the neuron, a convolution with a kernel can be used. The kernel defines the postsynaptic response kernel, for example, an alpha (bi-exponential) function, decaying exponential, or a delta function. (See :ref:`Kernel functions` for how to define a kernel.) The convolution of the kernel with the spike train is defined as follows:

.. math::

   \large (f \ast s)(t) = \sum_{i=1}^N w_i \cdot f(t - t_i)

where :math:`w_i` is the weight of spike :math:`i`.

For example, say there is a spiking input port defined named ``spikes``. A decaying exponential with time constant ``tau_syn`` is defined as postsynaptic kernel ``G``. Integration into the membrane potential ``V_m`` can be expressed using the ``convolve(f, g)`` function, which takes a kernel and input port as its arguments:

.. code-block:: nestml

   kernel G = exp(-t/tau_syn)
   V_m' = -V_m/tau_m + convolve(G, spikes)

The type of the convolution is equal to the type of the second parameter, that is, of the spike buffer. Kernels themselves are always untyped.


Multiple input synapses
^^^^^^^^^^^^^^^^^^^^^^^

If there is more than one line specifying a `spike` or `current` port with the same sign, a neuron with multiple receptor types is created. For example, say that we define three spiking input ports as follows:

.. code-block:: nestml

   input:
     spikes1 nS <- spike
     spikes2 nS <- spike
     spikes3 nS <- spike
   end

For the sake of keeping the example simple, we assign a decaying exponential-kernel postsynaptic response to each input port, each with a different time constant:

.. code-block:: nestml

   equations:
     kernel I_kernel1 = exp(-t / tau_syn1)
     kernel I_kernel2 = exp(-t / tau_syn2)
     kernel I_kernel3 = -exp(-t / tau_syn3)
     function I_syn pA = convolve(I_kernel1, spikes1) - convolve(I_kernel2, spikes2) + convolve(I_kernel3, spikes3) + ...
     V_abs' = -V_abs/tau_m + I_syn / C_m
   end

After generating and building the model code, a ``receptor_type`` entry is available in the status dictionary, which maps port names to numeric port indices in NEST. The receptor type can then be selected in NEST during `connection setup <http://nest-simulator.org/connection_management/#receptor-types>`_:

.. code-block:: python

   neuron = nest.Create("iaf_psc_exp_multisynapse_neuron_nestml")

   sg = nest.Create("spike_generator", params={"spike_times": [20., 80.]})
   nest.Connect(sg, neuron, syn_spec={"receptor_type" : 1, "weight": 1000.})

   sg2 = nest.Create("spike_generator", params={"spike_times": [40., 60.]})
   nest.Connect(sg2, neuron, syn_spec={"receptor_type" : 2, "weight": 1000.})

   sg3 = nest.Create("spike_generator", params={"spike_times": [30., 70.]})
   nest.Connect(sg3, neuron, syn_spec={"receptor_type" : 3, "weight": 500.})

Note that in multisynapse neurons, receptor ports are numbered starting from 1.

We furthermore wish to record the synaptic currents ``I_kernel1``, ``I_kernel2`` and ``I_kernel3``. During code generation, one buffer is created for each combination of (kernel, spike input port) that appears in convolution statements. These buffers are named by joining together the name of the kernel with the name of the spike buffer using (by default) the string "__X__". The variables to be recorded are thus named as follows:

.. code-block:: python

   mm = nest.Create('multimeter', params={'record_from': ['I_kernel1__X__spikes1',
                                                          'I_kernel2__X__spikes2',
                                                          'I_kernel3__X__spikes3'],
                                          'interval': .1})
   nest.Connect(mm, neuron)

The output shows the currents for each synapse (three bottom rows) and the net effect on the membrane potential (top row):

.. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/fig/nestml-multisynapse-example.png
   :alt: NESTML multisynapse example waveform traces

For a full example, please see `tests/resources/iaf_psc_exp_multisynapse.nestml <https://github.com/nest/nestml/blob/master/tests/resources/iaf_psc_exp_multisynapse.nestml>`_ for the full model and `tests/nest_tests/nest_multisynapse_test.py <https://github.com/nest/nestml/blob/master/tests/nest_tests/nest_multisynapse_test.py>`_ for the corresponding test harness that produced the figure above.


Output
~~~~~~

Each neuron model can only send a single type of event. The type of the event has to be given in the ``output`` block. Currently, however, only spike output is supported.

.. code-block:: nestml

   output: spike

Please note that this block is **not** terminated with the ``end`` keyword.


Handling of time
----------------

To retrieve some fundamental simulation parameters, two special functions are built into NESTML:

-  ``resolution`` returns the current resolution of the simulation in ms. In NEST, this can be set by the user using the PyNEST function ``nest.SetKernelStatus({"resolution": ...})``.
-  ``steps`` takes one parameter of type ``ms`` and returns the number of simulation steps in the current simulation resolution.

These functions can be used to implement custom buffer lookup logic but should be used with care.


Equations
---------

Systems of ODEs
~~~~~~~~~~~~~~~

In the ``equations`` block one can define a system of differential equations with an arbitrary amount of equations that contain derivatives of arbitrary order. When using a derivative of a variable, say ``V``, one must write: ``V'``. It is then assumed that ``V'`` is the first time derivate of ``V``. The second time derivative of ``V`` is ``V''``, and so on. If an equation contains a derivative of order :math:`n`, for example, :math:`V^{(n)}`, all initial values of :math:`V` up to order :math:`n-1` must be defined in the ``state`` block. For example, if stating

.. code-block:: nestml

   V' = a * V

in the ``equations`` block,

.. code-block:: nestml

   V mV = 0 mV

has to be stated in the ``initial_values`` block. Otherwise, an error message is generated.

The content of spike and current buffers can be used by just using their plain names. NESTML takes care behind the scenes that the buffer location at the current simulation time step is used.


Inline expressions
^^^^^^^^^^^^^^^^^^

In the ``equations`` block, inline expressions may be used to reduce redundancy, or improve legibility in the model code. An inline expression is a named expression, that will be "inlined" (effectively, copied-and-pasted in) when its variable symbol is mentioned in subsequent ODE or kernel expressions. In the following example, the inline expression ``h_inf_T`` is defined, and then used in an ODE definition:

.. code-block:: nestml

   inline h_inf_T real = 1 / (1 + exp((V_m / mV + 83) / 4))
   IT_h' = (h_inf_T * nS - IT_h) / tau_h_T / ms

Because of nested substitutions, inline statements may cause the expressions to grow to large size. In case this becomes a problem, it is recommended to use functions instead.


Kernel functions
~~~~~~~~~~~~~~~

A `kernel` is a function of time, or a differential equation, that represents a kernel which can be used in convolutions. For example, an exponentially decaying kernel could be described as a direct function of time, as follows:

.. code-block:: nestml

   kernel g = exp(-t / tau)

with time constant, for example, equal to 20 ms:

.. code-block:: nestml

   parameters:
     tau ms = 20 ms
   end

The start at time :math:`t \geq 0` is an implicit assumption for all kernels.

Equivalently, the same exponentially decaying kernel can be formulated as a differential equation:

.. code-block:: nestml

   kernel g' = -g / tau

In this case, initial values have to be specified up to the order of the differential equation, e.g.:

.. code-block:: nestml

   initial_values:
     g real = 1
   end

Here, the ``1`` defines the peak value of the kernel at :math:`t = 0`.

An example second-order kernel is the dual exponential ("alpha") kernel, which can be defined in three equivalent ways.

(1) As a direct function of time:

    .. code-block:: nestml

       kernel g = (e/tau) * t * exp(-t/tau)

(2) As a system of coupled first-order differential equations:

    .. code-block:: nestml

       kernel g' = g$ - g  / tau,
              g$' = -g$ / tau

    with initial values:

    .. code-block:: nestml

       initial_values:
         g real = 0
         g$ real = 1
       end
       
   Note that the types of both differential equations are :math:`\text{ms}^{-1}`.

(3) As a second-order differential equation:

    .. code-block:: nestml

       kernel g'' = (-2/tau) * g' - 1/tau**2) * g

    with initial values:

    .. code-block:: nestml

       initial_values:
         g real = 0
         g' ms**-1 = e / tau
       end

A Dirac delta impulse kernel can be defined by using the predefined function ``delta``:

.. code-block:: nestml

   kernel g = delta(t)


Solver selection
~~~~~~~~~~~~~~~~

Currently, there is support for GSL and exact integration. ODEs that can be solved analytically are integrated to machine precision from one timestep to the next. To allow more precise values for analytically solvable ODEs *within* a timestep, the same ODEs are evaluated numerically by the GSL solver. In this way, the long-term dynamics obeys the "exact" equations, while the short-term (within one timestep) dynamics is evaluated to the precision of the numerical integrator.

In the case that the model is solved with the GSL integrator, desired absolute error of an integration step can be adjusted with the ``gsl_error_tol`` parameter in a ``SetStatus`` call. The default value of ``gsl_error_tol`` is ``1e-3``.


Dynamics and time evolution
---------------------------

Inside the ``update`` block, the current time can be accessed via the variable ``t``.

``integrate_odes``: this function can be used to integrate all stated differential equations of the ``equations`` block.

``emit_spike``: calling this function in the ``update`` block results in firing a spike to all target neurons and devices time stamped with the current simulation time.


Concepts for refractoriness
---------------------------

In order to model refractory and non-refractory states, two variables are necessary. The first variable (``t_ref``) defines the duration of the refractory period. The second variable (``ref_counts``) specifies the time of the refractory period that has already passed. It is initialized with 0 (the neuron is non-refractory) and set to the refractory offset every time the refractoriness condition holds. Else, the refractory offset is decremented.

.. code-block:: nestml

   parameters:
     t_ref ms = 5 ms
   end

   internals:
     ref_counts = 0
   end

   update:
     if ref_count == 0: # neuron is in non-refractory state
       if <refractoriness_condition>:
         ref_counts = steps(t_ref) # make neuron refractory for 5 ms
       end
     else:
       ref_counts -= 1 # neuron is refractory
     end
   end


Setting and retrieving model properties
---------------------------------------

-  All variables in the ``state``, ``parameters`` and ``initial_values`` blocks are added to the status dictionary of the neuron.
-  Values can be set using ``nest.SetStatus(<gid>, <variable>, <value>)`` where ``<variable>`` is the name of the corresponding NESTML variable.
-  Values can be read using ``nest.GetStatus(<gid>, <variable>)``. This call will return the value of the corresponding NESTML variable.


Recording values with devices
-----------------------------

-  All values in the ``state`` block are recordable by a ``multimeter`` in NEST.
-  The ``recordable`` keyword can be used to also make variables in other blocks (``parameters, internals``) available to recording devices.

.. code-block:: nestml

   parameters:
     recordable t_ref ms = 5 ms
   end


Guards
------

Variables which are defined in the ``state`` and ``parameters`` blocks can optionally be secured through  guards. These guards are checked during the call to ``nest.SetStatus()`` in NEST.

::

   block:
     <declaration> [[<boolean_expression>]]
   end


e.g.:

.. code-block:: nestml

   parameters:
     t_ref ms = 5 ms [[t_ref >= 0 ms]] # refractory period cannot be negative
   end
