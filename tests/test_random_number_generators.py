# -*- coding: utf-8 -*-
#
# test_random_number_generators.py
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

from pynestml.exceptions.code_generation_exception import CodeGenerationException
from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import MessageCode


class TestRandomNumberGeneratorsInODEs:
    """Test that random number sample functions may not appear on the right-hand side of ODEs and as state initialisers."""

    def test_random_number_generators_in_ODEs(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "random_number_generators_test.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"
        try:
            generate_nest_target(input_path,
                                 target_path=target_path,
                                 logging_level=logging_level,
                                 module_name=module_name,
                                 suffix=suffix)
        except CodeGenerationException:
            pass

        assert len(Logger.get_messages("test_random_nestml", LoggingLevel.ERROR, message_code=MessageCode.RANDOM_FUNCTIONS_LEGALLY_USED)) == 6
