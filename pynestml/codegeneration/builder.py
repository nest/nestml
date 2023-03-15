# -*- coding: utf-8 -*-
#
# builder.py
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
import subprocess
import os

from typing import Any, Mapping, Optional

from abc import ABCMeta, abstractmethod

from pynestml.exceptions.invalid_target_exception import InvalidTargetException
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.utils.with_options import WithOptions


class Builder(WithOptions, metaclass=ABCMeta):
    r"""Compile, build and install the code for a given target platform. Runs after the CodeGenerator."""

    def __init__(self, target, options: Optional[Mapping[str, Any]] = None):
        super(Builder, self).__init__(options)
        self.process_output_redirection_(options)
        from pynestml.frontend.pynestml_frontend import get_known_targets

        if not target.upper() in get_known_targets():
            code, msg = Messages.get_unknown_target(target)
            Logger.log_message(message=msg, code=code, log_level=LoggingLevel.ERROR)
            self._target = ""
            raise InvalidTargetException()

        self._target = target

    def process_output_redirection_(self, options):
        require_redirect_key = options.get("redirect_build_output", False)
        redirection_path_key = options.get("build_output_dir", "")

        # default values. The output will be printed to the console.
        stdout = None
        stderr = subprocess.STDOUT
        redirect = False
        error_location = "stderr"

        if options and len(options) > 0 and require_redirect_key:
            output_file_name = f"{self.get_builder_name()}_stdout.txt"
            error_file_name = f"{self.get_builder_name()}_stderr.txt"

            if redirection_path_key != "":
                if not os.path.isdir(redirection_path_key):
                    raise Exception(f"The provided directory {redirection_path_key} does not exist in your system!")
                else:
                    stdout = os.path.join(redirection_path_key, output_file_name)
                    stderr = os.path.join(redirection_path_key, error_file_name)
            else:
                target_path = FrontendConfiguration.get_target_path()
                stdout = os.path.join(target_path, output_file_name)
                stderr = os.path.join(target_path, error_file_name)

            error_location = stderr
            redirect = True

        self.add_options({"stdout": stdout, "stderr": stderr, "redirect": redirect, "error_location": error_location})

    @abstractmethod
    def build(self) -> None:
        pass

    def get_builder_name(self) -> str:
        return self.__class__.__name__

    def set_options(self, options: Mapping[str, Any]) -> Mapping[str, Any]:
        ret = super().set_options(options)
        ret.pop("redirect_build_output", None)
        ret.pop("build_output_dir", None)
        return ret
