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
#  Generated from NESTML 8.3.0-rc3-post-dev at time: 2026-07-19 17:20:00.407917

from numpy import exp, ceil

from spynnaker.pyNN.models.neuron import AbstractPyNNNeuronModel
from spynnaker.pyNN.models.defaults import default_parameters
from spynnaker.pyNN.data.spynnaker_data_view import SpynnakerDataView

from python_models8.neuron.implementations.iaf_psc_exp_neuron_nestml_impl import iaf_psc_exp_neuron_nestmlImpl


class iaf_psc_exp_neuron_nestml(AbstractPyNNNeuronModel):

    @default_parameters({
        "C_m", \
        "tau_m", \
        "tau_syn_inh", \
        "tau_syn_exc", \
        "refr_T", \
        "E_L", \
        "V_reset", \
        "V_th", \
        "I_e", \
    })
    def __init__(self,
                 # state variables
                 V_m = -70,    # type: mV
                 refr_t = 0,    # type: ms
                 I_syn_exc = 0,    # type: pA
                 I_syn_inh = 0,    # type: pA

                 # parameters
                 C_m = 250,    # type: pF
                 tau_m = 10,    # type: ms
                 tau_syn_inh = 2,    # type: ms
                 tau_syn_exc = 2,    # type: ms
                 refr_T = 2,    # type: ms
                 E_L = -70,    # type: mV
                 V_reset = -70,    # type: mV
                 V_th = -55,    # type: mV
                 I_e = 0,    # type: pA

                 # spike input ports
                 exc_spikes = 0.0,
                 ignore_spikes = 0.0,

                 # continuous input ports
                 I_stim = 0.0,
                ):
        timestep = (SpynnakerDataView.get_simulation_time_step_ms())

        # compute propagators and other internal parameters
        unit_psc = 1  # type: pA
        __h = timestep  # type: ms
        __P__I_syn_exc__I_syn_exc = exp((-__h) / tau_syn_exc)  # type: real
        __P__I_syn_inh__I_syn_inh = exp((-__h) / tau_syn_inh)  # type: real
        __P__V_m__I_syn_exc = tau_m * tau_syn_exc * ((-exp(__h / tau_m)) + exp(__h / tau_syn_exc)) * exp((-__h) * (tau_m + tau_syn_exc) / (tau_m * tau_syn_exc)) / (C_m * (tau_m - tau_syn_exc))  # type: real
        __P__V_m__I_syn_inh = tau_m * tau_syn_inh * (exp(__h / tau_m) - exp(__h / tau_syn_inh)) * exp((-__h) * (tau_m + tau_syn_inh) / (tau_m * tau_syn_inh)) / (C_m * (tau_m - tau_syn_inh))  # type: real
        __P__V_m__V_m = exp((-__h) / tau_m)  # type: real
        __P__refr_t__refr_t = 1  # type: real

        super().__init__(iaf_psc_exp_neuron_nestmlImpl(
                 # state:
                I_syn_exc,
                I_syn_inh,
                refr_t,
                V_m,
                 # parameters:
                C_m,
                E_L,
                I_e,
                refr_T,
                tau_m,
                tau_syn_exc,
                tau_syn_inh,
                V_reset,
                V_th,
                 # internal variables:
                __h,
                __P__I_syn_exc__I_syn_exc,
                __P__I_syn_inh__I_syn_inh,
                __P__refr_t__refr_t,
                __P__V_m__I_syn_exc,
                __P__V_m__I_syn_inh,
                __P__V_m__V_m,
                unit_psc,
                 # spiking input ports:
                exc_spikes,
                ignore_spikes,
                 # continuous input ports:
                I_stim,
                                           ))