# -*- coding: utf-8 -*-
#
# nest_declarations_helper.py
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

from pynestml.codegeneration.nest_code_generator_utils import NESTCodeGeneratorUtils
from pynestml.codegeneration.printers.type_symbol_printer import TypeSymbolPrinter
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.messages import Messages


class NestDeclarationsHelper:
    r"""
    This class contains several methods as used during generation of code.
    """

    def __init__(self, type_symbol_printer: TypeSymbolPrinter):
        """
        Initialized the declaration helper.
        """
        self.type_symbol_printer = type_symbol_printer

    def get_domain_from_type(self, type_symbol):
        """
        Returns the domain for the handed over type symbol
        :param type_symbol: a single type symbol
        :type type_symbol: type_symbol
        :return: the corresponding domain
        :rtype: str
        """
        return self.type_symbol_printer.print(type_symbol)

    def print_variable_type(self, variable_symbol) -> str:
        """
        Prints the type of the variable symbol to a corresponding nest representation.
        :param variable_symbol: a single variable symbol
        :type variable_symbol: variable_symbol
        :return: a string presentation of the variable symbol's type
        :rtype: str
        """
        if variable_symbol.has_vector_parameter():
            return 'std::vector< ' + self.type_symbol_printer.print(variable_symbol.get_type_symbol()) + \
                   ' > '

        return self.type_symbol_printer.print(variable_symbol.get_type_symbol())

    @classmethod
    def get_variables(cls, ast_declaration):
        """
        For a given meta_model declaration it returns a list of all corresponding variable symbols.
        :param ast_declaration: a single meta_model declaration.
        :type ast_declaration: ASTDeclaration
        :return: a list of all corresponding variable symbols.
        :rtype: list(VariableSymbol)
        """

        assert isinstance(ast_declaration, ASTDeclaration), \
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

    @classmethod
    def print_size_parameter(cls, ast_declaration) -> str:
        """
        Prints the size parameter of a single meta_model declaration.
        :param ast_declaration: a single meta_model declaration.
        :type ast_declaration: ASTDeclaration
        :return: a string representation of the size parameter.
        :rtype: str
        """
        return ast_declaration.get_size_parameter()

    @classmethod
    def print_delay_parameter(cls, variable: VariableSymbol) -> str:
        """
        Prints the delay parameter
        :param variable: Variable with delay parameter
        :return: the corresponding delay parameter
        """
        assert isinstance(variable, VariableSymbol), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of variable symbol provided (%s)!' % type(variable)
        delay_parameter = variable.get_delay_parameter()
        delay_parameter_var = ASTVariable(delay_parameter, scope=variable.get_corresponding_scope())
        symbol = delay_parameter_var.get_scope().resolve_to_symbol(delay_parameter_var.get_complete_name(),
                                                                   SymbolKind.VARIABLE)
        if symbol is not None:
            # delay parameter is a variable
            return NESTCodeGeneratorUtils.print_symbol_origin(symbol, delay_parameter_var) % delay_parameter

        return delay_parameter
