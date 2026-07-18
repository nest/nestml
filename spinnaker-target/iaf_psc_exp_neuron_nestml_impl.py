#
#  iaf_psc_exp_neuron_nestml_impl.py
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
#  Generated from NESTML 8.3.0-rc3-post-dev at time: 2026-07-14 18:14:13.994452

from spinn_front_end_common.interface.ds import DataType
from spinn_front_end_common.utilities.constants import BYTES_PER_WORD
from spynnaker.pyNN.utilities.struct import Struct
from spynnaker.pyNN.models.neuron.implementations import AbstractNeuronImpl

from spinn_utilities.overrides import overrides

import os



class iaf_psc_exp_neuron_nestmlImpl(AbstractNeuronImpl):
    r"""
    Generated sPyNNaker class for the model: iaf_psc_exp_neuron_nestml

    Model docstring:


        iaf_psc_exp - Leaky integrate-and-fire neuron model
    ###################################################

    Description
    +++++++++++

    iaf_psc_exp is an implementation of a leaky integrate-and-fire model
    with exponentially decaying synaptic currents according to [1]_.
    Thus, postsynaptic currents have an infinitely short rise time.

    The threshold crossing is followed by an absolute refractory period
    during which the membrane potential is clamped to the resting potential
    and spiking is prohibited.

    The general framework for the consistent formulation of systems with
    neuron like dynamics interacting by point events is described in
    [1]_.  A flow chart can be found in [2]_.

    Critical tests for the formulation of the neuron model are the
    comparisons of simulation results for different computation step
    sizes.

    References
    ++++++++++

    .. [1] Rotter S, Diesmann M (1999). Exact simulation of
           time-invariant linear systems with applications to neuronal
           modeling. Biologial Cybernetics 81:381-402.
           DOI: https://doi.org/10.1007/s004220050570
    .. [2] Diesmann M, Gewaltig M-O, Rotter S, & Aertsen A (2001). State
           space analysis of synchronous spiking in cortical neural
           networks. Neurocomputing 38-40:565-571.
           DOI: https://doi.org/10.1016/S0925-2312(01)00409-X
    .. [3] Morrison A, Straube S, Plesser H E, Diesmann M (2006). Exact
           subthreshold integration with continuous spike times in discrete time
           neural network simulations. Neural Computation, in press
           DOI: https://doi.org/10.1162/neco.2007.19.1.47

    See also
    ++++++++

    iaf_psc_delta, iaf_psc_alpha, iaf_cond_exp

    Copyright statement
    +++++++++++++++++++

    This file is part of NEST.

    Copyright (C) 2004 The NEST Initiative

    NEST is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    NEST is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with NEST.  If not, see <http://www.gnu.org/licenses/>.


    """
    def __init__(self,
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
                 # internals:
                 __h,
                 __P__I_syn_exc__I_syn_exc,
                 __P__I_syn_inh__I_syn_inh,
                 __P__refr_t__refr_t,
                 __P__V_m__I_syn_exc,
                 __P__V_m__I_syn_inh,
                 __P__V_m__V_m,
                 unit_psc,
                 # spike input ports:
                 exc_spikes,
                 ignore_spikes,
                 # continuous input ports:
                 I_stim,
                ):

        # state:
        self._I_syn_exc = I_syn_exc
        self._I_syn_inh = I_syn_inh
        self._refr_t = refr_t
        self._V_m = V_m
        # parameters:
        self._C_m = C_m
        self._E_L = E_L
        self._I_e = I_e
        self._refr_T = refr_T
        self._tau_m = tau_m
        self._tau_syn_exc = tau_syn_exc
        self._tau_syn_inh = tau_syn_inh
        self._V_reset = V_reset
        self._V_th = V_th
        # internals:
        self.___h = __h
        self.___P__I_syn_exc__I_syn_exc = __P__I_syn_exc__I_syn_exc
        self.___P__I_syn_inh__I_syn_inh = __P__I_syn_inh__I_syn_inh
        self.___P__refr_t__refr_t = __P__refr_t__refr_t
        self.___P__V_m__I_syn_exc = __P__V_m__I_syn_exc
        self.___P__V_m__I_syn_inh = __P__V_m__I_syn_inh
        self.___P__V_m__V_m = __P__V_m__V_m
        self._unit_psc = unit_psc
        # spike input ports:
        self._exc_spikes = exc_spikes
        self._ignore_spikes = ignore_spikes
        # continuous input ports:
        self._I_stim = I_stim

        # N.B. variables have to be in the same order as the neuron struct!
        self._struct = Struct([
                 # spike input ports:
            (DataType.S1615,   "exc_spikes"),
            (DataType.S1615,   "ignore_spikes"),
                 # continuous input ports:
            (DataType.S1615,   "I_stim"),
                 # state:
            (DataType.S1615,   "I_syn_exc"),
            (DataType.S1615,   "I_syn_inh"),
            (DataType.S1615,   "refr_t"),
            (DataType.S1615,   "V_m"),
                 # parameters:
            (DataType.S1615,   "C_m"),
            (DataType.S1615,   "E_L"),
            (DataType.S1615,   "I_e"),
            (DataType.S1615,   "refr_T"),
            (DataType.S1615,   "tau_m"),
            (DataType.S1615,   "tau_syn_exc"),
            (DataType.S1615,   "tau_syn_inh"),
            (DataType.S1615,   "V_reset"),
            (DataType.S1615,   "V_th"),
                 # internals:
            (DataType.S1615,   "__h"),
            (DataType.S1615,   "__P__I_syn_exc__I_syn_exc"),
            (DataType.S1615,   "__P__I_syn_inh__I_syn_inh"),
            (DataType.S1615,   "__P__refr_t__refr_t"),
            (DataType.S1615,   "__P__V_m__I_syn_exc"),
            (DataType.S1615,   "__P__V_m__I_syn_inh"),
            (DataType.S1615,   "__P__V_m__V_m"),
            (DataType.S1615,   "unit_psc"),
            ])

    @property
    @overrides(AbstractNeuronImpl.structs)
    def structs(self):
        return [self._struct]

    @property
    @overrides(AbstractNeuronImpl.model_name)
    def model_name(self):
        return "iaf_psc_exp_neuron_nestmlImpl"

    @property
    @overrides(AbstractNeuronImpl.binary_name)
    def binary_name(self):
        s: str = "iaf_psc_exp_neuron_nestml_impl.aplx"
        print("The aplx file for this neuron is: " + s)
        return s

    @overrides(AbstractNeuronImpl.get_global_weight_scale)
    def get_global_weight_scale(self):
        # TODO: Update if a weight scale is required
        return 1.

    @overrides(AbstractNeuronImpl.get_n_synapse_types)
    def get_n_synapse_types(self):
        return 0 \
                + 1 \
                + 1 \
                + 0

    @overrides(AbstractNeuronImpl.get_synapse_id_by_target)
    def get_synapse_id_by_target(self, target):
        if target == "exc_spikes":
            return 0
        if target == "ignore_spikes":
            return 1
        raise ValueError("Unknown target {}".format(target))

    @overrides(AbstractNeuronImpl.get_synapse_targets)
    def get_synapse_targets(self):
        return [
            "exc_spikes",
            "ignore_spikes",
               ]

    @overrides(AbstractNeuronImpl.get_recordable_variables)
    def get_recordable_variables(self):
        return [
            "I_syn_exc",
            "I_syn_inh",
            "refr_t",
            "V_m",
        ]

    @overrides(AbstractNeuronImpl.get_recordable_data_types)
    def get_recordable_data_types(self):
        return {
            "I_syn_exc": DataType.S1615,
            "I_syn_inh": DataType.S1615,
            "refr_t": DataType.S1615,
            "V_m": DataType.S1615,
            }

    @overrides(AbstractNeuronImpl.get_recordable_units)
    def get_recordable_units(self, variable):
        if variable == "V_m":
            return "mV"
        if variable == "refr_t":
            return "ms"
        if variable == "I_syn_exc":
            return "pA"
        if variable == "I_syn_inh":
            return "pA"
        raise ValueError("Unknown variable {}".format(variable))

    @overrides(AbstractNeuronImpl.get_recordable_variable_index)
    def get_recordable_variable_index(self, variable):
        if variable == "I_syn_exc":
            return 0
        if variable == "I_syn_inh":
            return 1
        if variable == "refr_t":
            return 2
        if variable == "V_m":
            return 3

        raise ValueError("Unknown variable {}".format(variable))

    @overrides(AbstractNeuronImpl.is_recordable)
    def is_recordable(self, variable):
        return variable in [
        "V_m",
        "refr_t",
        "I_syn_exc",
        "I_syn_inh",
                           ]

    @overrides(AbstractNeuronImpl.add_parameters)
    def add_parameters(self, parameters):
        parameters["C_m"] = self._C_m
        parameters["tau_m"] = self._tau_m
        parameters["tau_syn_inh"] = self._tau_syn_inh
        parameters["tau_syn_exc"] = self._tau_syn_exc
        parameters["refr_T"] = self._refr_T
        parameters["E_L"] = self._E_L
        parameters["V_reset"] = self._V_reset
        parameters["V_th"] = self._V_th
        parameters["I_e"] = self._I_e
        parameters["unit_psc"] = self._unit_psc
        parameters["__h"] = self.___h
        parameters["__P__I_syn_exc__I_syn_exc"] = self.___P__I_syn_exc__I_syn_exc
        parameters["__P__I_syn_inh__I_syn_inh"] = self.___P__I_syn_inh__I_syn_inh
        parameters["__P__V_m__I_syn_exc"] = self.___P__V_m__I_syn_exc
        parameters["__P__V_m__I_syn_inh"] = self.___P__V_m__I_syn_inh
        parameters["__P__V_m__V_m"] = self.___P__V_m__V_m
        parameters["__P__refr_t__refr_t"] = self.___P__refr_t__refr_t

    @overrides(AbstractNeuronImpl.add_state_variables)
    def add_state_variables(self, state_variables):
                 # state variables:
        state_variables["V_m"] = self._V_m
        state_variables["refr_t"] = self._refr_t
        state_variables["I_syn_exc"] = self._I_syn_exc
        state_variables["I_syn_inh"] = self._I_syn_inh
                 # spike input ports:
        state_variables["exc_spikes"] = self._exc_spikes
        state_variables["ignore_spikes"] = self._ignore_spikes
                 # continuous input ports:
        state_variables["I_stim"] = self._I_stim
                 # internals:
