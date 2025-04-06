# -*- coding: utf-8 -*-
#
# code_generator_utils.py
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

from typing import List, Optional

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.utils.string_utils import removesuffix


class CodeGeneratorUtils:

    @classmethod
    def get_model_types_from_names(cls, models: List[str], neuron_models: Optional[List[str]] = None, synapse_models: Optional[List[str]] = None):
        r"""
        Returns a prefix corresponding to the origin of the variable symbol.
        :param variable_symbol: a single variable symbol.
        :return: the corresponding prefix
        """
        if neuron_models is None:
            neuron_models = []

        if synapse_models is None:
            synapse_models = []

        neurons = []
        synapses = []
        for model in models:
            pure_name = removesuffix(removesuffix(model.name.split("_with_")[0], "_"), FrontendConfiguration.suffix)
            if pure_name in synapse_models \
               or (pure_name.endswith("synapse")
                   and not pure_name in neuron_models):
                synapses.append(model)
            else:
                neurons.append(model)

        return neurons, synapses
