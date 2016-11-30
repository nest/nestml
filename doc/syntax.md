# NESTML language documentation

NESTML has a concise syntax that avoids clutter in the form of
semicolons, curly braces or tags as known from other programming or
z languages. Instead it concentrates on the domain concepts
needed to efficiently write down neuron models and their equations.

NESTML files are expected to have the filename extension
`.nestml`. There is no connection between model and file name and each
file may contain one or more models. Models that shall be compiled
into one extension module for NEST have to reside in the same
directory.

In order to give the users of NESTML complete freedom, we provide a
full programming language with the following features:

### Physical units and data types
NESTML provides
*  `real`, `integer`, `boolean`,
*  Physical units
*  Type and unit checks

### Control structures

* declarations
```
a, b, c real = -0.42
d integer = 1
e string = "Bob"
f mV   = -2e12mV
```
* loops

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
* conditionals


### Expressions and operators

* list of operators

## Blocks

To structure NESTML fails, all content is split into blocks. Blocks
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
  blocks are contained in this block.

`parameters`
: blabla

`state`
: blabla

`internals`
: blabla

`equations`
: blabla

`input`
: blabla

`output`
: blabla

`update`
: blabla

`function`
: blabla


## Neuronal interactions

### Input
    `inhibitory`
    `excitatory`

### Output

Each neuron model in NESTML can only send a single type of event. The
type of the event has to be given in the `output` block.

Currenly only spike output is supported.


## Predefined functions, variables and keywords

 `curr_sum`

 `cond_sum`

 `delta`

 `resolution`
 `steps`

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

   concepts for refractoriness

   emit_spike()


## Setting and retrieving model properties

  * Everything in `state` and `parameters` is added to the status dict
  * All values can be set and read


## Recording values with devices

  All values in state are recordable

  `recordable` can be used to make variables in other block available
  to recording devices


## Guards

## Comments and documentation
