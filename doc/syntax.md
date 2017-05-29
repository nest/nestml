# NESTML language documentation

NESTML is a domain specific language for the specification of models for the neuronal simulator [NEST](http://www.nest-simulator.org). It has a concise syntax based on that of Python which avoids clutter in the form of semicolons, curly braces or tags as known from other programming and description languages. Instead it concentrates on domain concepts that help to efficiently write neuron models and their equations.

NESTML files are expected to have the filename extension `.nestml`. Each file may contain one or more neuron models. This means that there is no forced direct correspondence between model and file name. Models that shall be compiled into one extension module for NEST have to reside in the same directory. The name of the directory will be used as the name of the corresponding module.

In order to give users complete freedom in implementing neuron model dynamics, NESTML has a full procedural programming language built in. This programming language is used to define the model's time update and functions.

### Data types and physical units

Data types define types of variables as well as parameters and return values of functions. NESTML provides the following primitive types and physical data types:

#### Primitive data types
* `real` corresponds to the `double` data type in C++. Example literals are: `42.0`, `-0.42`, `.44`
* `integer` corresponds to the `long` data type in C++. Example literals are: `42`, `-7`
* `boolean` corresponds to the `bool` data type in C++. Its only literals are `true` and `false`
* `string` corresponds to the `std::string` data type in C++. Example literals are: `"Bob"`, `""`, `"Hello World!"`
* `void` corresponds to the `void` data type in C++. No literals are possible and this can only be used in the declaration of a function without return value.

#### Physical units

A physical unit in NESTML can be either a simple physical unit or a complex physical unit. A simple physical unit is composed of an optional magnitude prefix and the name of the unit.

The following table lists seven base units, which can be used to specify any physical unit. This idea is based on [the SI units](https://en.wikipedia.org/wiki/International_System_of_Units).

|Quantity | Unit Name | NESTML/SI unit |
|---|---|---|
| length              | metre    | m |
| mass                | kilogram | kg |
| time                | second   | s |
| electric current    | ampere   | A |
| temperature         | kelvin   | K |
| amount of substance | mole     | mol |
| luminous intensity  | candela  | cd |

Any other physical unit can be expressed as a combination of these seven units. These other units are called derived units. NESTML provides the following derived units as built-in data types:

|Quantity | Unit name | Definition | NESTML/SI unit |
|---|---|---|---|
| capacitance            | farad   | A<sup>2</sup> s<sup>4</sup> kg<sup>−1</sup> m<sup>−2</sup> | F |
| electrical conductance | siemens | A<sup>2</sup> s<sup>3</sup> kg<sup>−1</sup> m<sup>−2</sup> | S |
| electric charge        | coulomb | A s                                                        | C |
| electric potential     | volt    | kg m<sup>2</sup> A<sup>−1</sup> s<sup>−3</sup>             | V |
| electric resistance    | ohm     | kg m<sup>2</sup> A<sup>−2</sup> s<sup>−3</sup>             | ohm/&Omega; |
| frequency              | hertz   | s<sup>−1</sup>                                             | Hz |

| | | | |
|---|---|---|---|
|||| Bq |
|||| Gy |
|||| Sv |
|||| J |
|||| W  |
|||| Wb |
|||| N |
|||| Pa |
|||| kat |

Units can have at most one of the following magnitude prefixes:

|Factor | SI Name | NESTML prefix | Factor | SI Name | NESTML prefix
|---|---|---|---|---|---|
|10<sup>-1</sup>  | deci  | d  | 10<sup>1</sup>  | deca  | da |
|10<sup>-2</sup>  | centi | c  | 10<sup>2</sup>  | hecto | h |
|10<sup>-3</sup>  | milli | m  | 10<sup>3</sup>  | kilo  | k |
|10<sup>-6</sup>  | micro | mu | 10<sup>6</sup>  | mega  | M |
|10<sup>-9</sup>  | nano  | n  | 10<sup>9</sup>  | giga  | G |
|10<sup>-12</sup> | pico  | p  | 10<sup>12</sup> | tera  | T |
|10<sup>-15</sup> | femto | f  | 10<sup>15</sup> | peta  | P |

| | | | | | |
|---|---|---|---|---|---|
|10<sup>-18</sup> | atto  | a  | 10<sup>18</sup> | exa   | E |
|10<sup>-21</sup> | zepto | z  | 10<sup>21</sup> | zetta | Z |
|10<sup>-24</sup> | yocto | y  | 10<sup>24</sup> | yotta | Y |

Finally, simple physical units can be combined to complex units. For this, the operators , `*` (multiplication), `/` (division), `**` (power) and `()` (parenthesis) can be used. An example could be
```
mV*mV*nS**2/(mS*pA)
```

Units of the form `<unit> ** -1` can also be expressed as `1\<unit>`. For example
```
(ms*mV)**-1
```
is equivalent to
```
1/(ms*mV)
```

#### Physical unit literals

Simple unit literals are composed of a number and a type name (with or without a whitespace inbetween the two). Complex unit literals are composed of a number and a type inside of square brackets. Simple units can also be put inside square brackets.
```
<number> <unit_type>
<number> [<unit_type>]

a mV = 1mV
aa mV = 1[mV]
b mV/ms = 1[mV/ms]
```

#### Type and unit checks

NESTML checks type correctness of all expressions. This also applies to assignments, declarations with an initialization and function calls. NESTML supports conversion of `integer`s to `real`s. A conversion between `unit`-typed and `real`-typed variables is also possible. However, these conversions are reported as warnings. Finally, there is no conversion between numeric types and boolean types.

### Basic elements of the embedded programming language

The basic elements of the language are declarations, assignments, function calls and return statements.

#### Declarations

Declarations are composed of a non-empty list of comma separated names. A valid name starts with a letter, an underscore or the dollar character. Furthermore, it can contain an arbitrary number of letters, numbers, underscores and dollar characters. Formally, a valid name satisfies the following regular expression:
```
( 'a'..'z' | 'A'..'Z' | '_' | '$' )( 'a'..'z' | 'A'..'Z' | '_' | '0'..'9' | '$' )*
```

Names of functions and input ports must also satisfy this pattern. The type of the declaration can be any of the valid NESTML types. The type of the initialization expression must be compatible with the type of the declaration.
```
<list_of_comma_separated_names> <type> (= initialization_expression)?

a, b, c real = -0.42
d integer = 1
n integer # default value is 0
e string = "Bob"
f mV = -2e12mV
```

#### Assignments

NESTML supports simple or compound assignments. The left-hand side of the assignment is always a variable. The right-hand side can be an arbitrary expression of a type which is compatible with the left-hand side.

Examples for valid assignments for a numeric variable `n` are
  * simple assignment: `n = 10`
  * compound sum: `n += 10` which corresponds to `n = n + 10`
  * compound difference: `n -= 10` which corresponds to `n = n - 10`
  * compound product: `n *= 10` which corresponds to `n = n * 10`
  * compound quotient: `n /= 10` which corresponds to `n = n - 10`

#### Functions

Functions can be used to write repeatedly used code blocks only once. They consist of the function name, the list of parameters and an optional return type, if the function returns a value to the caller. The function declaration ends with the keyword `end`.
```
function <name>(<list_of_arguments>) <return_type>?:
  <statements>
end

function divide(a real, b real) real:
  return a/b
end
```

To use a function, it has to be called. A function call is composed of the function name and the list of required parameters. The returned value (if any) can be directly assigned to a variable of the corresponding type.
```
<function_name>(<list_of_arguments>)

x = max(a*2, b/2)
```

##### Predefined functions

| | | |
|---|---|---|
| exp | expm1 | log |
| max | pow | random |
| randomInt | warning | info |

#### Return statement

The `return` keyword can only be used inside of the `function` block. Depending on the return type (if any), it is followed by an expression of that type.
```
return (<expression>)?

if a > b:
  return a
else:
  return b
end
```

### Control structures

To control the flow of executioon, NESTML supports loops and conditionals.

#### Loops

The start of the `while` loop is composed of the keyword `while` followed by a boolean condition and a colon. It is closed with the keyword `end`. It executes the statements inside the block as long as the given boolean expression evaluates to `true`.
```
while <boolean_expression>:
  <statements>
end

x integer = 0
while x <= 10:
  y = max(3, x)
end
```

The `for` loop starts with the keyword `for` followed by the name of a previously defined variable of type `integer` or `real`. The fist variant uses an `integer` stepper variable which iterates over the half-open interval [`lower_bound`, `upper_bound`) in steps of 1.
```
for <existing_variable_name> in <lower_bound> ... <upper_bound>:
  <statements>
end

x integer = 0
for x in 1 ... 5:
  <statements>
end
```
The second variant uses an `integer` or `real` iterator variable and iterates over the half-open interval `[lower_bound, upper_bound)` with a positive `integer` or `real` step of size `step`. It is advisable to chose the type of the iterator variable and the step size to be the same.
```
for <existing_variable_name> in <lower_bound> ... <upper_bound> step <step>:
  <statements>
end

x integer
for x in 1 ... 5 step 2:
  <statements>
end

x real
for x in 0.1 ... 0.5 step 0.1:
  Statements
end
```

#### Conditionals

NESTML supports different variants of the if-else conditional. The first example shows the `if` conditional composed of a single `if` block:

```
if <boolean_expression>:
  <statements>
end

if 2 < 3:
  <statements>
end
```

The second example shows an if-else block, which executes the `if_statements` in case the boolean expression evaluates to true and the `else_statements` else.
```
if <boolean_expression>:
  <if_statements>
else:
  <else_statements>
end

if 2 < 3:
  <if_statements>
else:
  <else_statements>
end
```

In order to allow grouping a sequence of related `if` conditions, NESTML also supports the `elif`-conditionals. An `if` condition can be followed by an arbitrary number of `elif` conditions. Optionally, this variant also supports the `else` keyword for a catch-all statement. The whole conditional always concludes with an `end` keyword.
```
if <boolean_expression>:
  <if_statements>
elif <boolean_expression>:
  <elif_statements>
else:
  <else_statements>
end

if 2 < 3:
  <if_statements>
elif 4>6:
  <elif_statements>
else:
  <else_statements>
end

if 2 < 3:
  <if_statements>
elif 4>6:
  <elif_statements>
end
```

Conditionals can also be nested inside of each other.
```
if 1 < 4:
  <statements>
  if 2 < 3:
    <statements>
  end
end
```

### Expressions and operators

Expressions in NESTML can be specified in a recursive fashion.

#### Terms:

All variables, literals, and function calls are valid terms. Variables are names of user defined or predefined variables (`t`, `e`)

#### List of operators

For any two valid numeric expressions `a`, `b`, a boolean expressions `c`,`c1`,`c2`, and an integer expression `n` the following operators produce valid expressions.

| Operator | Description | Examples |
|---|---|---|
|`()`          | Expressions with parentheses | `(a)` |
|`**`          | Power operator. | `a ** b` |
|`+`, `-`, `~` | unary plus, unary minus, bitwise negation | `-a`, `~c` |
|`\*`, `/`, `%`| Multiplication, Division and Modulo-Operator | `a \* b`, `a % b` |
|`+`, `-`      | Addition and Subtraction | `a + b`, `a - b` |
|`<<`, `>>`    | Left and right bit shifts | `a << n`, `a >> n` |
|`&`, <code>&#124;</code>, `^`| Bitwise `and`, `or` and `xor` | `a&b`, <code>a&#124;b</code>, `a~b` |
|`<`, `<=`, `==`, `!=`, `>=`, `>`|  Comparison operators | `a <= b`, `a != b` |
|`not`, `and`, `or`| Logical conjunction, disjunction and negation | `not c`, `c1 or c2` |
| `?:`         | Ternary operator (return `a` if `c` is `true`, `b` else) | `c ? a : b` |

## Blocks

To structure NESTML files, all content is structured in blocks. Blocks begin with a keyword specifying the type of the block followed by a colon. They are closed with the keyword `end`. Indentation inside a block is not mandatory but recommended for better readability. Each of the following blocks must only occur at most once on each level. Some of the blocks are required to occur in every neuron model. The general syntax looks like this:
```
<block_type> [<args>]:
  ...
end
```

### Block types

* `neuron` *`<name>`* - The top-level block of a neuron model called `<name>`. The content will be translated into a single neuron model that can be instantiated in PyNEST using `nest.Create(<name>)`. All following blocks are contained in this block.
* `parameters` - This block is composed of a list of variable declarations that are supposed to contain all variables which remain constant during the simulation, but can vary among different simulations or instantiations of the same neuron. These variables can be set and read by the user using `nest.SetStatus(<gid>, <variable>, <value>)` and  `nest.GetStatus(<gid>, <variable>)`.
* `state` - This block is composed of a list of variable declarations that are supposed to describe the time dependent state of the neuron. Only variables from this block can be further defined with differential equations. The variables in this block can be recorded using a `multimeter`.
* `internals` - This block is composed of a list of implementation dependent helper variables that supposed to be constant during the simulation run. Therefore, their initialization expression can only reference parameters or other internal variables.
* `equations` - This block contains shape definitions and differential equations. It will be explained in further detail [later on in the manual](#equations).
* `input` - This block is composed of one or more input ports. It will be explained in further detail [later on in the manual](#input).
* `output` *`<event_type>`* - Defines which type of event the neuron can send. Currently, only `spike` is supported. No `end` is necessary at the end of this block.
* `update` - Inside this block arbitrary code can be implemented using the internal programming language. The `update` block defines the runtime behaviour of the neuron. It contains the logic for state and equation [updates](#equations) and [refractoriness](#concepts-for-refractoriness). This block is translated into the `update` method in NEST.

## Neuronal interactions

### Synaptic input

A neuron model written in NESTML can be configured to receive two distinct types of input, spikes and currents. For either of them, the modeler has to decide if inhibitory and excitatory inputs are lumped together into a single named buffer, or if they should be separated into different named buffers based on their sign. The `input` block is composed of one or more lines to express the exact combinations desired. Each line has the following general form:
```
port_name <- inhibitory? excitatory? (spike | current)
```

This way, a flexible combination of the inputs is possible. If, for example, current input should be lumped together, but spike input should be separated for inhibitory and excitatory incoming spikes, the following `input` block would be appropriate:
```
input:
  currents <- current
  inh_spikes <- inhibitory spike
  exc_spikes <- excitatory spike
end
```

Please note that it is equivalent if either both `inhibitory` and `excitatory` are given or none of them at all. If only a single one of them is given, another line has to be present and specify the inverse keyword. Failure to do so will result in a translation error.

If there is more than one line specifying a `spike` or `current` port with the same sign, a neuron with multiple receptor types is created. In this case, a `receptor_types` entry is created in the status dictionary, which maps port names to numeric port indices in NEST. The receptor type can then be selected in NEST during [connection setup](http://nest-simulator.org/connection_management/#receptor-types).

### Output

Each neuron model can only send a single type of event. The type of the event has to be given in the `output` block. Currently, however, only spike output is supported.
```
output: spike
```

Please note that this block is *not* terminated with the `end` keyword.

## Synaptic input

NESTML has two dedicated functions to ease the summation of synaptic input.

`curr_sum` is a function that has two arguments. The first is a function *I* of *t* which is either a `shape` function (see [Synaptic response](#synaptic-response)) or a function that is defined by an ODE plus initial values (see [Systems of ODEs](#systems-of-odes)). The second is a `spike` input buffer (see [Synaptic input](#synaptic-input)). `curr_sum` takes every weight in the `spike` buffer and multiplies it with the `shape` function *I*<sub>shape</sub> shifted by it's respective spike time *t<sub>i</sub>*. In mathematical terms, it thus performs the following operation:

<!--- $\large \sum_{t_i\le t, i\in\mathbb{N}}\sum_{w\in\text{spikeweights}} w I_{\text{shape}}(t-t_i)=\sum_{t_i\le t, i\in\mathbb{N}} I_{\text{shape}}(t-t_i)\sum_{w\in\text{spikeweights}} w$ --->
![equation](https://latex.codecogs.com/svg.latex?%5Clarge%20%5Csum_%7Bt_i%5Cle%20t%2C%20i%5Cin%5Cmathbb%7BN%7D%7D%5Csum_%7Bw%5Cin%5Ctext%7Bspikeweights%7D%7D%20w%20I_%7B%5Ctext%7Bshape%7D%7D%28t-t_i%29%3D%5Csum_%7Bt_i%5Cle%20t%2C%20i%5Cin%5Cmathbb%7BN%7D%7D%20I_%7B%5Ctext%7Bshape%7D%7D%28t-t_i%29%5Csum_%7Bw%5Cin%5Ctext%7Bspikeweights%7D%7D%20w).

When the sum above is used to describe conductances instead of currents, the function `cond_sum` can be used. It does exactly the same as `curr_sum` and can be used in exactly the same way and in the same cases, but makes explicit that the neural dynamics are based on synaptic conductances rather than currents.

For modeling post synaptic responses with delta functions, `curr_sum` and `cond_sum` can be called with the keyword `delta` as first argument instead of a `shape` function.

## Handling of time

To retrieve some fundamental simulation parameters, two special functions are built into NESTML:

* `resolution` returns the current resolution of the simulation in ms. This can be set by the user using the PyNEST function `nest.SetKernelStatus({"resolution": ...})`.
* `steps` takes one parameter of type `ms` and returns the number of simulation steps in the current simulation resolution.

These functions can be used to implement custom buffer lookup logic, but should be used with care.

## Equations

### Synaptic response

A `shape` is a function of *t* (which represents the current time of the system), that corresponds to the shape of a postsynaptic response, i.e. the function *I*<sub>shape</sub>(*t*) with which incoming spike weights *w* are multiplied to compose the synaptic input *I*<sub>syn</sub>:

<!--- $\large I_{\text{syn}}=\sum_{t_i\le t, i\in\mathbb{N}}\sum_{w\in\text{spikeweights}} w I_{\text{shape}}(t-t_i)$ --->
![equation](https://latex.codecogs.com/svg.latex?%5Clarge%20I_%7B%5Ctext%7Bsyn%7D%7D%3D%5Csum_%7Bt_i%5Cle%20t%2C%20i%5Cin%5Cmathbb%7BN%7D%7D%5Csum_%7Bw%5Cin%5Ctext%7Bspikeweights%7D%7D%20w%20I_%7B%5Ctext%7Bshape%7D%7D%28t-t_i%29).

### Systems of ODEs

In the `equations` block one can define a system of differential equations with an arbitrary amount of equations that contain derivatives of arbitrary order. When using a derivative of a variable, say *V*, one must write: *V*'. It is then assumed that *V*' is the first time derivate of *V*. The second time derivative of *V* is *V*'', and so on. If an equation contains a derivative of order *n*, for example *V*<sup>(*n*)</sup>, all initial values of *V* up to order *n*-1 must be defined in the `state` block. For example, if stating
```
V' = a * V
```
in the `equations` block,
```
V mV = 0mV
```
has to be stated in the `state` block. If the initial values are not defined in `state` it is assumed that they are zero and unit checks are no longer possible.

The content of spike and current buffers can be used by just using their plain names. NESTML takes care behind the scenes that the buffer location at the current simulation time step is used.

## Dynamics and time evolution

`update:` inside this block the current time can be accessed via the variable `t`

> `integrate_odes`: Explain the current behavior

> `process_spikes()`: Do we still have this function?

`emit_spike()`: calling this function in the `update`-block results in firing a spike to all target neurons and devices time stamped with the current simulation time.

### Solver selection

Currently there is support for GSL and exact integration.

### Concepts for refractoriness

In order to model refractory and non-refractory states, two variables are necessary. The first variable (`t_ref`) defines the duration of the refractory period. The second variable (`ref_counts`) specifies the time of the refractory period that has already passed. It is initialized with 0 (the neuron is non-refractory) and set to the refractory offset every time the refractoriness condition holds. Else, the refractory offset is decremented.

```
parameters:
  t_ref ms = 5ms
end
internals:
  ref_counts  = 0
end
update:

  if ref_count == 0: # neuron is in non-refractory state
    if <refractoriness_condition>:
      ref_counts = steps(t_ref) # make neuron refractory for 5ms
    end
  else:
    ref_counts  -= 1 # neuron is refractory
  end

end
```

## Setting and retrieving model properties

* All variables in the `state` and `parameters` blocks are added to the status dictionary of the neuron.
* Values can be set using `nest.SetStatus(<gid>, <variable>, <value>)` where `<variable>` is the name of the corresponding NESTML variable.
* Values can be read using `nest.GetStatus(<gid>, <variable>)`. This call will return the value of the corresponding NESTML variable.

## Recording values with devices

* All values in the `state` block are recordable by a `multimeter` in NEST.
* The `recordable` keyword can be used to also make variables in other blocks (`parameters, internals`) available to recording devices.
```
parameters:
  recordable t_ref ms = 5ms
end
```

## Guards

Variables which are defined in the `state` and `parameters` blocks can optionally be secured through guards. These guards are checked during the call to `nest.SetStatus()` in NEST.

```
block:
  <declaration> [[<boolean_expression>]]
end

parameters:
  t_ref ms = 5ms [[t_ref >= 0ms]] # refractory period cannot be negative
end
```
