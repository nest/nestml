# -*- coding: utf-8 -*-
#
# model_installer.py
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
import sys

from pynestml.exceptions.invalid_path_exception import InvalidPathException
from pynestml.exceptions.generated_code_build_exception import GeneratedCodeBuildException


def install_nest(target_path: str, nest_path: str, install_path: str = None) -> None:
    """
    This method can be used to build the generated code and install the resulting extension module into NEST.

    Parameters
    ----------
    target_path : str
        Path to the target directory, which should contain the generated code artifacts (target platform code and CMake configuration file).
    nest_path : str
        Path to the NEST installation, which should point to the main directory where NEST is installed. This folder contains the ``bin``, ``lib(64)``, ``include``, and ``share`` folders of the NEST install. The ``bin`` folder should contain the ``nest-config`` script, which is accessed by NESTML to perform the installation. This path is the same as that passed through the ``-Dwith-nest`` argument of the CMake command before building the generated NEST module. The suffix ``bin/nest-config`` will be automatically appended to ``nest_path``.
    install_path: str
        Path to the install directory, where the generated module library will be created.

    Raises
    ------
    GeneratedCodeBuildException
        If any kind of failure occurs during cmake configuration, build, or install.
    InvalidPathException
        If a failure occurs while trying to access the target path or the NEST installation path.
    """
    cmake_cmd = ["cmake"]
    if not os.path.isdir(nest_path):
        raise InvalidPathException(f"NEST path ({nest_path}) is not a directory!")

    nest_config_path = f"-Dwith-nest={os.path.join(nest_path, 'bin', 'nest-config')}"
    cmake_cmd.append(nest_config_path)

    if install_path:
        if not os.path.isabs(install_path):
            install_path = os.path.abspath(install_path)
        install_prefix = f"-DCMAKE_INSTALL_PREFIX={install_path}"
        cmake_cmd.append(install_prefix)

    if not os.path.isdir(target_path):
        raise InvalidPathException(f"Target path ({target_path}) is not a directory!")

    cmake_cmd.append('.')
    make_all_cmd = ['make', 'all']
    make_install_cmd = ['make', 'install']

    # check if we run on win
    if sys.platform.startswith('win'):
        shell = True
    else:
        shell = False

    # remove CMakeCache.txt if exists
    cmake_cache = os.path.join(target_path, "CMakeCache.txt")
    if os.path.exists(cmake_cache):
        os.remove(cmake_cache)

    # first call cmake with all the arguments
    try:
        result = subprocess.check_call(cmake_cmd, stderr=subprocess.STDOUT,
                                       shell=shell, cwd=str(os.path.join(target_path)))
    except subprocess.CalledProcessError as e:
        msg = "Error during 'cmake'. More detailed error messages can be found in stdout."
        raise GeneratedCodeBuildException(msg)

    # now execute make all
    try:
        subprocess.check_call(make_all_cmd, stderr=subprocess.STDOUT, shell=shell, cwd=target_path)
    except subprocess.CalledProcessError as e:
        msg = "Error during 'make all'. More detailed error messages can be found in stdout."
        raise GeneratedCodeBuildException(msg)

    # finally execute make install
    try:
        subprocess.check_call(make_install_cmd, stderr=subprocess.STDOUT, shell=shell, cwd=target_path)
    except subprocess.CalledProcessError as e:
        msg = "Error during 'make install'. More detailed error messages can be found in stdout."
        raise GeneratedCodeBuildException(msg)
