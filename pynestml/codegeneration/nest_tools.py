# -*- coding: utf-8 -*-
#
# nest_tools.py
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

import multiprocessing as mp
import sys

from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel


def _detect_nest_version(user_args):
    try:
        import nest

        vt = nest.Create("volume_transmitter")

        try:
            neuron = nest.Create('hh_psc_alpha_clopath')
        except Exception:
            pass

        if "DataConnect" in dir(nest):
            nest_version = "v2.20.2"
        elif "kernel_status" not in dir(nest):  # added in v3.1
            nest_version = "v3.0"
        elif "prepared" in nest.GetKernelStatus().keys():  # "prepared" key was added after v3.3 release
            nest_version = "master"
        elif "tau_u_bar_minus" in neuron.get().keys():   # added in v3.3
            nest_version = "v3.3"
        elif "tau_Ca" in vt.get().keys():   # removed in v3.2
            nest_version = "v3.1"
        else:
            nest_version = "v3.2"

    except ModuleNotFoundError:
        nest_version = ""

    return nest_version


class NESTTools:
    r"""Helper functions for NEST Simulator"""

    @classmethod
    def detect_nest_version(cls) -> str:
        r"""Auto-detect NEST Simulator installed version. The returned string corresponds to a git tag or git branch name.

        Do this in a separate process to avoid potential side-effects of import the ``nest`` Python module.

        .. admonition::

           NEST version detection needs improvement. See https://github.com/nest/nest-simulator/issues/2116
        """

        p = mp.Pool(processes=1)
        nest_version = p.map(_detect_nest_version, [None])[0]
        p.close()

        if nest_version == "":
            Logger.log_message(None, -1, "An error occurred while importing the `nest` module in Python. Please check your NEST installation-related environment variables and paths, or specify ``nest_version`` manually in the code generator options.", None, LoggingLevel.ERROR)
            sys.exit(1)

        Logger.log_message(None, -1, "The NEST Simulator version was automatically detected as: " + nest_version, None, LoggingLevel.INFO)

        return nest_version
