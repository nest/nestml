# -*- coding: utf-8 -*-
#
# nest_gpu_builder.py
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
import subprocess

from typing import Optional, Mapping, Any

from pynestml.codegeneration.builder import Builder
from pynestml.exceptions.generated_code_build_exception import GeneratedCodeBuildException
from pynestml.exceptions.invalid_path_exception import InvalidPathException
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.utils.logger import Logger, LoggingLevel


class NESTGPUBuilder(Builder):
    """
    Compile and build the model code for NEST GPU
    """

    _default_options = {
        "nest_gpu_path": None
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__("NEST_GPU", options)

        if not self.option_exists("nest_gpu_path") or not self.get_option("nest_gpu_path"):
            if "NEST_GPU" in os.environ:
                nest_gpu_path = os.environ["NEST_GPU"]
            else:
                nest_gpu_path = os.getcwd()
            self.set_options({"nest_gpu_path": nest_gpu_path})
            Logger.log_message(None, -1, "The NEST-GPU path was automatically detected as: " + nest_gpu_path, None,
                               LoggingLevel.INFO)

    def build(self) -> None:
        """
        Method to build the generated code for NEST GPU target.

        Raises
        ------
        GeneratedCodeBuildException
            If any kind of failure occurs during cmake configuration, build, or install.
        InvalidPathException
            If a failure occurs while trying to access the target path or the NEST installation path.
        """
        target_path = FrontendConfiguration.get_target_path()
        nest_gpu_path = self.get_option("nest_gpu_path")

        if not os.path.isdir(target_path):
            raise InvalidPathException('Target path (' + target_path + ') is not a directory!')

        if nest_gpu_path is None or (not os.path.isdir(nest_gpu_path)):
            raise InvalidPathException('NEST-GPU path (' + str(nest_gpu_path) + ') is not a directory!')

        # Construct the build commands
        autoreconf_cmd = ["autoreconf",  "-i"]
        config_args = [f"--prefix={nest_gpu_path}", f"--exec-prefix={nest_gpu_path}", "--with-gpu-arch=sm_80"]
        config_cmd = ["./configure"]
        config_cmd.extend(config_args)
        make_cmd = ['make']
        make_install_cmd = ['make', 'install']

        # a workaround for now
        # TODO: obtain this path automatically
        working_dir = str(os.path.join(nest_gpu_path, "repo"))

        # first call autoreconf command
        try:
            subprocess.check_call(autoreconf_cmd, stderr=subprocess.STDOUT, cwd=working_dir)
        except subprocess.CalledProcessError as e:
            raise GeneratedCodeBuildException(
                'Error occurred during \'autoreconf\'! More detailed error messages can be found in stdout.')

        # execute config command
        try:
            subprocess.check_call(config_cmd, stderr=subprocess.STDOUT, cwd=working_dir)
        except subprocess.CalledProcessError as e:
            raise GeneratedCodeBuildException(
                'Error occurred during \'configure\'! More detailed error messages can be found in stdout.')

        # now execute make
        try:
            subprocess.check_call(make_cmd, stderr=subprocess.STDOUT, cwd=working_dir)
        except subprocess.CalledProcessError as e:
            raise GeneratedCodeBuildException(
                'Error occurred during \'make\'! More detailed error messages can be found in stdout.')

        # finally execute make install
        try:
            subprocess.check_call(make_install_cmd, stderr=subprocess.STDOUT, cwd=working_dir)
        except subprocess.CalledProcessError as e:
            raise GeneratedCodeBuildException(
                'Error occurred during \'make install\'! More detailed error messages can be found in stdout.')
