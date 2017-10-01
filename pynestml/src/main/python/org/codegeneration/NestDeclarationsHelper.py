#
# NestDeclarationsHelper.py
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
from pynestml.src.main.python.org.nestml.ast.ASTDeclaration import ASTDeclaration
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.src.main.python.org.codegeneration.NESTML2NESTTypeConverter import NESTML2NESTTypeConverter


class NestDeclarationsHelper(object):
    """
    This class contains several methods as used during generation of code.
    """
    nestml2NESTTypeConverter = None

    def __init__(self):
        """
        Initialized the declaration helper.
        """
        self.nestml2NESTTypeConverter = NESTML2NESTTypeConverter()
        return

    def getVariables(self, _astDeclaration=None):
        """
        For a given ast declaration it returns a list of all corresponding variable symbols.
        :param _astDeclaration: a single ast declaration.
        :type _astDeclaration: ASTDeclaration
        :return: a list of all corresponding variable symbols.
        :rtype: list(VariableSymbol)
        """
        assert (_astDeclaration is not None and isinstance(_astDeclaration, ASTDeclaration)), \
            '(PyNestML.CodeGeneration.DeclarationsHelper) No or wrong type of declaration provided (%s)!' % type(
                _astDeclaration)
        ret = list()
        for var in _astDeclaration.getVariables():
            symbol = _astDeclaration.getScope().resolveToSymbol(var.getCompleteName())
            if symbol is not None:
                ret.append(symbol)
            else:
                Logger.logMessage('Symbol could not be resolve!', LOGGING_LEVEL.ERROR)
        return ret

    def printVariableType(self, _variableSymbol=None):
        """
        Prints the type of the variable symbol to a corresponding nest representation.
        :param _variableSymbol: a single variable symbol
        :type _variableSymbol: VariableSymbol
        :return: a string presentation of the variable symbol's type
        :rtype: str
        """
        if _variableSymbol.hasVectorParameter():
            return 'std::vector< ' + self.nestml2NESTTypeConverter.convert(_variableSymbol.getType()) + ' > '
        else:
            return self.nestml2NESTTypeConverter.convert(_variableSymbol.getType())

    def printSizeParameter(self, _astDeclaration=None):
        """
        Prints the size parameter of a single ast declaration.
        :param _astDeclaration: a single ast declaration.
        :type _astDeclaration: ASTDeclaration
        :return: a string representation of the size parameter.
        :rtype: str
        """
        return _astDeclaration.getSizeParameter()

    def getDomainFromType(self, _typeSymbol=None):
        """
        Returns the domain for the handed over type symbol
        :param _typeSymbol: a single type symbol
        :type _typeSymbol: TypeSymbol
        :return: the corresponding domain
        :rtype: str
        """
        return self.nestml2NESTTypeConverter.convert(_typeSymbol)
