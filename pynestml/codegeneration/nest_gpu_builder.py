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
        "nest_gpu_path": None,
        "nest_gpu_build_path": None,
        "nest_gpu_install_path": None
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__(options)

        if not self.option_exists("nest_gpu_path") or not self.get_option("nest_gpu_path"):
            if "NEST_GPU" in os.environ:
                nest_gpu_path = os.environ["NEST_GPU"]
            else:
                nest_gpu_path = os.getcwd()
            self.set_options({"nest_gpu_path": nest_gpu_path})
            Logger.log_message(None, -1, "The NEST-GPU path was automatically detected as: " + nest_gpu_path, None,
                               LoggingLevel.INFO)

            build_path = os.path.join(os.path.dirname(nest_gpu_path), "nest-gpu-build")
            install_path = os.path.join(os.path.dirname(nest_gpu_path), "nest-gpu-install")
            self.set_options({"nest_gpu_build_path": build_path, "nest_gpu_install_path": install_path})

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
        nest_gpu_build_path = self.get_option("nest_gpu_build_path")
        nest_gpu_install_path = self.get_option("nest_gpu_install_path")

        if not os.path.isdir(target_path):
            raise InvalidPathException('Target path (' + target_path + ') is not a directory!')

        if nest_gpu_path is None or (not os.path.isdir(nest_gpu_path)):
            raise InvalidPathException('NEST-GPU path (' + str(nest_gpu_path) + ') is not a directory!')

        # Construct the build commands
        mpi_option = "-Dwith-mpi=OFF"
        install_prefix = f"-DCMAKE_INSTALL_PREFIX={nest_gpu_install_path}"
        cmake_cmd = ["cmake", mpi_option, install_prefix, nest_gpu_path]
        make_cmd = ['make']
        make_install_cmd = ['make', 'install']

        # Make build directory
        try:
            os.makedirs(nest_gpu_build_path, exist_ok=True)
        except (FileExistsError, FileNotFoundError):
            raise GeneratedCodeBuildException(
                'Error occurred during \'make\'! More detailed error messages can be found in stdout.')

        # cmake
        try:
            subprocess.check_call(cmake_cmd, stderr=subprocess.STDOUT, cwd=nest_gpu_build_path)
        except subprocess.CalledProcessError as e:
            raise GeneratedCodeBuildException(
                'Error occurred during \'make\'! More detailed error messages can be found in stdout.')

        # now execute make
        try:
            subprocess.check_call(make_cmd, stderr=subprocess.STDOUT, cwd=nest_gpu_build_path)
        except subprocess.CalledProcessError as e:
            raise GeneratedCodeBuildException(
                'Error occurred during \'make\'! More detailed error messages can be found in stdout.')

        # finally execute make install
        try:
            subprocess.check_call(make_install_cmd, stderr=subprocess.STDOUT, cwd=nest_gpu_build_path)
        except subprocess.CalledProcessError as e:
            raise GeneratedCodeBuildException(
                'Error occurred during \'make install\'! More detailed error messages can be found in stdout.')
