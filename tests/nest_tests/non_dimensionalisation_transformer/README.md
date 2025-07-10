# Tests for Non-Dimensionilisation-Transformer

The transformer relates to [PR-1217](https://github.com/nest/nestml/pull/1217) and [Issue-984](https://github.com/nest/nestml/issues/984).
In a first instance the correct transformation of the expressions inside a NESTML file should be checked.

The tests should include:
- checking for all metric prefixes
- checking for nested expressions with metric prefixes
- checking that transformations occur in every part of the NESTML file units are specified
- checking of transformation for derived variables
- checking for transformation of reciprocal units/ expressions with reciprocal units
  - does it make sense for these to have the same desired unit?
  - E.g.: desired unit of 'electrical potential' is mV -> should variables with physical type of '1/V' also be then expressed as '1/mV' post transformation?
  - see *test_reciprocal_unit_in_paramterblock*
- checking additional parenthesis are set correctly

In a second instance the unit arithmetic and consistency of physical types needs to be checked pre-transformation after the original AST is built:
- will the expression on the RHS of an equation yield a unit that is a unit of what is specified on the LHS of the equation?
- How should exceptions be handled, for example if LHS is 'V' but result on RHS is '1/V'?
- Are the arguments inside of functions like exp(), log(), sin(), etc. dimensionless or has the user made a mistake?
- What should happen if unknown units are encountered?

### test_exp_in_equationblock
This test checks if the transformer can deal with functions like exp() in the equation block.
The target unit for V_exp'(s) is mV as the 1/s is being carried implicitly by declaring the variable with a tick, signifying that it is a derived unit with respect to time

### test_real_factor_in_stateblock
This test checks if state block expressions with a RHS with a unit being multiplied by a real factor a LHS with type 'real' will get processed correctly.
The target unit JSON file is
```JSON
{"quantity_to_preferred_prefix": 
      {
      "electrical potential": "m",    # needed for V_m_init and U_m
      "electrical current": "1",      # needed for currents not part of the test
      "electrical capacitance": "1",  # needed for caps not part of the test
      }
}
```
Before the transformation the relevant .NESTML should read

```NESTML
    state:
        U_m real = b * V_m_init          # Membrane potential recovery variable
        
    parameters:
        b real = 0.2                     # sensitivity of recovery variable
        V_m_init mV = -65 mV             # Initial membrane potential  
```
After the transformation it should read
```NESTML
    state:
        U_m real = b * V_m_init          # Membrane potential recovery variable
        
    parameters:
        b real = 0.2                     # sensitivity of recovery variable
        V_m_init real = 1e3 * (-65e-3)   # Initial membrane potential  
```

### test_inline_expression_in_equationblock
This test checks if the transformer can deal with inline expressions in the equation block. Additionally there is an exp() in the expression

The target unit JSON file is
```JSON
{"quantity_to_preferred_prefix": 
      {
      "electrical potential": "m",    # needed for V_m_init
      "electrical current": "p",      # needed for I_spike_test
      "electrical capacitance": "1",  # needed for caps not part of the test
      }
}
```

Before the transformation the relevant .NESTML should read
```NESTML
    equations:
        inline I_spike_test A = 30.0 nS * (-V_m_init / 130e3) * exp(((-80 mV) - (-20 mV)) / 3000 uV)
        
    parameters:
        V_m_init mV = -65 mV     # Initial membrane potential
```

After the transformation it should read
```NESTML
    equations:
        inline I_spike_test real = 1e12 * ((30.0 * 1e-9) * ((-V_m_init * * 1e-3)/ 130e3) * exp(((-80 * 1e-3) - (-20 * 1e-3)) / (3000 * 1e-6)))
        
    parameters:
        V_m_init real = 1e3 * (-65 * 1e-3)     # Initial membrane potential
```

### test_reciprocal_unit_in_paramterblock
This test checks if the transformer can deal with reciprocal units on the LHS of an equation inside the parameter block.

The target unit JSON file is
```JSON
{"quantity_to_preferred_prefix": 
      {
      "electrical potential": "m",    # needed for V_exp, alpha_exp
      "electrical current": "1",      # needed for I_spike_test
      "electrical capacitance": "1",  # needed for caps not part of the test
      }
}
```
Before the transformation the relevant .NESTML should read
```NESTML
    state:
        V_exp V = 2500 uV + V_m_init * exp(alpha_exp * 10 V)
        
    parameters:
        V_m_init mV = -65 mV                      # Initial membrane potential
        alpha_exp 1/V = 2 /(3 MV)                 # this could be a factor for a voltage inside of en exp(), e.g. exp(alpha_exp * V_test)
```

After the transformation it should read
```NESTML
    state:
        V_exp V = (2500 * 1e-6) + (V_m_init * 1e-3) * exp((alpha_exp * 1e-6) * 10)
        
    parameters:
        V_m_init real = 1e3 * (-65 * 1e-3)        # Initial membrane potential
        alpha_exp real = 1e-3 * (2 / (3 * 1e6))   # this could be a factor for a voltage inside of en exp(), e.g. exp(alpha_exp * V_test)
```

### test_giga - test_atto
These tests will check if the standardized metric prefixes in the range of Giga- to Atto- can be resolved.
The prefixes Deci- and Deca- are probably little used in a neuroscience context.
The test for Femto- includes the use of a combined physical type, the "magnetic field strength".