# -*- coding: utf-8 -*-
#
# error_listener.py
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

"""
This class contains several method used to parse handed over models and returns them as one or more AST trees.
"""
from antlr4.error.ErrorListener import ConsoleErrorListener, ErrorListener


class NestMLErrorListener(ErrorListener):
    """helper class to listen for parser errors and record whether an error has occurred"""

    def __init__(self):
        super(NestMLErrorListener, self).__init__()
        self._error_occurred = False

    @property
    def error_occurred(self):
        return self._error_occurred

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self._error_occurred = True
