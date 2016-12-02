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


## Handling synaptic input

NESTML has two dedicated functions to ease the summation of synaptic input.

`curr_sum` is a function that has two arguments. The first is a `shape` function (see Equations) or a function that is defined by an ODE plus initial values (see ODEs) *I* of *t*. The second is a `spike` input buffer (see Input). `curr_sum` takes every weight in the `spike` buffer and multiplies it with the `shape` function *I*<sub>shape</sub> shifted by it's respective spike time *t<sub>i</sub>*. I.e.

<!--- $\large \sum_{t_i\le t, i\in\mathbb{N}}\sum_{w\in\text{spikeweights}} w I_{\text{shape}}(t-t_i)=\sum_{t_i\le t, i\in\mathbb{N}} I_{\text{shape}}(t-t_i)\sum_{w\in\text{spikeweights}} w$ --->
![equation](https://latex.codecogs.com/svg.latex?%5Clarge+%5Csum_%7Bt_i%5Cle+t%2C+i%5Cin%5Cmathbb%7BN%7D%7D%5Csum_%7Bw%5Cin%5Ctext%7Bspikeweights%7D%7D+w+I_%7B%5Ctext%7Bshape%7D%7D%28t-t_i%29%3D%5Csum_%7Bt_i%5Cle+t%2C+i%5Cin%5Cmathbb%7BN%7D%7D+I_%7B%5Ctext%7Bshape%7D%7D%28t-t_i%29%5Csum_%7Bw%5Cin%5Ctext%7Bspikeweights%7D%7D+w).

When the sum above is used to decribe conductances instead of currents, the function `cond_sum` can be used. It does exactly the same as `curr_sum` and can be used in exactly the same way and in the same cases, but makes explicit the the neural dynamics are based on synaptic conductances rather than currents.

For modeling post synaptic responses with delta functions, `curr_sum` is called with the keyword  `delta` as first argument instead of the `shape` function.

## Handling of time

 `resolution`
 `steps`

## Equations

### Synaptic response

A `shape` should be a function of *t* (which represents the current time of the system), that represents the shape of a postsynaptic response, i.e. the function *I*<sub>shape</sub>(*t*) with which incoming spike weights *w* are multiplied to compose the synaptic input *I*<sub>syn</sub>:

<!--- $\large I_{\text{syn}}=\sum_{t_i\le t, i\in\mathbb{N}}\sum_{w\in\text{spikeweights}} w I_{\text{shape}}(t-t_i)$ --->
![equation](https://latex.codecogs.com/svg.latex?%5Clarge+I_%7B%5Ctext%7Bsyn%7D%7D%3D%5Csum_%7Bt_i%5Cle+t%2C+i%5Cin%5Cmathbb%7BN%7D%7D%5Csum_%7Bw%5Cin%5Ctext%7Bspikeweights%7D%7D+w+I_%7B%5Ctext%7Bshape%7D%7D%28t-t_i%29).

### Systems of ODEs

In the `equations` block one can define a system of differential equations with an arbitrary amount of equations that contain derivatives of arbitrary order.
When using a derivative of a variable, say *V*, one must write: *V*'. It is then assumed that *V*' is the first time derivate of *V*. The second time derivative of *V* is *V*'', and so on.
If an equation contains a derivative of order *n*, for example *V*<sup>(*n*)</sup>, all initial values of *V* up to order *n*-1 must me defined in the `state` block. For example, one could state
```
V' = a * V
```
in the `equations` block, but would also have to state
```
V mV = 0mV
```
in the `state` block. If the initial values are not defined in `state` it is assumed that they are zero and unit checks are no longer possible.


  access to spike and current buffers


  Currently support for GSL and exact integration, if possible



## Dynamics and time evolution

   `update()` has access to the current time via the variable `t`

   `integrate_odes`

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
