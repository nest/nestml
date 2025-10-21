# -*- coding: utf-8 -*-
#
# test_log_functions_in_odes.py
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

from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestLogFunctionsInODEs:

    def test_log_functions_in_odes(self):
        """
        Tests whether the code is generated for the log functions when used in ODEs.
        """
        generate_nest_target(input_path="resources/equations_log.nestml",
                             target_path="target",
                             logging_level="INFO", )
