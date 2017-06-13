from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from sympy.matrices import zeros

from shapes import ShapeFunction, ShapeODE

h = symbols("__h")


class PropagatorCalculator(object):
    global h

    @staticmethod
    def ode_to_prop_matrices(shapes, ode_var_str, ode_rhs_str):
        """
        The function `ode_to_prop_matrices` calculates a so called proagator
        for any given linear constant coefficient ODE with an inhomogeneous part
        wich is a sum of `shapes` (instaces of the class `ShapeFunction` or
        `ShapeODE`; they satisfy a linear homogeneous ODE).
        The idea is to reformulate the ODE or systems of ODEs as the ODE
        y'=Ay and to calculate A and then exp(Ah) to give an evolution of
        the system for a given timestep `h`.

        Example:
        ========
        shape_alpha = ShapeFunction("shape_alpha", "e / tau * t * exp(-t / tau)")
        shape_exp = ShapeFunction("shape_exp", "exp(-t/tau)")
        shape_sin = ShapeFunction("shape_sinb", "sin(t)")
        shapes = [shape_alpha, shape_exp, shape_sin]

        ode_var = "V_m"
        ode_rhs = "-1/Tau * V_m-1/C * (shape_alpha + shape_exp + shape_sin + currents + I_E)"
        prop_matrices, const_input, step_const = otpm.ode_to_prop_matrices(shapes, ode_var, ode_rhs)
        """
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

            if isinstance(shape, ShapeFunction):
                # For shapes that satisfy a homogeneous linear ODE of order 1 or
                # 2 we calculate a upper triangular matrix to make calculations more
                # efficient.
                if shape.order == 1:
                    A = Matrix([[shape.derivative_factors[0], 0             ],
                                [shape_factor,                ode_var_factor]])
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

            if isinstance(shape, ShapeODE):

                A = zeros(shape.order + 1)
                A[:shape.order, :shape.order] = shape.matrix
                A[shape.order, shape.order] = ode_var_factor
                A[shape.order, shape.order - 1] = shape_factor

            shape_factors.append(shape_factor)
            # Calculate the mat
            prop_matrices.append(simplify(exp(A * h)))

        step_const = -1/ode_var_factor * (1 - exp(h * ode_var_factor))

        const_input = ode_rhs - ode_var_factor * ode_var
        for shape_factor, shape in zip(shape_factors, shapes):
            const_input -= shape_factor * shape.name

        return prop_matrices, simplify(const_input), simplify(step_const)

    @staticmethod
    def constant_input(step_const, ode_var_str):
        return "__ode_var_factor * " + ode_var_str + " + __const_input * (" + str(step_const) + ")"

    @staticmethod
    def prop_matrix_to_prop_step(prop_matrices, const_input, step_const, shapes, ode_var_str):
        p_order_order = prop_matrices[0][shapes[0].order, shapes[0].order]
        ode_var = parse_expr(ode_var_str)
        ode_var_factor = {"__ode_var_factor": str(p_order_order)}
        const_input = {"__const_input": str(const_input)}

        propagator_elements = {}
        update_instructions = [ode_var_str + " = " + str(PropagatorCalculator.constant_input(step_const, ode_var_str))]
        for p, shape in zip(prop_matrices, shapes):
            P = zeros(shape.order + 1, shape.order + 1)
            for i in range(shape.order + 1):
                for j in range(shape.order + 1):
                    if simplify(p[i, j]) != sympify(0):
                        P[i, j] = parse_expr("__P_{}_{}_{}".format(shape.name, i, j))
                        propagator_elements["__P_{}_{}_{}".format(shape.name, i, j)] = str(p[i, j])

            y = zeros(shape.order + 1, 1)
            for i in range(shape.order):
                y[i] = parse_expr("__{}_{}".format(shape.name, i))
            y[shape.order] = ode_var

            P[shape.order, shape.order] = 0
            z = P * y

            update_instructions.append(ode_var_str + " += " + str(z[shape.order]))

        return propagator_elements, ode_var_factor, const_input, update_instructions

