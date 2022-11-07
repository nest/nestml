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

from typing import Any, Mapping, Optional

from abc import ABCMeta, abstractmethod

from pynestml.exceptions.invalid_target_exception import InvalidTargetException
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.utils.with_options import WithOptions


class Builder(WithOptions, metaclass=ABCMeta):
    r"""Compile, build and install the code for a given target platform. Runs after the CodeGenerator."""

    def __init__(self, target, options: Optional[Mapping[str, Any]]=None):
        super(Builder, self).__init__(options)
        from pynestml.frontend.pynestml_frontend import get_known_targets

        if not target.upper() in get_known_targets():
            code, msg = Messages.get_unknown_target(target)
            Logger.log_message(message=msg, code=code, log_level=LoggingLevel.ERROR)
            self._target = ""
            raise InvalidTargetException()

        self._target = target

    @abstractmethod
    def build(self) -> None:
        pass
