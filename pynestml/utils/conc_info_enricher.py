# -*- coding: utf-8 -*-
#
# conc_info_enricher.py
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
from collections import defaultdict

from pynestml.utils.mechs_info_enricher import MechsInfoEnricher


class ConcInfoEnricher(MechsInfoEnricher):
    """
    This file is part of the compartmental code generation process.

    Class extends MechsInfoEnricher by the computation of the inline derivative. This hasn't been done in the
    channel processing because it would cause a circular dependency through the coco checks used by the ModelParser
    which we need to use.
    """
    def __init__(self, params):
        super(MechsInfoEnricher, self).__init__(params)

    @classmethod
    def enrich_mechanism_specific(cls, neuron, mechs_info):
        mechs_info = cls.ode_toolbox_processing_for_root_expression(neuron, mechs_info)
        return mechs_info

    @classmethod
    def ode_toolbox_processing_for_root_expression(cls, neuron, conc_info):
        """applies the ode_toolbox_processing to the root_expression since that was never appended to the list of ODEs
        in the base processing and thereby also never went through the ode_toolbox processing"""
        for concentration_name, concentration_info in conc_info.items():
            # Create fake mechs_info such that it can be processed by the existing ode_toolbox_processing function.
            fake_conc_info = defaultdict()
            fake_concentration_info = defaultdict()
            fake_concentration_info["ODEs"] = list()
            fake_concentration_info["ODEs"].append(concentration_info["root_expression"])
            fake_conc_info["fake"] = fake_concentration_info

            fake_conc_info = cls.get_transformed_ode_equations(fake_conc_info)
            fake_conc_info = cls.ode_toolbox_processing(neuron, fake_conc_info)
            cls.add_propagators_to_internals(neuron, fake_conc_info)
            fake_conc_info = cls.transform_ode_solutions(neuron, fake_conc_info)

            conc_info[concentration_name]["ODEs"] = {**conc_info[concentration_name]["ODEs"], **fake_conc_info["fake"]["ODEs"]}
            if "time_resolution_var" in fake_conc_info["fake"]:
                conc_info[concentration_name]["time_resolution_var"] = fake_conc_info["fake"]["time_resolution_var"]

        return conc_info
