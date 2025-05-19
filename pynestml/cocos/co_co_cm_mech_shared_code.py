# -*- coding: utf-8 -*-
#
# co_co_cm_mech_shared_code.py
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

from pynestml.cocos.co_co import CoCo
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.utils.channel_processing import ChannelProcessing
from pynestml.utils.concentration_processing import ConcentrationProcessing
from pynestml.utils.receptor_processing import ReceptorProcessing
from pynestml.utils.continuous_input_processing import ContinuousInputProcessing
from pynestml.meta_model.ast_model import ASTModel


class CoCoCmMechSharedCode(CoCo):
    @classmethod
    def check_co_co(cls, model: ASTModel):
        chan_info = ChannelProcessing.get_mechs_info(model)
        conc_info = ConcentrationProcessing.get_mechs_info(model)
        rec_info = ReceptorProcessing.get_mechs_info(model)
        con_in_info = ContinuousInputProcessing.get_mechs_info(model)

        used_vars = dict()
        all_info = chan_info | conc_info | rec_info | con_in_info
        for info_name, info in all_info.items():
            all_vars = list(set(info['States'].keys()) | set(info["Parameters"].keys()) | set(
                info["Internals"].keys()))  # + [e.get_name() for e in info["Dependencies"]["global"]]
            for var in all_vars:
                if var not in used_vars.keys():
                    used_vars[var] = list()
                used_vars[var].append(info_name)

        for var_name, var in used_vars.items():
            if len(var) > 1:
                code, message = Messages.cm_shared_variables_not_allowed(var_name, var)
                Logger.log_message(error_position=None,
                                   code=code, message=message,
                                   log_level=LoggingLevel.ERROR)
