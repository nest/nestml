# NESTML language documentation

NESTML has a concise syntax that avoids clutter in the form of
semicolons, curly braces or tags as known from other programming or
description languages. Instead it concentrates on the domain concepts
needed to efficiently write down neuron models and their equations.

NESTML files are expected to have the filename extension
`.nestml`. There is no connection between model and file name and each
file may contain one or more models. Models that shall be compiled
into one extension module for NEST have to reside in the same
directory.

In order to give the users of NESTML complete freedom, we provide a
full programming language with the following features:

### Physical units and data types

*  `real`, `integer`, `boolean`
*  Physical units
*  Type and unit checks

### Control structures

* loops
* conditionals
* declarations

### Expressions and operators

* list of operators

## Blocks

To structure NESTML files, all content is split into blocks. Blocks
begin with a keyword specifying the type of the block followed by zero
or more arguments (depending on the type) and a colon. They are
closed with the keyword `end`. Indentation inside a block is not
mandatory but recommended for better legibiliy. Each block must only
occur once on each level.

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

Curr_sum is a function that has two arguments

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




