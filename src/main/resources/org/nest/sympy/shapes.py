"""
   This script provides the framework for receiving properties
   of so called 'shapes' that are relevant for constructing an
   apropriate evolution scheme for the ODEs in which the shapes 
   occur. A shape is a postsynaptic function which can be used
   to convolve spiking input, whose properties are often relevant
   for the construction of a good evolution schemes. Shape functions
   can be defined either as a function of `t` or an ODE.
    
   Here we provide a class, `ShapeFunction` that can be called
   with a chosen name of the shape and it's mathematical discription;
   it checks for any given fuction of positive t, i.e. the shape, if
   it satisfies a linear homogeneous ODE of order 1,...,10:
    
   Example:
   ========
    
   shape_alpha = ShapeFunction("shape_alpha", "e / tau * t * exp(-t / tau)") 
    
   The class will provide the properties name, order,
   nestml_ode_form, derivative factors and intitial_values.
    
   in this example: 
   'name' will be 'shape_alpha' as a symbolic expression
    
   'order' is 2, as the function above satisfies a homogeneos ODE of order 2
    
   `nestml_ode_form` is 
   shape_alpha'' = -1/tau**2 * shape_alpha -2/tau * shape_alpha'
   this is the linear homogeneous ODE that shape_alpha satisfies
    
   `derivative_factors` will be a list [-1/tau**2, -2/tau]
   these are the factor occuring in the ODE above 
    
   `initial_values` is [0, e/tau]. These are the initial values of
   all derivatives of occuring on the right hand side of the ODE. 
   From lowest derivative to highest.
    
    
   Also we provide a class 'ShapeODE'. An instance of `ShapeODE` is 
   defined with the name of the shape (i.e a function of `t`
   that satisfies a certain ODE), the variables on the lefthandside 
   of the ODE system, the right hand sides of the ODE systems
   and the initial of the function. 
        
   Example:
   ========
    
   shape_alpha = ShapeODE("shape_alpha",  "shape_alpha", 
   [-1/tau**2 * shape_alpha -2/tau * shape_alpha'],[0, e/tau]) 
  
   The calculation of the properties, `order`, `name`, 
   `initial_values` and the system of ODEs in matrix form is canonical.
"""

from sympy.parsing.sympy_parser import parse_expr
from sympy import *

from sympy.matrices import zeros

# Define constants:
# When we are checking if a function satisfies a linear homogeneous ODE
# of some order n we will check from n=0 to n=MAX_ORDERS. 
MAX_ORDER = 10
# The algorithm below will use a matrix with entries that are the
# evaluation of derivatives of the `shape` function at certain points t.
# In an unlikely case the matrix is not invertible. Therefore we check
# for t from 1 to 100.
# with certain properties. For this purpose we
MAX_TRIES = 100

# 't' is predefined in NESTML and represents time
# 'derivative_factor' is the factor in 
# shape'=derivative_factor*shape in case shape satisfies such an ODE.
derivative_factor, t = symbols("derivative_factor, t")


