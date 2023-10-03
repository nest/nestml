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
        "neuron_synapse_pairs": [],
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
        generated_file_names_neuron_py = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.py") and not "impl.py" in fn and not "example" in fn]
        generated_file_names_neuron_impl_py = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.py") and "impl.py" in fn]
        generated_file_names_makefiles = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "Makefile_*") if not fn == "Makefile"]
        generated_file_names_neuron_c = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.c")]
        generated_file_names_neuron_h = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.h")]
        generated_file_names_neuron_examples_py = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.py") and "example" in fn]

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
            except (FileExistsError, FileNotFoundError):
                pass

            try:
                os.mkdir(os.path.join(install_path, "c_models/src"))
            except (FileExistsError, FileNotFoundError):
                pass

            try:
                os.mkdir(os.path.join(install_path, "c_models/src/my_models"))
            except (FileExistsError, FileNotFoundError):
                pass

            try:
                os.mkdir(os.path.join(install_path, "c_models/src/my_models/implementations"))
            except (FileExistsError, FileNotFoundError):
                pass

            for fn in generated_file_names_neuron_c:
                try:
                    to_path = os.path.join(install_path, "c_models", "src", "my_models", "implementations")
                    print("Copying \"" + fn + "\" to " + to_path)
                    subprocess.check_call(["cp", "-v", fn, to_path],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=str(os.path.join(target_path)))
                except subprocess.CalledProcessError:
                    pass

            for fn in generated_file_names_neuron_h:
                try:
                    to_path = os.path.join(install_path, "c_models", "src", "my_models", "implementations")
                    print("Copying \"" + fn + "\" to " + to_path)
                    subprocess.check_call(["cp", "-v", fn, to_path],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=str(os.path.join(target_path)))
                except subprocess.CalledProcessError:
                    pass

            # copy python files from target to install directory

            try:
                os.mkdir(os.path.join(install_path, "python_models8"))
            except (FileExistsError, FileNotFoundError):
                pass

            try:
                to_path = os.path.join(install_path, "python_models8")
                subprocess.check_call(["cp", "-v", "__init__.py", to_path],
                                      stderr=subprocess.STDOUT,
                                      shell=shell,
                                      cwd=str(os.path.join(target_path)))
            except Exception:
                pass

            try:
                os.mkdir(os.path.join(install_path, "python_models8", "neuron"))
            except (FileExistsError, FileNotFoundError):
                pass

            try:
                os.mkdir(os.path.join(install_path, "python_models8", "neuron", "builds"))
            except (FileExistsError, FileNotFoundError):
                pass

            to_path = os.path.join(install_path, "python_models8", "neuron", "builds")
            for fn in generated_file_names_neuron_py:
                try:
                    print("Copying \"" + fn + "\" to " + to_path)
                    subprocess.check_call(["cp", "-v", fn, to_path],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=target_path)
                except subprocess.CalledProcessError:
                    pass

            # Copy the pyNN implementation file
            try:
                os.makedirs(os.path.join(install_path, "python_models8", "neuron", "implementations"))
            except (FileExistsError, FileNotFoundError):
                pass

            for fn in generated_file_names_neuron_impl_py:
                try:
                    to_path = os.path.join(install_path, "python_models8", "neuron", "implementations")
                    print("Copying \"" + fn + "\" to " + to_path)
                    subprocess.check_call(["cp", "-v", os.path.join(target_path, fn), to_path],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=target_path)
                except subprocess.CalledProcessError:
                    pass  # no problem if file is already there and gets overwritten

            # Copy the example files
            try:
                os.mkdir(os.path.join(install_path, "examples"))
            except (FileExistsError, FileNotFoundError):
                pass

            for fn in generated_file_names_neuron_examples_py:
                try:
                    to_path = os.path.join(install_path, "examples")
                    print("Copying \"" + fn + "\" to " + to_path)
                    subprocess.check_call(["cp", "-v", os.path.join(target_path, fn), to_path],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=target_path)
                except subprocess.CalledProcessError:
                    pass  # no problem if file is already there and gets overwritten

            # create python_models8 module directory
            try:
                os.makedirs(os.path.join(install_path, "python_models8", "model_binaries"))
            except (FileExistsError, FileNotFoundError):
                pass

            try:
                subprocess.check_call(["touch", os.path.join(install_path, "python_models8", "model_binaries", "__init__.py")])
            except Exception:
                pass

            # Copy the root Makefile
            try:
                os.makedirs(os.path.join(install_path, "c_models", "makefiles"))
            except (FileExistsError, FileNotFoundError):
                pass

            try:
                subprocess.check_call(["cp", "-v", "Makefile_root", os.path.join(install_path, "c_models", "Makefile")],
                                      stderr=subprocess.STDOUT,
                                      shell=shell,
                                      cwd=target_path)
            except subprocess.CalledProcessError:
                pass

            try:
                subprocess.check_call(["cp", "-v", "Makefile_models", os.path.join(install_path, "c_models", "makefiles", "Makefile")],
                                      stderr=subprocess.STDOUT,
                                      shell=shell,
                                      cwd=target_path)
            except subprocess.CalledProcessError:
                pass

            # Copy the extra.mk file
            try:
                subprocess.check_call(["cp", "-v", "extra.mk", os.path.join(install_path, "c_models", "makefiles")],
                                      stderr=subprocess.STDOUT,
                                      shell=shell,
                                      cwd=target_path)
            except subprocess.CalledProcessError:
                pass

            # Copy the extra_neuron.mk file
            try:
                subprocess.check_call(["cp", "-v", "extra_neuron.mk", os.path.join(install_path, "c_models", "makefiles")],
                                      stderr=subprocess.STDOUT,
                                      shell=shell,
                                      cwd=target_path)
            except subprocess.CalledProcessError:
                pass

            # Copy the model Makefile
            for fn in generated_file_names_makefiles:
                neuron_subdir = fn[len("Makefile_"):]

                try:
                    os.mkdir(os.path.join(install_path, "c_models", "makefiles", neuron_subdir))
                except (FileExistsError, FileNotFoundError):
                    pass

                try:
                    try:
                        os.makedirs(os.path.join(install_path, "c_models", "makefiles", neuron_subdir))
                    except (FileExistsError, FileNotFoundError):
                        pass

                    subprocess.check_call(["cp", "-v", fn, os.path.join(install_path, "c_models", "makefiles", neuron_subdir, "Makefile")],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=target_path)
                except subprocess.CalledProcessError:
                    pass

            # Copy the .h files of the neuron model
            try:
                os.makedirs(os.path.join(install_path, "c_models", "src", "my_models", "implementations"))
            except (FileExistsError, FileNotFoundError):
                pass

            for fn in generated_file_names_neuron_c:
                try:
                    subprocess.check_call(["cp", "-v", fn, os.path.join(install_path, "c_models", "src", "my_models", "implementations", fn)],
                                          stderr=subprocess.STDOUT,
                                          shell=shell,
                                          cwd=target_path)
                except subprocess.CalledProcessError:
                    pass

            # call make clean
            try:
                subprocess.check_call(["make", "clean"],
                                      stderr=subprocess.STDOUT,
                                      shell=shell,
                                      cwd=str(os.path.join(install_path, "c_models")))
            except subprocess.CalledProcessError:
                raise GeneratedCodeBuildException(
                    'Error occurred during \'make clean\'! More detailed error messages can be found in stdout.')

            # call make
            try:
                subprocess.check_call(make_cmd,
                                      stderr=subprocess.STDOUT,
                                      shell=shell,
                                      cwd=str(os.path.join(install_path, "c_models", "makefiles")))
            except subprocess.CalledProcessError:
                raise GeneratedCodeBuildException(
                    'Error occurred during \'make\'! More detailed error messages can be found in stdout.')
        finally:
            os.chdir(old_cwd)
