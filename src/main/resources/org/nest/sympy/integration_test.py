from sympy import *
import prop_matrix as otpm
import unittest
from shapes import ShapeFunction, ShapeODE

class TestShapesConversionAndPropagatorMatrxiComputation(unittest.TestCase):
    def test_shape_conversion(self):
        shape_alpha = ShapeFunction("shape_alpha", "e / tau * t * exp(-t / tau)")
        self.assertEqual(2, shape_alpha.order)

        shape_exp = ShapeFunction("shape_exp", "exp(-t/tau)")
        self.assertEqual(1, shape_exp.order)

        shape_1 = ShapeFunction("shape_1",  "e / tau * t * t * exp(-t / tau)")
        self.assertEqual(3, shape_1.order)
        shape_3 = ShapeFunction("shape_3", "exp(-t/tau) + e / tau * t * exp(-t / tau)")
        self.assertEqual(2, shape_3.order)

        shape_4 = ShapeFunction("shape_4", "cos(t)")
        self.assertEqual(2, shape_4.order)

        shape_5 = ShapeFunction("shape_5", "sin(t)")
        self.assertEqual(2, shape_5.order)

    def test_propagator_matrix(self):
        shape_alpha = ShapeFunction("shape_alpha", "e / tau * t * exp(-t / tau)")
        shape_exp = ShapeFunction("shape_exp", "exp(-t/tau)")
        shape_sin = ShapeFunction("shape_sinb", "sin(t)")
        shapes = [shape_alpha, shape_exp, shape_sin]

        ode_var = "V_m"
        ode_rhs = "-1/Tau * V_m-1/C * (shape_alpha + shape_exp + shape_sin + currents + I_E)"
        prop_matrices, const_term, step_const = otpm.ode_to_prop_matrices(shapes, ode_var, ode_rhs)

        pm, ps = otpm.prop_matrix_to_prop_step(prop_matrices, const_term, step_const, shapes, ode_var)

if __name__ == '__main__':
    unittest.main()
