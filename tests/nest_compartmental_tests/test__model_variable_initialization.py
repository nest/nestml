# -*- coding: utf-8 -*-
#
# test__model_variable_initialization.py
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

import os

import pytest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

# set to `True` to plot simulation traces
TEST_PLOTS = True
try:
    import matplotlib
    import matplotlib.pyplot as plt
except BaseException as e:
    # always set TEST_PLOTS to False if matplotlib can not be imported
    TEST_PLOTS = False


class TestInitialization():
    @pytest.fixture(scope="module", autouse=True)
    def setup(self):
        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=0.1))

        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(
            tests_path,
            "resources",
            "concmech.nestml"
        )
        target_path = os.path.join(
            tests_path,
            "target/"
        )

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        print(
            f"Compiled nestml model 'cm_main_cm_default_nestml' not found, installing in:"
            f"    {target_path}"
        )

        generate_nest_compartmental_target(
            input_path=input_path,
            target_path="/tmp/nestml-component/",
            module_name="concmech_module",
            suffix="_nestml",
            logging_level="DEBUG"
        )

        nest.Install("concmech_module.so")

    def test_non_existing_param(self):
        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=0.1))
        nest.Install("concmech_module.so")

        params = {'C_m': 10.0, 'g_C': 0.0, 'g_L': 1., 'e_L': -70.0, 'non_existing': 1.0}

        with pytest.raises(nest.NESTErrors.BadParameter):
            cm = nest.Create('multichannel_test_model_nestml')
            cm.compartments = [{"parent_idx": -1, "params": params}]

    def test_existing_states(self):
        """Testing whether the python initialization of variables works by looking up the variables at the very start of
        the simulation. Since the values change dramatically in the very first step, before which we can not sample them
        we test whether they are still large enough and not whether they are the same"""
        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=0.1))
        nest.Install("concmech_module.so")

        params = {'C_m': 10.0, 'g_C': 0.0, 'g_L': 1., 'e_L': -70.0, 'gbar_NaTa_t': 1.0, 'h_NaTa_t': 1000.0, 'c_Ca': 1000.0, 'v_comp': 1000.0}

        cm = nest.Create('multichannel_test_model_nestml')
        cm.compartments = [{"parent_idx": -1, "params": params}]

        mm = nest.Create('multimeter', 1, {
            'record_from': ['v_comp0', 'c_Ca0', 'h_NaTa_t0'], 'interval': .1})

        nest.Connect(mm, cm)

        nest.Simulate(1000.)

        res = nest.GetStatus(mm, 'events')[0]

        data_array_index = 0

        fig, axs = plt.subplots(3)

        axs[0].plot(res['times'], res['v_comp0'], c='r', label='v_comp0')
        axs[1].plot(res['times'], res['c_Ca0'], c='y', label='c_Ca0')
        axs[2].plot(res['times'], res['h_NaTa_t0'], c='b', label='h_NaTa_t0')

        axs[0].set_title('v_comp0')
        axs[1].set_title('c_Ca0')
        axs[2].set_title('h_NaTa_t')

        axs[0].legend()
        axs[1].legend()
        axs[2].legend()

        plt.savefig("initialization test.png")

        assert res['v_comp0'][data_array_index] > 50.0, ("the voltage (left) is not as expected (right). (" + str(res['v_comp0'][data_array_index]) + "<" + str(50.0) + ")")

        assert res['c_Ca0'][data_array_index] > 900.0, ("the concentration (left) is not as expected (right). (" + str(res['c_Ca0'][data_array_index]) + "<" + str(900.0) + ")")

        assert res['h_NaTa_t0'][data_array_index] > 5.0, ("the gating variable state (left) is not as expected (right). (" + str(res['h_NaTa_t0'][data_array_index]) + "<" + str(5.0) + ")")