class ShapeFunction(object):
    """
    Here we provide a class, `ShapeFunction` that can be called
    with a chosen name of the shape and its mathematical description;
    it checks for any given fuction of positive t, i.e. the shape, if
    it satisfies a linear homogeneous ODE of order 1,...,10:
    
    Example:
    ========
    
    shape_alpha = ShapeFunction("shape_alpha", "e / tau * t * exp(-t / tau)") 
    
    The class will provide the properties name, order,
    nestml_ode_form, derivative factors and intitial_values.
    
    in this example: 
    'name' will be 'shape_alpha' as a symbolic expression
    
    'order' is 2, as the function above satisfies a homogeneos ODE of order 2
    
    `nestml_ode_form` is 
    shape_alpha'' = -1/tau**2 * shape_alpha -2/tau * shape_alpha'
    this is the linear homogeneous ODE that shape_alpha satisfies
    
    `derivative_factors` will be a list [-1/tau**2, -2/tau]
    these are the factor occuring in the ODE above 
    
    `initial_values` is [0, e/tau]. These are the initial values of
    all derivatives of occuring on the right hand side of the ODE. 
    From lowest derivative to highest.
    """

    def __init__(self, name, function_def):

        self.name = parse_expr(name)

        # convert the shape function from a string to a symbolic expression
        self.shape_expr = parse_expr(function_def)

        # found_ode is true if we find a linear homogeneous ODE that
        # `shape` satisfies
        found_ode = False

        # First we check if `shape` satisfies a linear homogeneous ODE
        # of order 1. `derivatives` is a list of all derivatives of `shape`
        # up to the order we are checking (which we just call 'order')
        derivatives = [self.shape_expr, diff(self.shape_expr, t)]

        # If `diff_rhs_lhs`, which is here shape'-derivative_factors*shape
        # equals 0 for some 'derivative_factors', 'shape' satisfies a
        # first order linear homogeneous ODE (and does for t=1).
        # Thereafter `diff_rhs_lhs` will be the difference of the derivative
        # of shape of order 'order' and the sum of all lower derivatives times their
        # 'derivative_factors'. This is a list of the potential
        # factors in the ODE from the factor of shape^(0) to
        # shape^(order-1).
        # In the case of the ODE of order 1 we have only one `derivative_factor`
        # but in all other cases we have several. For unified handling we define
        # `derivative_factors` as a list for all orders (also for order 1).
        # As I(t)=0 is possible for some ts we check for several ts to make
        # sure we are not dividing by zero.
        for k in range(1, MAX_TRIES):
            if derivatives[0].subs(t, k) != 0:
                l = k
                break
        derivative_factors = (1 / derivatives[0] * derivatives[1]).subs(t, l),

        diff_rhs_lhs = derivatives[1] - derivative_factors[0] * derivatives[0]

        if simplify(diff_rhs_lhs) == sympify(0):
            found_ode = True

        # Initialize the (potential) order of the differential equation.
        order = 1

        # while an ODE has not yet been found and we have not yet
        # reached the maximum order we are checking for, we check if
        # `shape` satisfies a linear homogeneous ODE of the next higher
        # order.
        while not found_ode and order < MAX_ORDER:
            # The potential order must be at least `order+1`
            order += 1
            # Add the next higher derivative to the list of
            # derivatives of `shape`
            derivatives.append(diff(derivatives[-1], t))

            # The goal here is to calculate the factors (which we call
            # `derivative_factors`) of the ODE (assuming they
            # exist). The idea is to create a system of equations by
            # substituting (natural) numbers into the homogeneous
            # linear homogeneous ODE with variable derivative factors
            # order many times for varying (natural) numbers and solving for
            # derivative factors. Once we have derivative factors the
            # ODE is uniquely defined. This is assuming that shape
            # satisfies an ODE of this order. (This we must stil
            # check)

            # `X` will contain as rows derivatives up to `order-1` of some
            # natural numbers (differing in each row)
            X = zeros(order)

            # `Y` will contain the derivatives of `order` of the natural
            # number in the corresponding row of `X`
            Y = zeros(order, 1)

            # It is possible that by choosing certain natural numbers,
            # the system of equations will not be solvable, i.e. `X` is
            # not invertible. This is unlikely but we check for
            # invertibility of `X` for varying sets of natural numbers.
            invertible = False
            for k in range(MAX_TRIES):
                for i in range(order):
                    substitute = i + k + 1
                    Y[i] = derivatives[order].subs(t, substitute)
                    for j in range(order):
                        X[i, j] = derivatives[j].subs(t, substitute)
                d = det(X)
                if d != 0:
                    invertible = True
                    break

            if not invertible:
                raise Exception("Failed to find homogeneous linear ODE "
                                "which shape satisfies, or shape does "
                                "not satisfy any such ODE of order <= {}".format(MAX_ORDER))

            derivative_factors = X.inv() * Y
            diff_rhs_lhs = 0
            # Once we have 'derivative_factors' the

            # If $shape^{(order)}(t) = \sum_{i<order} C_i shape^{(i)}(t)$, where
            # the $C_i$ are the derivative factors then we can find the
            # $order-1$ derivative factors by evaluating the previous equation as a
            # linear system of order $order-1$ such that Y = [shape^{(order)}] = X * [C_i]
            # hence [C_i] can be found by inverting X.

            # We calculated derivative_factors of the linear
            # homogeneous ODE of order `order` but assumed that shape satisfies
            # such an ODE. This we check here
            for k in range(order):
                # sum up derivatives 'shapes' times their potential 'derivative_factors'
                diff_rhs_lhs -= derivative_factors[k] * derivatives[k]
            diff_rhs_lhs += derivatives[order]
            if simplify(diff_rhs_lhs) == sympify(0):
                found_ode = True
                break

        # It is still possible that `shape` satisfies a linear homogeneous ODE of some order larger than `MAX_ORDER`
        if not found_ode:
            raise Exception("Shape does not satisfy any ODE of order <= {}".format(MAX_ORDER))

        self.order = order
        self.nestml_ode_form = []

        for cur_order in range(0, order-1):
            if cur_order > 0:
                self.nestml_ode_form.append({name + "__" + str(cur_order): name + "__" + str(cur_order + 1)})
            else:
                self.nestml_ode_form.append({name: name + "__1"})
        # Compute the right and left hand side of the ODE that 'shape' satisfies
        rhs_str = []

        for k in range(order):
            if k > 0:
                rhs_str.append("{} * {}__{}".format(simplify(derivative_factors[k]), name, str(k)))

            else:
                rhs_str.append("{} * {}".format(simplify(derivative_factors[k]), name))

        rhs = " + ".join(rhs_str)
        if order == 1:
            lhs = name
        else:
            lhs = name + "__" + str(order-1)

        self.nestml_ode_form.append({lhs: rhs})
        self.derivative_factors = list(simplify(derivative_factors))
        self.initial_values = [x.subs(t, 0) for x in derivatives[:-1]]
        self.updates_to_state_shape_variables = []  # must be filled after the propagator matrix is computed

    def additional_shape_state_variables(self):
        """

        :return: Creates list with state shapes variables in the `reversed` order, e.g. [I'', I', I]
        """
        result = []
        for order in range(0, self.order):
            if order > 0:
                result = [(str(self.name) + "__" + str(order))] + result
            else:
                result = [str(self.name)] + result
        return result

    def add_update_to_shape_state_variable(self, shape_state_variable, shape_state_variable_update):
        self.updates_to_state_shape_variables = [{str(shape_state_variable): str(shape_state_variable_update)}] + self.updates_to_state_shape_variables

    def get_updates_to_shape_state_variables(self):
        result = []
        if self.order > 0:  # FIX ME

            for entry_map in self.updates_to_state_shape_variables:
                # by construction, there is only one value in the `entry_map`
                for shape_state_variable, shape_state_variable_update in entry_map.iteritems():
                    result.append({"__tmp__" + shape_state_variable: shape_state_variable_update})

            for entry_map in self.updates_to_state_shape_variables:
                # by construction, there is only one value in the `entry_map`
                for shape_state_variable, shape_state_variable_update in entry_map.iteritems():
                    result.append({shape_state_variable: "__tmp__" + shape_state_variable})

        else:
            result = self.updates_to_state_shape_variables

        return result

    def get_initial_values(self):
        result = []
        for idx, initial_value in enumerate(self.initial_values):
            if idx > 0:
                p = {str(self.name) + "__" + str(idx): str(initial_value)}
            else:
                p = {str(self.name): str(initial_value)}
            result = [p] + result
        return result


class ShapeODE(object):
    """
    Provides a class 'ShapeODE'. An instance of `ShapeODE` is
    defined with the name of the shape (i.e a function of `t`
    that satisfies a certain ODE), the variables on the left handside
    of the ODE system, the right handsides of the ODE systems
    and the initial value of the function.
        
    Canonical calculation of the properties, `order`, `name`,
    `initial_values` and the system of ODEs in matrix form are made.
    """
    def __init__(self, name, ode_sys_var, ode_sys_rhs, initial_values):

        self.name = parse_expr(name)

        self.ode_sys_var = [symbols(i) for i in ode_sys_var]
        self.ode_sys_rhs = [parse_expr(i) for i in ode_sys_rhs]
        self.order = len(initial_values)
        self.initial_values = [parse_expr(i) for i in initial_values]

        self.matrix = zeros(self.order)

        for i, rhs in enumerate(self.ode_sys_rhs):
            for j, var in enumerate(self.ode_sys_var):
                self.matrix[i, j] = diff(rhs, var)
