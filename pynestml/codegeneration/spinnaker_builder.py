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

from typing import Any, Mapping, Optional, Sequence, Union

import os
import platform
import subprocess
import sys
import fnmatch

from pynestml.codegeneration.builder import Builder
from pynestml.exceptions.generated_code_build_exception import GeneratedCodeBuildException
from pynestml.exceptions.invalid_path_exception import InvalidPathException
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel


class SpiNNakerBuilder(Builder):
    r"""Compiles and build the SpiNNaker generated C code."""

    _default_options = {
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__("SPINNAKER", options)

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
        generated_file_names_neuron_c = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.h")]
        generated_file_names_neuron_py = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.py") and not "impl.py" in fn]
        generated_file_names_neuron_impl_py = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.py") and "impl.py" in fn]
        generated_file_names_makefiles = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "Makefile_*") if not fn == "Makefile"]
        generated_file_names_neuron_c = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.h")]

        old_cwd = os.getcwd()
        try:
            os.chdir(install_path)

            make_cmd = ['make']

            # check if we run on win
            if sys.platform.startswith('win'):
                shell = True
            else:
                shell = False

            # copy C files from target to install directory
            try:
                os.mkdir(os.path.join(install_path, "c_models"))
            except:
                pass

            try:
                os.mkdir(os.path.join(install_path, "c_models/src"))
            except:
                pass

            try:
                os.mkdir(os.path.join(install_path, "c_models/src/my_models"))
            except:
                pass

            try:
                os.mkdir(os.path.join(install_path, "c_models/src/my_models/implementations"))
            except:
                pass

            for fn in generated_file_names_neuron_c:
                try:
                    subprocess.check_call(["cp", fn, os.path.join(install_path, "c_models", "src", "my_models", "implementations")], stderr=subprocess.STDOUT, shell=shell,
                                        cwd=str(os.path.join(target_path)))
                except subprocess.CalledProcessError as e:
                    raise GeneratedCodeBuildException(
                        'Error occurred during install! More detailed error messages can be found in stdout.')

            # copy python files from target to install directory

            try:
                os.mkdir(os.path.join(install_path, "python_models8"))
            except:
                pass

            try:
                os.mkdir(os.path.join(install_path, "python_models8", "neuron"))
            except:
                pass

            try:
                os.mkdir(os.path.join(install_path, "python_models8", "neuron", "builds"))
            except:
                pass

            for fn in generated_file_names_neuron_py:
                try:
                    subprocess.check_call(["cp", fn, os.path.join(install_path, "python_models8", "neuron", "builds")], stderr=subprocess.STDOUT, shell=shell,
                                        cwd=target_path)
                except subprocess.CalledProcessError as e:
                    raise GeneratedCodeBuildException(
                        'Error occurred during install! More detailed error messages can be found in stdout.')

            # Copy the pyNN implementation file
            try:
                os.makedirs(os.path.join(install_path, "python_models8", "neuron", "implementations"))
            except:
                pass

            for fn in generated_file_names_neuron_impl_py:
                try:
                    subprocess.check_call(["cp", os.path.join(target_path, fn), os.path.join(install_path, "python_models8", "neuron", "implementations")], stderr=subprocess.STDOUT, shell=shell,
                                        cwd=target_path)
                except subprocess.CalledProcessError as e:
                    raise GeneratedCodeBuildException(
                        'Error occurred during install! More detailed error messages can be found in stdout.')

            # copy makefiles
            try:
                os.makedirs(os.path.join(install_path, "python_models8", "model_binaries"))
            except:
                pass

            # Copy the root Makefile
            try:
                os.makedirs(os.path.join(install_path, "c_models", "makefiles"))
            except:
                pass

            try:
                subprocess.check_call(["cp", "Makefile_root", os.path.join(install_path, "c_models", "Makefile")], stderr=subprocess.STDOUT, shell=shell,
                                    cwd=target_path)
            except subprocess.CalledProcessError as e:
                raise GeneratedCodeBuildException(
                    'Error occurred during install! More detailed error messages can be found in stdout.')

            try:
                subprocess.check_call(["cp", "Makefile_models", os.path.join(install_path, "c_models", "makefiles", "Makefile")], stderr=subprocess.STDOUT, shell=shell,
                                    cwd=target_path)
            except subprocess.CalledProcessError as e:
                raise GeneratedCodeBuildException(
                    'Error occurred during install! More detailed error messages can be found in stdout.')

            # Copy the extra.mk file
            try:
                subprocess.check_call(["cp", "extra.mk", os.path.join(install_path, "c_models", "makefiles")], stderr=subprocess.STDOUT, shell=shell,
                                    cwd=target_path)
            except subprocess.CalledProcessError as e:
                raise GeneratedCodeBuildException(
                    'Error occurred during install! More detailed error messages can be found in stdout.')

            # Copy the extra_neuron.mk file
            try:
                subprocess.check_call(["cp", "extra_neuron.mk", os.path.join(install_path, "c_models", "makefiles")], stderr=subprocess.STDOUT, shell=shell,
                                    cwd=target_path)
            except subprocess.CalledProcessError as e:
                raise GeneratedCodeBuildException(
                    'Error occurred during install! More detailed error messages can be found in stdout.')

            # Copy the model Makefile
            for fn in generated_file_names_makefiles:
                neuron_subdir = fn[len("Makefile_"):]

                try:
                    os.mkdir(os.path.join(install_path, "c_models", "makefiles", neuron_subdir))
                except:
                    pass

                try:
                    try:
                        os.makedirs(os.path.join(install_path, "c_models", "makefiles", neuron_subdir))
                    except:
                        pass
                    subprocess.check_call(["cp", fn, os.path.join(install_path, "c_models", "makefiles", neuron_subdir, "Makefile")], stderr=subprocess.STDOUT, shell=shell,
                                        cwd=target_path)
                except subprocess.CalledProcessError as e:
                    raise GeneratedCodeBuildException(
                        'Error occurred during install! More detailed error messages can be found in stdout.')

            # Copy the .h files of the neuron model
            try:
                os.makedirs(os.path.join(install_path, "c_models", "src", "my_models", "implementations"))
            except:
                pass
            for fn in generated_file_names_neuron_c:
                try:
                    subprocess.check_call(["cp", fn, os.path.join(install_path, "c_models", "src", "my_models", "implementations", fn)], stderr=subprocess.STDOUT, shell=shell,
                                          cwd=target_path)
                except:
                    raise GeneratedCodeBuildException(
                        'Error occurred during install! More detailed error messages can be found in stdout.')

            # call make
            try:
                subprocess.check_call(make_cmd, stderr=subprocess.STDOUT, shell=shell,
                                      cwd=str(os.path.join(install_path, "c_models", "makefiles")))
            except subprocess.CalledProcessError as e:
                raise GeneratedCodeBuildException(
                    'Error occurred during \'make\'! More detailed error messages can be found in stdout.')
        finally:
            os.chdir(old_cwd)
