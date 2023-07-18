# -*- coding: utf-8 -*-
#
# with_options.py
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

from typing import Any, Mapping, Optional

import copy


class WithOptions:
    r"""This class allows options (indexed by strings) to be set and retrieved. A set of default options may be supplied by overriding the `_default_options` member in the inheriting class."""

    _default_options: Mapping[str, Any] = {}

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(WithOptions, self).__init__()
        self._options = copy.deepcopy(self.__class__._default_options)
        if options:
            self.set_options(options)

    def get_option(self, k: str) -> Any:
        r"""Get the value of a given option."""
        return self._options[k]

    def option_exists(self, k: str) -> bool:
        r"""Test whether an option exists."""
        return k in self._options.keys()

    def add_options(self, options: Mapping[str, Any]) -> None:
        r"""Extend the current options dictionary with extra options."""
        for key in options:
            if not key in self._options:
                self._options[key] = options[key]
            else:
                raise Exception(f"The key '{key}' already exists in  the options list!")

    def set_options(self, options: Mapping[str, Any]) -> Mapping[str, Any]:
        r"""Set options. "Eats off" any options that it knows how to set, and returns the rest as "unhandled" options."""
        unhandled_options = {}
        for k in options.keys():
            if k in self.__class__._default_options:
                self._options[k] = options[k]
            else:
                unhandled_options[k] = options[k]
        return unhandled_options