#
#        state_variables["unit_psc"] = self._unit_psc
#
#        state_variables["__h"] = self.___h
#
#        state_variables["__P__I_syn_exc__I_syn_exc"] = self.___P__I_syn_exc__I_syn_exc
#
#        state_variables["__P__I_syn_inh__I_syn_inh"] = self.___P__I_syn_inh__I_syn_inh
#
#        state_variables["__P__V_m__I_syn_exc"] = self.___P__V_m__I_syn_exc
#
#        state_variables["__P__V_m__I_syn_inh"] = self.___P__V_m__I_syn_inh
#
#        state_variables["__P__V_m__V_m"] = self.___P__V_m__V_m
#
#        state_variables["__P__refr_t__refr_t"] = self.___P__refr_t__refr_t
#

    @overrides(AbstractNeuronImpl.get_units)
    def get_units(self, variable):
        # state:
        if variable == "V_m":
            return "mV"
        if variable == "refr_t":
            return "ms"
        if variable == "I_syn_exc":
            return "pA"
        if variable == "I_syn_inh":
            return "pA"
        # parameters:
        if variable == "C_m":
            return "pF"
        if variable == "tau_m":
            return "ms"
        if variable == "tau_syn_inh":
            return "ms"
        if variable == "tau_syn_exc":
            return "ms"
        if variable == "refr_T":
            return "ms"
        if variable == "E_L":
            return "mV"
        if variable == "V_reset":
            return "mV"
        if variable == "V_th":
            return "mV"
        if variable == "I_e":
            return "pA"
        # internals:
        if variable == "unit_psc":
            return "pA"
        if variable == "__h":
            return "ms"
        if variable == "__P__I_syn_exc__I_syn_exc":
            return ""
        if variable == "__P__I_syn_inh__I_syn_inh":
            return ""
        if variable == "__P__V_m__I_syn_exc":
            return ""
        if variable == "__P__V_m__I_syn_inh":
            return ""
        if variable == "__P__V_m__V_m":
            return ""
        if variable == "__P__refr_t__refr_t":
            return ""
        # spike input ports:
        if variable == "exc_spikes":
            return "1 / s"
        if variable == "ignore_spikes":
            return "1 / s"
        # continuous input ports:
        if variable == "I_stim":
            return "pA"

        raise ValueError("Unknown variable {}".format(variable))

    @property
    @overrides(AbstractNeuronImpl.is_conductance_based)
    def is_conductance_based(self):
        # TODO: Update if uses conductance
        return False