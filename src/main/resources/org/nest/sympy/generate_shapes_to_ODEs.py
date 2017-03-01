 '''The aim of this script is to check for any given function of
    positive `t`, which we will call `shape`, if it satisfies a linear
    homogeneous ODE. If it does, it will give it's order, initial
    values, the equation itself and a list of all factors of
    derivatives (which we will call `derivative_factors`) of the shape
    function in the ODE, i.e. if shape''= a*shape+b*shape' the list
    will be: [a,b].

    Example:
    ========

    Convert the postsynaptic response shape from a function form  
       shape = t * exp(t * a)
    to an ODE form
       shape'' = -a**2 * shape + 2*a * shape'
    '''

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
with certain properties. For this purpose we
MAX_TRIES = 100

# 't' is predefined in NESTML and represents time
# 'derivative_factor' is the factor in 
# shape'=derivative_factor*shape in case shape satisfies such an ODE.
derivative_factor, t = symbols("derivative_factor, t")
        

class ShapeFunction(object):

    def __init__(self, name, function):

        self.name = parse_expr(name)

        
        # convert the shape function from a string to a symbolic expression
        shape = parse_expr(function)

        # found_ode is true if we find a linear homogeneous ODE that
        # `shape` satisfies
        found_ode = False
        
        # First we check if `shape` satisfies a linear homogeneous ODE
        # of order 1. `derivatives` is a list of all derivatives of `shape`
        # up to the order we are checking (which we just call 'order')
        derivatives = [shape, diff(shape, t)]
        
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
	    for k in range(MAX_TRIES)
            derivative_factors = (1/derivatives[0] * derivatives[1]).subs(t,k),
            if derivatives[0].subs(t,k) != 0:
                break

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
                    substitute = i+k+1
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
       
        # Compute the right and left hand side of the ODE that 'shape' satisfies
        rhs_str = []
        for k in range(order):
            rhs_str.append("{} * {}{}".format(simplify(derivative_factors[k]), name, "'" * k))
        rhs = " + ".join(rhs_str)
        lhs = name + "'" * order

        self.order = order
        self.nestml_ode_form = "{} = {}".format(lhs, rhs)
        self.derivative_factors = list(simplify(derivative_factors))
        self.initial_values = [x.subs(t, 0) for x in derivatives[:-1]]



class ShapeODE(object):
    '''It is also possible to define a shape function by giving a
    set of linear homogeneous ODEs which the shape functions satisfies 
    and a set of initial values (for an ODE of order `order`, `order-1` many.)
    In this case the calculation of the ODE, `order`, `initial_values` and 
    the system of ODEs in matrix form is canonical.
    '''
    
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
