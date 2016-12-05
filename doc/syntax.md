# NESTML language documentation

NESTML has a concise syntax that avoids clutter in the form of
semicolons, curly braces or tags as known from other programming or
markup languages. Instead it concentrates on the domain concepts
needed to efficiently write down neuron models and their equations.

NESTML files are expected to have the filename extension
`.nestml`. There is no connection between model and file name. Each
file may contain one or more neuron models. Models that shall be compiled
into one extension module for NEST have to reside in the same
directory. The name of the model corresponds to the name of the folder.

In order to give the users of NESTML complete in implementing neuron's dynamics
freedom, we provide a full programming language. This programming language
is used in the update block and function block. It provides the following features:

### Data types and physical units
Data types define types of variables, function's parameters and
return values of functions. NESTML provides the following primitive types
and physical data types.
#### Primitive data types
* `real`: corresponds to the `double` data type in C++. Its literals are: 42.0,
-0.42, .44
* `integer`: corresponds to the `int` data type in C++. Its literals are: 42, -7
* `boolean`: corresponds to the `bool` data type in C++. Its literals only are:
`true`, `false`
* `string`: String data type. Its literals are: "Bob", ""
* `void`: corresponds to the `void` data type in C++. No literals are possible.
It can be used to identify a function without the return value.

#### Physical units
A physical unit in NESTML can be either a simple physical unit or a complex
physical unit. A simple physical unit is composed of a optional magnitude prefix
and the name of the unit.

The following table present seven base units, which can be used to specify any
physical unit. This idea is based on the Le Système internationale d’unités.

|Quantity | SI Symbol | SI Name | NESTML Name|
|-|-|-| - |
| length | L | metre  | m |
| mass | M | kilogram | kg |
| time | T | second | s |
| electric current | I | ampere | A |
| temperature | $\Theta$ | kelvin | K |
| amount of substance | N | mole | mol |
| luminous intensity | J | candela | cd |

All remaining physical units are called derived units. Theoretically, any physical
unit can be expressed as a combination of these seven
units. In order to support convenience in modeling, NESTML provides following
derived units as built-in data types:

| | | | |
|-|-|-|-|
| Bq | C | F | Gy |
| Hz | J | N | Ohm |
| Pa | S | Sv | TH |
| V | W  | Wb | kat | |

Units can have at most one of the following magnitude prefixes:

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

Finally, simple physical units can be combined to complex units. For this,
multiplication (\*)-, division(\)- and power(\*\*)-operators can be used.
```
mV*mV*nS**2/(mS*pA)
```
There is a special cases for the expressions of the form `physical_unit ** -1`.
It can be expressed as `1\physical_unit`
```
(ms*mV)**-1 is equivalent to 1/(ms*mV)
```

#### Physical unit literals
* Simple unit literals are composed of a number with the type name (with or without a whitespace).
Complex unit literals are composed of a number and type inside of square brackets.
Also simple units can be put inside of square brackets.  

```
<number> <unit_type>
<number> [<unit_type>]

a mV = 1mV
aa mV = 1[mV]
b mV/ms = 1[mV/ms]
```
#### Type and unit checks
NESTML checks type correctness of all expressions. For assignments, declarations
with an initialization and function calls type conformity is checked also.
NESTML supports conversion of an `integer` to `real`. Also
conversion between `unit`-typed and `real`-typed variables is possible. However,
these conversions are reported as warnings. Finally, there is no conversion
between numeric types and boolean types.

### Basic elements of the embedded programming language
Basic elements are: declarations, assignments, function calls and return statements.
#### Declarations
---------------------------------------------
Declarations are composed of a non empty list of comma separated names. A
valid name starts with a letter or underscore or dollar character. Further it
can contain arbitrary number of letters, numbers and underscores.
Formally, a valid name satisfies the following regular expression:
` ( 'a'..'z' | 'A'..'Z' | '_' | '$' )( 'a'..'z' | 'A'..'Z' | '_' | '0'..'9' | '$' )*`.
A type is any of the valid NESTML types. The type of the initialization expression
must be compatible to the type of the declaration.
```
<list_of_comma_separated_names> <type> (= initialization_expression)?

a, b, c real = -0.42
d integer = 1
e string = "Bob"
f mV   = -2e12mV
```
#### Assignments
---------------------------------------------
NESTML supports simple or compound assignments. The lefthand side of the assignments
is always a variable. The righthand side can be an arbitrary expression of a type
which is compatible to the lefthand side. E.g. for a numeric variable `n`:
* simple assignment: ```n = 10```
* compound sum: ```n += 10 corresponds to n = n + 10```
* compound minus: ```n -= 10 corresponds to n = n - 10```
* compound product: ```n *= 10 corresponds to n = n * 10```
* compound quotient: ```n /= 10 corresponds to n = n - 10```



#### Function call
---------------------------------------------
A function call is composed of the function name and the list of required
parameters.

