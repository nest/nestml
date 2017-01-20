from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from sympy.matrices import zeros

import misc

__h = symbols("__h")

def ode_to_prop_matrices(shapes, ode_var_str, ode_rhs_str):
    '''
     The aim of this script is to calculate a so called proagator
     for any given linear constant coefficient ODE with an inhomogeneous part
     wich is a sum of shapes (These satisfy a linear hoomogeneous ODE). 
     The idea is to reformulate the ODE or system of ODEs as the ODE
     y'=Ay and to calculate A and then exp(Ah) to give an evolution of 
     the system for a given timestep `h`.
     Although we think of the equation as something like this:
    '''
    ode_rhs = parse_expr(ode_rhs_str)
    ode_var = parse_expr(ode_var_str)
    
    # For V'= 1/Tau * V + 1/C * shape `ode_var_factor` is `1/Tau`
    # The `shape_factor` here is `1/C` this will be a list `shape_factors`
    # as different shapes will have different `shape_factors` and a sum of 
    # multiple differnt shapes is possible.

    ode_var_factor = diff(ode_rhs, ode_var)
    shape_factors = []
    # This is a list of different propagator matrices for different shapes. 
    # These will be combined to give a complete step.
    prop_matrices = []

    for shape in shapes:
        
        shape_factor = diff(ode_rhs, shape.name)
    
        if isinstance(shape, misc.ShapeFunction):
            # For shapes that satisfy a homogeneous linear ODE of order 1 or
            # 2 we calculate a upper triangular matrix to make calculations more 
            # efficient.
            if shape.order == 1:
                A = Matrix([[shape.derivative_factors[0], 0             ],
                            [shape_factor,          ode_var_factor]])
            elif shape.order == 2:
                solutionpq = -shape.derivative_factors[1]/2 + sqrt(shape.derivative_factors[1]**2 / 4 + shape.derivative_factors[0])
                A = Matrix([[shape.derivative_factors[1]+solutionpq, 0,            0             ],
                            [1,                                      -solutionpq,  0             ],
                            [0,                                     shape_factor, ode_var_factor]])
            # For shapes that satisfy a homogeneous linear ODE of order larger than
            # 2 we calculate A by choosing the state variables canonicaly as
            # y_0=I^(n),..., y_{n-1}=I, y_n=V
            else:
                A = zeros(shape.order+1)
                A[shape.order, shape.order] = ode_var_factor
                A[shape.order, shape.order - 1] = shape_factor
                for j in range(0, shape.order):
                    A[0, j] = shape.derivative_factors[shape.order - j - 1]
                for i in range(1, shape.order):
                    A[i, i - 1] = 1
        
        if isinstance(shape, misc.ShapeODE):
    
            A = zeros(shape.order + 1)
            A[:shape.order, :shape.order] = shape.matrix
            A[shape.order, shape.order] = ode_var_factor
            A[shape.order, shape.order - 1] = shape_factor

        shape_factors.append(shape_factor)
        # Calculate the mat
        prop_matrices.append(simplify(exp(A * __h)))

    step_const = -1/ode_var_factor * (1 - exp(__h * ode_var_factor))

    const_term = ode_rhs - ode_var_factor * ode_var 
    for shape_factor, shape in zip(shape_factors, shapes):
        const_term -= shape_factor * shape.name
    
    return prop_matrices, simplify(const_term), simplify(step_const)

# Here we calculate the explicit step, i.e y(t+h) = y(t) * exp(Ah)
def prop_matrix_to_prop_step(prop_matrices, const_term, step_const, shapes, ode_var_str):

    P_order_order = prop_matrices[0][shapes[0].order, shapes[0].order]
    ode_var = parse_expr(ode_var_str)

    prop_step_str = "__P_order_order real = " + str(P_order_order * ode_var) + "\n" + \
                    "__const_term real = " + str(const_term) + "\n" + \
                    ode_var_str + " = __P_order_order * " + ode_var_str + " + __const_term * (" + str(step_const) + ")\n"
    prop_matrix_str = ""

    for p, shape in zip(prop_matrices, shapes):

        P = zeros(shape.order + 1, shape.order + 1)
        for i in range(shape.order + 1):
            for j in range(shape.order + 1):
                if simplify(p[i,j]) != sympify(0):
                    prop_matrix_str += "__P_{}_{}_{} real = ".format(shape.name, i, j) + str(p[i,j]) + "\n"
                    P[i,j] = parse_expr("__P_{}_{}_{}".format(shape.name, i, j))

        y = zeros(shape.order + 1, 1)
        for i in range(shape.order):
            y[i] = parse_expr("y_{}_{}".format(shape.name, i))
        y[shape.order] = ode_var

        P[shape.order, shape.order] = 0
        z = P * y

        prop_step_str += ode_var_str + " += " + str(z[shape.order]) + "\n"


    return prop_matrix_str, prop_step_str




    

    

    
    
