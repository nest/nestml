# -*- coding: utf-8 -*-
#
# ast_printer.py
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

from abc import ABCMeta, abstractmethod

from pynestml.meta_model.ast_node import ASTNode


class ASTPrinter(metaclass=ABCMeta):
    r"""
    Printer for ``ASTNode``s.

    Printers are instantiated rather than having only static methods. This is the "compositionality over inheritance" pattern, chosen because "lower" grammar elements need to be printed in different ways (for instance, references to variables which could live in different data structures depending on the context) while the "higher" grammar element printers stay the same (for instance, printing a composite expression).

    Some printers have internal parameters/settings, like the ``with_vector_parameter`` attribute of the ``NESTVariablePrinter``.
    """

    def __init__(self):
        pass

    @abstractmethod
    def print(self, node: ASTNode) -> str:
        raise Exception("Cannot call abstract method")
