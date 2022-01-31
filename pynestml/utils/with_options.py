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
        return self._options[k]

    def option_exists(self, k: str) -> bool:
        return k in self._options.keys()

    def set_options(self, options: Mapping[str, Any]):
        for k in options.keys():
            if k in self.__class__._default_options:
                self._options[k] = options[k]
            else:
                print("Option \"" + str(k) + "\" does not exist in builder")
