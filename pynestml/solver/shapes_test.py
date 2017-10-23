import unittest

from pynestml.solver.shapes import ShapeFunction


class TestThatShapeIsConvertedToODEs(unittest.TestCase):
    def test_shape_to_odes(self):
        shape_inh = ShapeFunction("I_in", "(e/tau_syn_in) * t * exp(-t/tau_syn_in)")
        shape_exc = ShapeFunction("I_ex", "(e/tau_syn_ex) * t * exp(-t/tau_syn_ex)")

        print(shape_inh.get_ode_form())
        print(shape_exc.get_ode_form())


if __name__ == '__main__':
    unittest.main()
