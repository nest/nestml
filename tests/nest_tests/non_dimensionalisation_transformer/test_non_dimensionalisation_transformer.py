# -*- coding: utf-8 -*-
#
# test_non_dimensionalisation_transformer.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

import nest
import numpy as np
import scipy as sp
import os
import pytest

from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestNonDimensionalisationTransformer:

    r"""



    ### test_giga - test_atto
    These tests will check if the standardized metric prefixes in the range of Giga- to Atto- can be resolved.
    The prefixes Deci- and Deca- are probably little used in a neuroscience context.
    The test for Femto- includes the use of a combined physical type, the "magnetic field strength".

    """

    def generate_code(self, codegen_opts=None):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "non_dimensionalisation_transformer_test_neuron.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix,
                             codegen_opts=codegen_opts)

    def generate_code_metric_prefixes(self, codegen_opts=None):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "test_metric_prefix_transformation.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix,
                             codegen_opts=codegen_opts)


    @pytest.mark.parametrize("preffered_prefix", ["1", "m"])
    def test_non_dimensionalisation_transformer(self, preffered_prefix: str):
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "M",
                                                         "electrical current": preffered_prefix}}
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")

        nest.SetStatus(mm, {"record_from": ["I_foo", "V_3"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        I_foo = mm.get("events")["I_foo"]
        V_3 = mm.get("events")["V_3"]

        if preffered_prefix == "1":
            # we want representation in Ampère
            np.testing.assert_allclose(I_foo, 0.042)
        elif preffered_prefix == "m":
            # we want representation in mA
            np.testing.assert_allclose(I_foo, 42)

        np.testing.assert_allclose(V_3, 8.4)






    def test_exp_in_equationblock(self):
        """
        This test checks if the transformer can deal with functions like exp() in the equation block
        V_exp_der' (s) is a time dependent voltage
        original expression: V_exp_der' V = (I_foo - 200uA) / (C_exp_0 * (1+exp(alpha_exp * V_m_init)))
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and V_exp'
                                                         "electrical current": "n",  # needed for I_foo
                                                         "electrical capacitance": "p",  # needed for C_exp_0
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "1",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["I_foo", "V_m_init"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        I_foo = mm.get("events")["I_foo"]
        V_m_init = mm.get("events")["V_m_init"]

        np.testing.assert_allclose(I_foo, 4.2e7)  # should be 42.000.000 (nA)
        np.testing.assert_allclose(V_m_init, -65)  # should be -65 (mV)

        lhs_expression_after_transformation = "V_exp_der' real"
        rhs_expression_after_transformation = "1e3 * ((I_foo * 1e-3) - (200 * 1e-6)) / ((C_exp_0 * 1e-12) * (1 + exp((alpha_exp * 1e-6) * (V_m_init * 1e-3))))"



    def test_real_factor_in_stateblock(self):
        r"""
        This test checks if state block expressions with
        a RHS with a unit being multiplied by a real factor and
        a LHS with type 'real'
        will get processed correctly
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                         "electrical current": "1",  # needed for currents not part of the test
                                                         "electrical capacitance": "1",  # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "1",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["V_m_init", "U_m"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        V_m_init = mm.get("events")["V_m_init"]
        U_m = mm.get("events")["U_m"]

        np.testing.assert_allclose(V_m_init, -65)
        np.testing.asser_allclose(U_m, -13)

        lhs_expression_after_transformation = "U_m real"
        rhs_expression_after_transformation = "b * (V_m_init * 1e-3)"


    def test_inline_expression_in_equationblock(self):
        """
        This test checks if the transformer can deal with inline expressions in the equation block
        Additionally there is an exp() in the expression
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for voltages not part of the test
                                                         "electrical current": "p",  # needed for currents not part of the test
                                                         "electrical capacitance": "1",  # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "1",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["I_spike_test", "V_m_init"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        V_m_init = mm.get("events")["V_m_init"]
        I_spike_test = mm.get("events")["I_spike_test"]

        np.testing.assert_allclose(V_m_init, -65)  # should be -65 mV
        np.testing.assert_allclose(I_spike_test, 60)  # should be 60 pA

        lhs_expression_after_transformation = "Inline I_spike_test real"
        rhs_after_expression = "1e12 *((30.0 * 1e-9) * ((-V_m_init * 1e-3) / 130e3) * exp((((-80 * 1e-3)) - ((-20 * 1e-3))) / (3000 * 1e-6)))"






    def test_reciprocal_unit_in_parameterblock(self):
        """
        This test checks if the transformer can deal with reciprocal units on the LHS of an equation inside the parameter block
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                         "electrical current": "1",  # needed for currents not part of the test
                                                         "electrical capacitance": "1",  # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "1",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["V_exp", "alpha_exp"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        V_exp = mm.get("events")["V_exp"]
        alpha_exp = mm.get("events")["alpha_exp"]

        np.testing.assert_allclose(V_exp, -62.5)  # should be -62.5004333 mV
        np.testing.assert_allclose(alpha_exp, 6.667e-10)  # should be (2e-10/3) (1/mV)

        lhs_expression_after_transformation_parameter = "alpha_exp real"
        rhs_expression_after_transformation_parameter = "2 /(3 * 1e6)"


    def test_giga(self):
        """
        This test checks if the transformer can deal with the Giga- prefix
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                         "electrical current": "1",  # needed for currents not part of the test
                                                         "electrical capacitance": "1",  # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "1",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_giga"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_giga = mm.get("events")["para_giga"]

        np.testing.assert_allclose(para_giga, 500)  # should be 500 MOhm


    def test_mega(self):
        """
        This test checks if the transformer can deal with the Mega- prefix
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                         "electrical current": "1",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "1",
                                                         # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "1",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code_metric_prefixes(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_mega"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_mega = mm.get("events")["para_mega"]

        np.testing.assert_allclose(para_mega, 3300)  # should be 3300 kHz
        
        
    def test_kilo(self):
        """
        This test checks if the transformer can deal with the Kilo- prefix
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                         "electrical current": "1",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "1",
                                                         # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "1",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_kilo"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_kilo = mm.get("events")["para_kilo"]

        np.testing.assert_allclose(para_kilo, 0.002)  # should be 0.002 MW

        
    def test_hecto(self):
        """
        This test checks if the transformer can deal with the Hecto- prefix
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                         "electrical current": "1",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "1",
                                                         # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "1",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_hecto"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_hecto = mm.get("events")["para_hecto"]

        np.testing.assert_allclose(para_hecto, 102.4)  # should be 102.4 kPa


    def test_deca(self):
        """
        This test checks if the transformer can deal with the Deca- prefix
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                         "electrical current": "1",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "1",
                                                         # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "1",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_deca"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_deca = mm.get("events")["para_deca"]

        np.testing.assert_allclose(para_deca, 2300)  # should be 2300 m


    def test_deci(self):
        """
        This test checks if the transformer can deal with the Deci- prefix
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                         "electrical current": "1",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "1",
                                                         # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "1",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_deci"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_deci = mm.get("events")["para_deca"]

        np.testing.assert_allclose(para_deci, 80)  # should be 80 mol


    def test_centi(self):
        """
        This test checks if the transformer can deal with the Centi- prefix
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                         "electrical current": "1",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "1",
                                                         # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "m",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_centi"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_centi = mm.get("events")["para_centi"]

        np.testing.assert_allclose(para_centi, 6700)  # should be 6700 mM


    def test_milli(self):
        """
        This test checks if the transformer can deal with the Milli- prefix
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                         "electrical current": "1",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "1",
                                                         # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "m",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_milli"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_milli = mm.get("events")["para_milli"]

        np.testing.assert_allclose(para_milli, 6700)  # should be 6700 mM


    def test_micro(self):
        """
        This test checks if the transformer can deal with the Micro- prefix
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "u",  # needed for V_m_init and U_m
                                                         "electrical current": "1",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "1",
                                                         # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "m",
                                                         "amount of substance": "1",
                                                         "electrical conductance":"m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_micro"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_micro = mm.get("events")["para_micro"]

        np.testing.assert_allclose(para_micro, 0.002)  # should be 0.002 mS


    def test_nano(self):
        """
        This test checks if the transformer can deal with the Nano- prefix
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "u",  # needed for V_m_init and U_m
                                                         "electrical current": "1",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "u",
                                                         # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "m",
                                                         "amount of substance": "1",
                                                         "electrical conductance": "m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_nano"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_nano = mm.get("events")["para_nano"]

        np.testing.assert_allclose(para_nano, 0.011)  # should be 0.011 uF


    def test_pico(self):
        """
        This test checks if the transformer can deal with the Pico- prefix
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "u",  # needed for V_m_init and U_m
                                                         "electrical current": "1",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "u",
                                                         # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "m",
                                                         "amount of substance": "1",
                                                         "electrical conductance":"m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_pico"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_pico = mm.get("events")["para_pico"]

        np.testing.assert_allclose(para_pico, 0.003)  # should be 0.003 nF


    def test_femto(self):
        """
        This test checks if the transformer can deal with the Femto- prefix
        si.A/si.m is the unit of magnetic field strength, so there might be problems
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "u",  # needed for V_m_init and U_m
                                                         "electrical current": "p",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "u",
                                                         # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "1",
                                                         "amount of substance": "1",
                                                         "electrical conductance":"m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_femto"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_femto = mm.get("events")["para_femto"]

        np.testing.assert_allclose(para_femto, 77000)  # should be 77000 pA/m


    def test_atto(self):
        """
        This test checks if the transformer can deal with the Atto- prefix
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "u",  # needed for V_m_init and U_m
                                                         "electrical current": "p",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "u",
                                                         # needed for caps not part of the test
                                                         "electrical resistance": "M",
                                                         "frequency": "k",
                                                         "power": "M",
                                                         "pressure": "k",
                                                         "length": "1",
                                                         "amount of substance": "1",
                                                         "electrical conductance":"m",
                                                         "inductance": "n",
                                                         "time": "f",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["para_atto"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_atto = mm.get("events")["para_atto"]

        np.testing.assert_allclose(para_atto, 0.04)  # should be 0.04 fs
        

            
    