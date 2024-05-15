# -*- coding: utf-8 -*-
#
# autodoc_builder.py
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
import os.path
from typing import Optional, Mapping, Any

from pynestml.codegeneration.autodoc_code_generator_utils import AutoDocCodeGeneratorUtils
from pynestml.codegeneration.builder import Builder
from pynestml.exceptions.generated_code_build_exception import GeneratedCodeBuildException
from pynestml.frontend.frontend_configuration import FrontendConfiguration


class AutodocBuilder(Builder):

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__("AUTODOC", options)

    def build(self) -> None:
        target_path = FrontendConfiguration.get_target_path()

        try:
            AutoDocCodeGeneratorUtils.generate_docs(target_path)
        except Exception:
            raise GeneratedCodeBuildException("Error occurred while building autodocs")
