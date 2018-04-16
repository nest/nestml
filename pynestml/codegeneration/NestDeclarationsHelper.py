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
from pynestml.meta_model.ASTDeclaration import ASTDeclaration
from pynestml.codegeneration.PyNestMl2NESTTypeConverter import NESTML2NESTTypeConverter
from pynestml.symbols.Symbol import SymbolKind
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.Messages import Messages


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

    def get_variables(self, ast_declaration=None):
        """
        For a given meta_model declaration it returns a list of all corresponding variable symbols.
        :param ast_declaration: a single meta_model declaration.
        :type ast_declaration: ASTDeclaration
        :return: a list of all corresponding variable symbols.
        :rtype: list(VariableSymbol)
        """

        assert (ast_declaration is not None and isinstance(ast_declaration, ASTDeclaration)), \
            '(PyNestML.CodeGeneration.DeclarationsHelper) No or wrong type of declaration provided (%s)!' % type(
                ast_declaration)
        ret = list()
        for var in ast_declaration.get_variables():
            symbol = ast_declaration.get_scope().resolve_to_symbol(var.get_complete_name(), SymbolKind.VARIABLE)
            if symbol is not None:
                ret.append(symbol)
            else:
                code, message = Messages.get_could_not_resolve(var.get_complete_name())
                Logger.log_message(code=code, message=message,
                                   error_position=ast_declaration.get_source_position(), log_level=LoggingLevel.ERROR)
            return ret

    def printVariableType(self, _variableSymbol=None):
        """
        Prints the type of the variable symbol to a corresponding nest representation.
        :param _variableSymbol: a single variable symbol
        :type _variableSymbol: VariableSymbol
        :return: a string presentation of the variable symbol's type
        :rtype: str
        """
        if _variableSymbol.has_vector_parameter():
            return 'std::vector< ' + self.nestml2NESTTypeConverter.convert(_variableSymbol.get_type_symbol()) + ' > '
        else:
            return self.nestml2NESTTypeConverter.convert(_variableSymbol.get_type_symbol())

    def printSizeParameter(self, _astDeclaration=None):
        """
        Prints the size parameter of a single meta_model declaration.
        :param _astDeclaration: a single meta_model declaration.
        :type _astDeclaration: ASTDeclaration
        :return: a string representation of the size parameter.
        :rtype: str
        """
        return _astDeclaration.get_size_parameter()

    def getDomainFromType(self, _typeSymbol=None):
        """
        Returns the domain for the handed over type symbol
        :param _typeSymbol: a single type symbol
        :type _typeSymbol: TypeSymbol
        :return: the corresponding domain
        :rtype: str
        """
        return self.nestml2NESTTypeConverter.convert(_typeSymbol)
