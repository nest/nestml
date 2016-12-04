# NESTML language documentation

NESTML has a concise syntax that avoids clutter in the form of
semicolons, curly braces or tags as known from other programming or
markup languages. Instead it concentrates on the domain concepts
needed to efficiently write down neuron models and their equations.

NESTML files are expected to have the filename extension
`.nestml`. There is no connection between model and file name and each
file may contain one or more models. Models that shall be compiled
into one extension module for NEST have to reside in the same
directory.

In order to give the users of NESTML complete freedom, we provide a
full programming language. This programming language is used in the
update block and function block. It provides the following features:

### Physical units and data types
NESTML provides the following types
#### Primitive data types
* `real`: corresponds to the `double` data type in C++. Its literals are: 42.0,
-0.42, .44
* `integer`: corresponds to the `int` data type in C++. Its literals are: 42, -7
* `boolean`: corresponds to the `bool` data type in C++. Its literals are only:
`true`, `false`
* `string`: String data type. Its literals are: "Bob", ""
* `void`: corresponds to the `void` data type in C++. No literals possible.

#### Physical units
A physical unit in NESTML can be either simple unit or a complex physical unit.
The idea is based on the Le Système internationale d’unités.
A simple physical unit is composed of a magnitude prefix and the name of the
unit.

|Quantity | SI Symbol | SI Name | NESTML Name|
|-|-|-| - |
| length | L | metre  | m |
| mass | M | kilogram | kg |
| time | T | second | s |
| electric current | I | ampere | A |
| temperature | $\Theta$ | kelvin | K |
| amount of substance | N | mole | mol |
| luminous intensity | J | candela | cd |

Theoretically, any unit can be expressed as a combination of these seven units.
In order to support convenience in modeling, NESTML provides following
derived units:

| | | | |
|-|-|-|-|
| Bq | C | F | Gy |
| Hz | J | N | Ohm |
| Pa | S | Sv | TH |
| V | W  | Wb | kat | |

Units can have at most one of the following prefixes:

|Factor | SI Name | NESTML prefix | Factor | SI Name | NESTML prefix
|-|-|-|-|-|-|
|$10^{-1}$ | deci | d | $10^1$ | deca | da |
|$10^{-2}$ | centi | c | $10^2$ | hecto | h |
|$10^{-3}$ | milli | m | $10^3$ | kilo | k |
|10^{-6}$ | micro | mu | $10^6$ | mega | M |
|$10^{-9}$ | nano | n | $10^9$ | giga | G |
|10^{-12}$ | pico | p | $10^{12}$ | tera | T |
|$10^{-15}$ | femto | f | $10^{15}$ | peta | P |
|$10^{-18}$ | atto | a | $10^{18}$ | exa | E |
|$10^{-21}$ | zepto | z | $10^{21}$ | zetta | Z |
|$10^{-24}$ | yocto | y | $10^{24}$ | yotta | Y |

Finally, physical units can be combined to complex unit types.
#### Type and unit checks
NESTML checks type correctness of all expressions. For assignments, declarations
with an initialization and function calls type conformity is checked.
NESTML supports conversion of an `integer` variable to a `real` variable. Also
 conversion between `unit`-typed and `real`-typed variables is possible. However,
these conversions are reported as warnings.

### Basic elements of the embedded programming language
Basic elements can be: declarations, assignments or function calls.
#### Declarations
---------------------------------------------
```
a, b, c real = -0.42
d integer = 1
e string = "Bob"
f mV   = -2e12mV
```
#### Assignments
---------------------------------------------
NESTML supports plain or compound assignments. The lefthand side of the assignments
is always an variable. The righthand side can be an arbitrary expression of a type
compatible to the lefthand side. E.g. for a numeric variable `n`
* assignment: ```n = 10```
* compound sum: ```n += 10```
* compound minus: ```n -= 10```
* compound product: ```n *= 10```
* compound quotient: ```n /= 10```

#### Functions
---------------------------------------------
| | | | |
|-|-|-| - |
| cond_sum | curr_sum |  delta | emit\_spike |
| exp   | expm1 | info | integrate\_odes |
| log | max | pow | random |
| randomInt    | resolution | steps | warning |

### Control structures
NESTML supports loop- and conditional control-structures.
#### Loops
---------------------------------------------
```
while <boolean_expression>:
  <Statements>
end

x integer = 0
while x <= 10:
  <statements>
end
```

```
for <existing_variable_name> in <lower_bound> ... <upper_bound>:
  <statements>
end

x integer = 0
for x in 1 ... 5:
  <statements>
end
```

```
for <existing_variable_name> in <integer_lower_bound> ... <integer_upper_bound> step <integer_step_size>:
  <statements>
end

x integer
for x in 1 ... 5 step 2:
  <statements>
end
```

```
for <existing_variable_name> in <real_lower_bound> ... <real_upper_bound> step <real_step_size>:
  <statements>
end

x real
for x in 0.1 ... 0.5 step 0.1:
  Statements
end
```

#### Conditionals
---------------------------------------------
NESTML supports the following types of if-else conditionals. The indentation is
not important. The first example shows if conditional composed of a single if
block:

