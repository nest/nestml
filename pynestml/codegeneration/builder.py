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
from typing import Any, List, Mapping, Optional, Sequence

from abc import ABCMeta, abstractmethod


class Builder(metaclass=ABCMeta):

    _default_options: Mapping[str, Any] = {}

    def __init__(self, target, options: Optional[Mapping[str, Any]]=None):
        if not target.upper() in self.get_known_targets():
            code, msg = Messages.get_unknown_target(target)
            Logger.log_message(message=msg, code=code, log_level=LoggingLevel.ERROR)
            self._target = ""
            raise InvalidTargetException()

        self._target = target
        if "_default_options" in dir(self.__class__):
            self._options = dict(self.__class__._default_options)
        if options:
            self.set_options(options)

    def set_options(self, options: Mapping[str, Any]):
        if not "_default_options" in dir(self.__class__):
            print("Warning: Builder class \"" + str(self.__class__) + "\" does not support setting options.")
        for k in options.keys():
            if k in self.__class__._default_options:
                self._options[k] = options[k]
            else:
                print("Option \"" + str(k) + "\" does not exist in builder")

    def get_option(self, k):
        return self._options[k]

    @staticmethod
    def get_known_targets():
        targets = ["NEST", "NEST2", "autodoc", "none"]
        targets = [s.upper() for s in targets]
        return targets

    @staticmethod
    def from_target_name(target_name: str, options: Optional[Mapping[str, Any]]=None) -> Builder:
        """Static factory method that returns a new instance of a child class of Builder"""
        assert target_name.upper() in Builder.get_known_targets(), "Unknown target platform requested: \"" + str(target_name) + "\""

        if target_name.upper() in ["NEST", "NEST2"]:
            from pynestml.codegeneration.nest_builder import NESTBuilder
            return NESTBuilder(target_name, options)

        return None   # no builder requested or available

    @abstractmethod
    def build(self) -> None:
        pass
