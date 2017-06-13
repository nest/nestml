import unittest

from prop_matrix import PropagatorCalculator
from shapes import ShapeFunction
from OdeAnalyzer import OdeAnalyzer
import json

class TestShapesConversionAndPropagatorMatrxiComputation(unittest.TestCase):

    def test_shape_conversion(self):
        shape_alpha = ShapeFunction("shape_alpha", "e / tau * t * exp(-t / tau)")
        self.assertEqual(2, shape_alpha.order)

        shape_exp = ShapeFunction("shape_exp", "exp(-t/tau)")
        self.assertEqual(1, shape_exp.order)

        shape_1 = ShapeFunction("shape_1", "e / tau * t * t * exp(-t / tau)")
        self.assertEqual(3, shape_1.order)
        shape_3 = ShapeFunction("shape_3", "exp(-t/tau) + e / tau * t * exp(-t / tau)")
        self.assertEqual(2, shape_3.order)

        shape_4 = ShapeFunction("shape_4", "cos(t)")
        self.assertEqual(2, shape_4.order)

        shape_5 = ShapeFunction("shape_5", "sin(t)")
        self.assertEqual(2, shape_5.order)

    def test_propagator_matrix(self):
        shape_inh = ShapeFunction("I_in", "(e/tau_syn_in) * t * exp(-t/tau_syn_in)")
        shape_exc = ShapeFunction("I_ex", "(e/tau_syn_ex) * t * exp(-t/tau_syn_ex)")
        shapes = [shape_inh, shape_exc]

        ode_var = "V_m"
        ode_rhs = "-V_m/Tau + (I_in + I_ex + I_e) / C_m"

        calculator = PropagatorCalculator()
        prop_matrices, const_input, step_const = calculator.ode_to_prop_matrices(shapes, ode_var, ode_rhs)
        propagator_elements, ode_var_factor, const_input, update_instructions \
            = calculator.prop_matrix_to_prop_step(prop_matrices, const_input, step_const, shapes, ode_var)
        self.assertTrue(len(propagator_elements) > 0)

    def test_analyzer(self):
        testant = OdeAnalyzer.compute_solution(
            ["V_m' = -V_m/Tau + (I_in + I_ex + I_e) / C_m",
             "I_in = (e/tau_syn_in) * t * exp(-t/tau_syn_in)",
             "I_ex = (e/tau_syn_ex) * t * exp(-t/tau_syn_ex)"])
        self.assertIsNotNone(testant)
        print(testant)
        self.assertEqual("success", testant.status)
        self.assertEqual("exact", testant.solver)

    def test_unconvertable_shape(self):
        testant = OdeAnalyzer.compute_solution(
            ["V_m' = -V_m/Tau + (I_in + I_ex + I_e) / C_m",
             "I_in = " + "t " + " * t" * 10,
             "I_ex = " + "t " + " * t" * 10])

        print(testant)

        self.assertEqual("failed", json.loads(testant)["status"])

if __name__ == '__main__':
    unittest.main()