```
<function_name>(<list_of_arguments>)

max(a*2, b/2)
```
##### Predefined Functions
---------------------------------------------
| | | | |
|-|-|-| - |
| cond_sum | curr_sum |  delta | emit\_spike |
| exp   | expm1 | info | integrate\_odes |
| log | max | pow | random |
| randomInt    | resolution | steps | warning |
#### Return statement
The return expression can be only used inside of the function block.
```
return (<expression>)?

if a > b:
  return a
else:
  return b
end
```
### Control structures
NESTML supports loop- and conditional control-structures.
#### Loops
---------------------------------------------
The following while and for loops are possible.

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
All variables, literals, and function calls are valid terms. Variables are names of
user defined or predefined variables (`t, e`)

#### List of operators
For any two valid numeric expressions `a, b`, a boolean expression `c`, and an
integer expression `n` the following operators produce valid expressions.

| Operator | Description | Examples |
|-|-|-|
|() | Expressions with parentheses | (a) |
|**|  Power operator. Power is right associative, e.g. a \*\* b \*\* c corresponds a \*\* (b \*\* c) | a \*\* b |
|+,  -, ~| unary plus, unary minus, bitwise negation | -a, ~c|
|*, /,%  | Multiplication, Division and Modulo-Operator | a * b, a % b|
|+, -| Addition and Subtraction |a + b, a - b|
|<<, >>| & Left and right bit shifts |a << n, a >> n|
|&, &#124;,^ | Bitwise `and`, `or` and `xor` | a&b, a&#124;b, a~b |
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
:  This block is composed of a list with variable declarations. This block is
supposed to contain variables
which remain constant during the concrete simulation, but they can vary among
different simulations or instantiations neuron of the same neuron. The block
terminates with the `end` keyword.

`state:`
: This block is composed of a list with variable declarations. These variables are supposed to
model the time dependent  state of the neuron. Only variables form this block can be refined with
differential equations. The block terminates with the `end` keyword.

`internals:`
:  This block is composed of a list with variable declarations. These variables
are supposed to be constant during the simulation run. Therefore, its initialization
expression can only reference parameter- or another internal-variables. The block
terminates with the `end` keyword.

`equations:`
: This block is composed of shape definitions and differential equations. In will
be explained in further details later in the manual. The block terminates with
the `end` keyword.

`input:`
: The block is composed of a list of input ports. In will
be explained in further details later in the manual. The block terminates with the `end` keyword.

`output:`
: Defines which kinds of events the neuron can fire. Currently, only `spike` is
supported. No `end` is necessary.
```
output: spike
```
`update:`
: Inside the block arbitrary code in the introduced programming language can be
implemented. The block terminates with the `end` keyword.

`function *`<name>`*([<list_of_arguments>]) <return_type>?:`
: `function ([<args>]`.
The function has an unique name and a list of arguments between round brackets.
Inside the block arbitrary code in the introduced
programming language can be implemented. The function definitions
terminates with the `end` keyword.
```
function <name>(<list_of_arguments>) <return_type>?:
  <statements>
end

function devide(a real, b real) real:
  return a/b
end
```

## Neuronal interactions

### Input
Input block is composed of input lines. Every input line of the form:
```
port_name <- inhibitory? excitatory? (spike | current)
```
There are three basic constilations for a valid input block.
* It is composed of the single port, which is either `spike` or `current`,
that receives as well positive weighted spikes as well as negative weighted spikes.
* It is composed of two ports. The first port is an `inhibitory` port, the second
port is an `excitatory` port. In that case, spikes are routed based on their
weight. Positive weighted spikes go to the `excitatory` port, negative weighted
spikes go to the `inhibitory` port. In that case both ports are mandatory.
* There are more the one `spike` or `current` port. In that case, a multisynapse
neuron is created. The `receptor_types` entry is created in the dict. It maps
port names to its port indexes in NEST.
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

  * Access to spike and current buffers: all buffers can be be accessed through their plain names.


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
The second variable `ref_counts` specifies the current delay of the refractory period. It is
initialized with 0 (the neuron is non-refractory) and set to the refractory offset
every time the refractoriness condition holds. Otherwise, the refractory offset
is decremented.

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

  * Everything in `state` and `parameters` is added to the status dict.
  * All values can be set and read `nest.SetStatus(n, {var_name:var_value})`

## Recording values with devices

  * All values in the `state` block are recordable
  * `recordable` can be used to make variables in other blocks (`parameters, internals`)
  available to recording devices. For this, a declaration hast to be prepended
  with the `recordable` keyword.

  ```
  parameters:
    recordable t_ref ms = 5ms
  end
  ```

## Guards
Variables which are defined in the in `state` and `parameters` blocks can be
optionally secured through a guard. This guard is checked during
`nest.SetStatus(n, ...)` call in NEST.
```
block:
  <declaration> [[<boolean_expression>]]
end

parameters:
  t_ref ms = 5ms [[t_ref >= 0ms]] # refractory period cannot be negative
end
```

## Comments and documentation