```
if <boolean_expression>:
  <statements>
end

if 2 < 3:
  <statements>
end
```

The following example shows an if-else block:
```
if <boolean_expression>:
  <statements>
else:
  <statements>
end

if 2 < 3:
  <statements>
else:
  <statements>
end
```
The  following examples shows usage of the `elif`-conditionals. After an `if`
condition an arbitrary number of `elif` conditions can follow. The last condition
block always concludes with an `end` keyword.
```
if <boolean_expression>:
  <statements>
elif <boolean_expression>:
  <statements>
else:
  <statements>
end

if 2 < 3:
  <statements>
elif 4>6:
  <statements>
else:
  <statements>
end

if 2 < 3:
  <statements>
elif 4>6:

  <statements>
end
```

The last example shows nesting of conditionals.
```
if 1 < 4:
  <statements>
  if 2 < 3:
    <statements>
  end
end
```
### Expressions and operators
Expressions in NESTML can be specified in a recursive fashion. First, terms are
valid expressions.
#### Terms:
All variables, literals, and functions are valid terms. Variables are names of
user defined or predefined variables (```t, e ```)

#### List of operators
For any two valid numeric expressions a, b, a boolean expression c, and an
integer expression n the following operators produce valid expressions.

| Operator | Description | Examples |
|-|-|-|
|() | Expressions with parentheses | (a) |
|**|  Power operator. Power is right associative, e.g. a \*\* b \*\* c corresponds a \*\* (b \*\* c) | a \*\* b |
|+,  -, ~| unary plus, unary minus, bitwise negation | -a, ~c|
|*, /,%  | Multiplication, Division and Modulo-Operator | a * b, a % b|
|+, -| Addition and Subtraction |a + b, a - b|
|<<, >>| & Left and right bit shifts |a << n, a >> n|
|&, &#124;,^ | Bitwise and, or and xor | a&b, a&#124;b, a~b |
|<, <=, ==, !=, >=, >|  Comparison operators |a <= b, a != b|
|not, and, or| & Logical conjunction, disjunction and negation |not b, b or b|
|?:| The ternary logical operator |c?a:b|

## Blocks

To structure NESTML files, all content is split into blocks. Blocks
begin with a keyword specifying the type of the block followed by a colon.
They are closed with the keyword `end`. Indentation inside a block is not
mandatory but recommended for better readability. Each block must only
occur at most once on each level. Some of the blocks are required to occur in
every neuron model.

### Syntax
```
<block_type> [<args>]:
  ...
end
```

### Block types

`neuron` *`<name>`*
: This block contains the description of a neuron model called
  `<name>`. The content will be translated into a single neuron model
  that can be instantiated in NEST using `nest.Create(<name>)`. This
  is the top-level block of a model specification and all following
  blocks are contained in this block. The block terminates with the `end` keyword.

`parameters:`
:  The block terminates with the `end` keyword.

`state`
:  The block terminates with the `end` keyword.

`internals`
:  The block terminates with the `end` keyword.

`equations`
:  The block terminates with the `end` keyword.

`input`
:  The block terminates with the `end` keyword.

`output`
: Defines which kinds of events the neuron can fire. Currently, only `spike` is
supported.

`update`
: The block terminates with the `end` keyword.

`function`
: The block terminates with the `end` keyword.


## Neuronal interactions

### Input
    `inhibitory`
    `excitatory`

### Output

Each neuron model in NESTML can only send a single type of event. The
type of the event has to be given in the `output` block.

Currently only spike output is supported.


## Predefined functions, variables and keywords

 `curr_sum`

 `cond_sum`

 `delta`

 `resolution`: returns the current resolution of the simulation. Can vary dependent on
 the `nest.SetKernelStatus({"resolution": ...})` setting.

 `steps`: takes one parameter of the type `ms` and returns the number of simulation
 ticks which are needed.

## Equations

  `shape` notation

  ODEs:
    * syntax
    * orders and initial values

  access to spike and current buffers


  Currently support for GSL and exact integration, if possible



## Dynamics and time evolution

   `update()` has access to the current time via the variable `t`

   `integrate_odes`

   `process_spikes()`

   emit_spike(): calling this function in the `update`-block results in firing
   a spike through the neuron.
### Concepts for refractoriness
In order to model refractory and non-refractory states, two variables are
necessary. First variable `t_ref` defines the duration of the refractoriness period.
The second variable specifies the current delay of the refractory period. It is
initialized with 0 and set to the refractory offset every time the refractoriness
condition holds. Otherwise, the refractory offset is decremented.

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
      ref_counts = steps(t_ref)
    end
  else:
    ref_counts  -= 1 # neuron is refractory
  end

end
```

## Setting and retrieving model properties

  * Everything in `state` and `parameters` is added to the status dict.
  * All values can be set and read


## Recording values with devices

  * All values in state are recordable
  * `recordable` can be used to make variables in other block available
  to recording devices


## Guards
Variables which are defined in the parameter block can be optionally secured
through an optional guards. This guard is checked during `nest.SetStatus(n, ...)`
call.
```
parameters:
  t_ref ms = 5ms [[t_ref >= 0ms]] # refractory period cannot be negative
end
```

## Comments and documentation
