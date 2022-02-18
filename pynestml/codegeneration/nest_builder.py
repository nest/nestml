# -*- coding: utf-8 -*-
#
# nest_builder.py
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
from typing import Any, List, Mapping, Optional, Sequence, TextIO

import os
import platform
import subprocess
import sys

from pynestml.codegeneration.builder import Builder
from pynestml.exceptions.generated_code_build_exception import GeneratedCodeBuildException
from pynestml.exceptions.invalid_path_exception import InvalidPathException
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel


def __add_library_to_sli(lib_path):
    if not os.path.isabs(lib_path):
        lib_path = os.path.abspath(lib_path)

    system = platform.system()
    lib_key = ""

    if system == "Linux":
        lib_key = "LD_LIBRARY_PATH"
    else:
        lib_key = "DYLD_LIBRARY_PATH"

    if lib_key in os.environ:
        current = os.environ[lib_key].split(os.pathsep)
        if lib_path not in current:
            current.append(lib_path)
            os.environ[lib_key] += os.pathsep.join(current)
    else:
        os.environ[lib_key] = lib_path


def add_libraries_to_sli(paths: Union[str, Sequence[str]]):
    '''
    This method can be used to add external modules to SLI environment

    Parameters
    ----------
    paths
        paths to external nest modules
    '''
    if isinstance(paths, str):
        paths = [paths]
    for path in paths:
        __add_library_to_sli(path)


class NESTBuilder(Builder):
    r"""Compile, build and install the NEST C++ code and NEST extension module."""

    _default_options = {
        "nest_path": None
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__("NEST", options)

        if not self.option_exists("nest_path") or not self.get_option("nest_path"):
            try:
                import nest
            except ModuleNotFoundError:
                Logger.log_message(
                    None, -1, "An error occurred while importing the `nest` module in Python. Please check your NEST installation-related environment variables and paths.", None, LoggingLevel.ERROR)
                sys.exit(1)

            nest_path = nest.ll_api.sli_func("statusdict/prefix ::")
            self.set_options({"nest_path": nest_path})
            Logger.log_message(None, -1, "The NEST installation was automatically detected as: " +
                               nest_path, None, LoggingLevel.INFO)

    def build(self, stdout: TextIO = None, stderr: TextIO = None) -> None:
        r"""
        This method can be used to build the generated code and install the resulting extension module into NEST.

        Raises
        ------
        GeneratedCodeBuildException
            If any kind of failure occurs during cmake configuration, build, or install.
        InvalidPathException
            If a failure occurs while trying to access the target path or the NEST installation path.
        """
        error_location = ""
        if stderr is None:
            stderr = subprocess.STDOUT
            error_location = "stdout"
        else:
            error_location = os.path.abspath(stderr.name)

        cmake_cmd = ["cmake"]
        target_path = FrontendConfiguration.get_target_path()
        install_path = FrontendConfiguration.get_install_path()
        if install_path is not None:
            add_libraries_to_sli(install_path)
        nest_path = self.get_option("nest_path")

        if not os.path.isdir(target_path):
            raise InvalidPathException('Target path (' + target_path + ') is not a directory!')

        if nest_path is None or (not os.path.isdir(nest_path)):
            raise InvalidPathException('NEST path (' + str(nest_path) + ') is not a directory!')

        install_prefix = ""
        if install_path:
            if not os.path.isabs(install_path):
                install_path = os.path.abspath(install_path)
            install_prefix = f"-DCMAKE_INSTALL_PREFIX={install_path}"

        nest_config_path = f"-Dwith-nest={os.path.join(nest_path, 'bin', 'nest-config')}"
        cmake_cmd = ['cmake', nest_config_path, install_prefix, '.']
        make_all_cmd = ['make', 'all']
        make_install_cmd = ['make', 'install']

        # remove CMakeCache.txt if exists
        cmake_cache = os.path.join(target_path, "CMakeCache.txt")
        if os.path.exists(cmake_cache):
            os.remove(cmake_cache)

        # check if we run on win
        if sys.platform.startswith('win'):
            shell = True
        else:
            shell = False

        # first call cmake with all the arguments
        try:
            result = subprocess.check_call(cmake_cmd, stderr=stderr, shell=shell, stdout=stdout,
                                           cwd=str(os.path.join(target_path)))
        except subprocess.CalledProcessError as e:
            raise GeneratedCodeBuildException(
                'Error occurred during \'cmake\'! More detailed error messages can be found in stdout.')

        # now execute make all
        try:
            subprocess.check_call(make_all_cmd, stderr=stderr, shell=shell, stdout=stdout,
                                  cwd=str(os.path.join(target_path)))
        except subprocess.CalledProcessError as e:
            raise GeneratedCodeBuildException(
                'Error occurred during \'make all\'! More detailed error messages can be found in stdout.')

        # finally execute make install
        try:
            subprocess.check_call(make_install_cmd, stderr=stderr, shell=shell, stdout=stdout,
                                  cwd=str(os.path.join(target_path)))
        except subprocess.CalledProcessError as e:
            raise GeneratedCodeBuildException(
                'Error occurred during \'make install\'! More detailed error messages can be found in stdout.')
