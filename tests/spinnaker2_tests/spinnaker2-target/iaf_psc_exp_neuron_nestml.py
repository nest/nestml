#
#  iaf_psc_exp_neuron_nestml.py
#
#  This file is part of NEST.
#
#  Copyright (C) 2004 The NEST Initiative
#
#  NEST is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  NEST is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
#
#  Generated from NESTML 8.0.0-post-dev at time: 2025-03-31 13:04:47.130292


import numpy as np

from spinnaker2.neuron_models.application import BaseApplication
from spinnaker2.neuron_models.lif_neuron import LIFApplication
from spinnaker2.coordinates import ByteAddr




class iaf_psc_exp_neuron_nestmlApplication(LIFApplication):
    default_parameters = {
            "C_m": 250,
            "tau_m": 10,
            "tau_syn_inh": 2,
            "tau_syn_exc": 2,
            "refr_T": 2,
            "E_L": -70,
            "V_reset": -70,
            "V_th": -55,
            "I_e": 0,
    }

    max_atoms_per_core = 250
    splittable = True
    recordables = ["spikes", "v", "v_last"]  # TODO: Read this out from NESTML file
    # fixed addresses
    neuron_params_addr = ByteAddr(0xDC00)
    data_spec_addr = ByteAddr(0x10000)  # until 0x10080
    log_addr = ByteAddr(0x1B000)
    data_spec_max_size = 16  # in words

    def __init__(self):
        app_name =  "iaf_psc_exp_neuron_nestml"
        BaseApplication.__init__(self, name=app_name)
    @classmethod
    def convert_lif_neuron_params_to_raw_data(cls, pop_slice):






















        ordered_param_names = [
                "C_m",
                "tau_m",
                "tau_syn_inh",
                "tau_syn_exc",
                "refr_T",
                "E_L",
                "V_reset",
                "V_th",
                "I_e",
            ]
        n_params = len(ordered_param_names)
        max_neurons = cls.max_atoms_per_core

        float_array = np.zeros(max_neurons * n_params, dtype=np.float32)
        params = pop_slice.pop.params
        n_neurons = pop_slice.size()
        for i, key in enumerate(ordered_param_names):
            value = params.get(key, cls.default_params[key])
            if np.isscalar(value) or len(value) == 1:  # same value for all
                float_array[i : i + n_params * n_neurons : n_params] = value
            else:  # array like
                assert len(value) == pop_slice.pop.size
                float_array[i : i + n_params * n_neurons : n_params] = value[pop_slice.start : pop_slice.stop]

        # convert to uint32 array and return as list
        raw_data = np.frombuffer(float_array.data, dtype=np.uint32)
        return raw_data.tolist()









































































