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
from pynestml.meta_model.ast_model import ASTModel
from pynestml.utils.string_utils import removesuffix


class CodeGeneratorUtils:

    @classmethod
    def get_model_types_from_names(cls, models: List[ASTModel], synapse_models: Optional[List[str]] = None):
        r"""
        Determine which models are neuron models, and which are synapse models. All model names given in ``synapse_models``, as well as models of which the name ends in ``synapse``, are taken to be synapse models. All others are taken to be neuron models.

        :param models: a list of models
        :param synapse_models: a list of model names that should be interpreted as synapse models.
        :return: a tuple ``(neurons, synapses)``, each element a list of strings containing model names.
        """

        if synapse_models is None:
            synapse_models = []

        neurons = []
        synapses = []
        for model in models:
            stripped_model_name = removesuffix(removesuffix(model.name.split("_with_")[0], "_"), FrontendConfiguration.suffix)

            if stripped_model_name in synapse_models \
               or stripped_model_name.endswith("synapse"):
                synapses.append(model)
            else:
                neurons.append(model)

        return neurons, synapses
