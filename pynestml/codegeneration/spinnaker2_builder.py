# -*- coding: utf-8 -*-
#
# spinnaker_builder.py
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

from __future__ import annotations

from typing import Any, Mapping, Optional

import os
import subprocess
import sys
import fnmatch

from pynestml.codegeneration.builder import Builder
from pynestml.exceptions.generated_code_build_exception import GeneratedCodeBuildException
from pynestml.exceptions.invalid_path_exception import InvalidPathException
from pynestml.frontend.frontend_configuration import FrontendConfiguration


class SpiNNaker2Builder(Builder):
    r"""
    Compiles and build the SpiNNaker2 Python Class and generated C code.
    """


    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__(options)

    def build(self) -> None:
        r"""
        This method can be used to build the generated code.

        Raises
        ------
        GeneratedCodeBuildException
            If any kind of failure occurs during compile or build.
        InvalidPathException
            If a failure occurs while trying to access the target path or the SpiNNaker installation path.
        """
        target_path = FrontendConfiguration.get_target_path()

        if not os.path.isdir(target_path):
            raise InvalidPathException('Target path (' + target_path + ') is not a directory!')

        install_path = FrontendConfiguration.get_install_path()

        if install_path is None or not os.path.isdir(install_path):
            raise InvalidPathException('Installation path (' + str(install_path) + ') is not a directory!')

        generated_file_names = os.listdir(target_path)
        generated_file_names_neuron_py = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.py") and not "impl.py" in fn and not "example" in fn]
        generated_file_names_synapse_types = [fn for fn in generated_file_names if fn in {'synapse_types.h', 'synapse_types_exponential_impl.h'}]
        generated_file_names_common = [fn for fn in generated_file_names if fn in {'maths-util.h', 'neuron-typedefs.h'}]

        old_cwd = os.getcwd()
        try:
            os.chdir(install_path)

            # check if we run on win
            if sys.platform.startswith('win'):
                shell = True
            else:
                shell = False

            try:
                os.mkdir(os.path.join(install_path, "PySpiNNaker2Application"))
                for fn in generated_file_names_neuron_py:
                    subprocess.check_call(["cp", "-v", fn, os.path.join(install_path, "PySpiNNaker2Application")],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=target_path)
                    subprocess.check_call(["rm", "-rf", fn, os.path.join(target_path, fn)],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=target_path)

            except:
                pass

            try:
                os.mkdir(os.path.join(target_path, "common"))
                for fn in generated_file_names_common:
                    subprocess.check_call(["cp", "-v", fn, os.path.join(target_path, "common")],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=target_path)
                    subprocess.check_call(["rm", "-rf", fn, os.path.join(target_path, fn)],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=target_path)
            except:
                pass

            try:
                os.mkdir(os.path.join(target_path, "synapse_types"))
                for fn in generated_file_names_synapse_types:
                    subprocess.check_call(["cp", "-v", fn, os.path.join(target_path, "synapse_types")],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=target_path)
                    subprocess.check_call(["rm", "-rf", fn, os.path.join(target_path, fn)],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=target_path)
            except:
                pass
            try:
                for name in os.listdir(old_cwd):
                    if name.startswith("nestml_python_target_"):
                        subprocess.check_call(["rm", "-rf", os.path.join(old_cwd, name)],
                                              stderr=subprocess.STDOUT,
                                              shell=shell)
            except Exception as e:
                print(f"Error deleting temporary directories: {e}")
        finally:
            os.chdir(old_cwd)
