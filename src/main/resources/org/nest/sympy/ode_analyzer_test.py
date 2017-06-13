import unittest

import json
from prop_matrix import PropagatorCalculator
from shapes import ShapeFunction
from OdeAnalyzer import OdeAnalyzer
from OdeAnalyzer import Input

cond_ode_block = '{' \
                 '"functions" : [ "I_syn_exc = g_ex*(V_m-E_ex)", "I_syn_inh = g_in*(V_m-E_in)", "I_leak = g_L*(V_m-E_L)" ],' \
                 '"shapes" : [ "g_in = (e/tau_syn_in)*t*exp((-1)/tau_syn_in*t)", "g_ex = (e/tau_syn_ex)*t*exp((-1)/tau_syn_ex*t)" ],' \
                 '"ode" : "V_m\' = (-I_leak-I_syn_exc-I_syn_inh+I_stim+I_e)/C_m"' \
                 '}'
psc_ode_block = '{' \
                '"functions" : [ "I_syn = I_shape_in+I_shape_ex+I_e+currents" ],' \
                '"shapes" : [ "I_shape_in = pA*(e/tau_syn_in)*t*exp((-1)/tau_syn_in*t)", "I_shape_ex = pA*(e/tau_syn_ex)*t*exp((-1)/tau_syn_ex*t)" ], ' \
                '"ode" : "V_abs\' = (-1)/Tau*V_abs+1/C_m*I_syn"' \
                '}'

psc_ode_block2 = '{' \
                 '"ode" : "V_m\' = -V_m/Tau + (I_in + I_ex + I_e) / C_m", ' \
                 '"shapes" : ["I_in = (e/tau_syn_in) * t * exp(-t/tau_syn_in)", ' \
                 '"I_ex = (e/tau_syn_ex) * t * exp(-t/tau_syn_ex)" ] }'


class TestSolutionComputation(unittest.TestCase):

    def test_is_linear_constant_coefficient_ode(self):
        testant = json.loads(OdeAnalyzer.compute_solution(psc_ode_block))
        self.assertTrue(testant["solver"] == "exact")

        testant = json.loads(OdeAnalyzer.compute_solution(cond_ode_block))
        self.assertTrue(testant["solver"] == "numeric")

    def test_propagator_matrix(self):
        shape_inh = ShapeFunction("I_in", "(e/tau_syn_in) * t * exp(-t/tau_syn_in)")
        shape_exc = ShapeFunction("I_ex", "(e/tau_syn_ex) * t * exp(-t/tau_syn_ex)")
        shapes = [shape_inh, shape_exc]

        ode_var = "V_m"
        ode_rhs = "-V_m/Tau + (I_in + I_ex + I_e) / C_m"

        calculator = PropagatorCalculator()
        prop_matrices, const_input, step_const = calculator.ode_to_prop_matrices(shapes, ode_var, ode_rhs, [], [])
        propagator_elements, ode_var_factor, const_input, update_instructions \
            = calculator.prop_matrix_to_prop_step(prop_matrices, const_input, step_const, shapes, ode_var)
        self.assertTrue(len(propagator_elements) > 0)

    def test_analyzer(self):
        testant = OdeAnalyzer.compute_solution(psc_ode_block2)
        self.assertIsNotNone(testant)
        print testant

    def test_analyzer_iaf_cond_alpha(self):

        testant = OdeAnalyzer.compute_solution(cond_ode_block)
        self.assertIsNotNone(testant)
        print testant

    def test_analyzer_iaf_psc_alpha(self):

        testant = OdeAnalyzer.compute_solution(psc_ode_block)
        self.assertIsNotNone(testant)
        print testant

    def test_creation_from_json(self):
        ode_block = '{'\
                  '"functions" : [ "I_syn_exc = cond_sum(g_ex, spikeExc)*(V_m-E_ex)]", "I_syn_inh = cond_sum(g_in, spikeInh)*(V_m-E_in)", "I_leak = g_L*(V_m-E_L)" ],' \
                  '"shapes" : [ "g_in = (e/tau_syn_in)*t*exp((-1)/tau_syn_in*t)", "g_ex = (e/tau_syn_ex)*t*exp((-1)/tau_syn_ex*t)" ],'\
                  '"ode" : "V_m\' = ((-I_leak)-I_syn_exc-I_syn_inh+I_stim+I_e)/C_m" }'
        testant = Input(ode_block)
        self.assertIsNotNone(testant)

if __name__ == '__main__':
    unittest.main()
