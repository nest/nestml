#
# VariableSymbol.py
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
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import Symbol
from enum import Enum


class VariableSymbol(Symbol):
    """
    This class is used to store a single variable symbol containing all required information.
    """
    __blockType = None
    __vectorParameter = None


    def getVectorParameter(self):
        """
        Returns the vector parameter of this symbol if any available, e.g., spike[12]
        :return: the vector parameter of this variable symbol.
        :rtype: str
        """
        return self.__vectorParameter

    def getBlockType(self):
        """
        Returns the type of the block in which this variable-symbol has been declared in.
        :return: the type of block
        :rtype: BlockType
        """
        return self.__blockType

    def printSymbol(self):
        return 'VariableSymbol[' + self.getSymbolName() + ', ' + str(self.getBlockType()) + ', ' \
               + 'array parameter: ' + self.getVectorParameter() + \
               (self.getReferencedObject().getSourcePosition().printSourcePosition() if self.getReferencedObject()
                                                                                        is not None else '') + ')'

    def equals(self, _other=None):
        pass


class BlockType(Enum):
    STATE = 1
    PARAMETERS = 2
    INTERNALS = 3
    EQUATION = 4
    LOCAL = 5
    INPUT_BUFFER_CURRENT = 6
    INPUT_BUFFER_SPIKE = 7
    OUTPUT = 8
    SHAPE = 9
