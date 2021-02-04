# -*- coding: utf-8 -*-
#
# ast_symbol_table_visitor.py
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
from pynestml.cocos.co_cos_manager import CoCosManager
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.symbol_table.scope import Scope, ScopeType
from pynestml.symbols.function_symbol import FunctionSymbol
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import VariableSymbol, BlockType, VariableType
from pynestml.utils.either import Either
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.stack import Stack
from pynestml.visitors.ast_data_type_visitor import ASTDataTypeVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTSymbolTableVisitor(ASTVisitor):
    """
    This class is used to create a symbol table from a handed over AST.
    """

    def __init__(self):
        super(ASTSymbolTableVisitor, self).__init__()
        self.symbol_stack = Stack()
        self.scope_stack = Stack()
        self.block_type_stack = Stack()
        self.after_ast_rewrite_ = False

    def visit_neuron(self, node):
        """
        Private method: Used to visit a single neuron and create the corresponding global as well as local scopes.
        :return: a single neuron.
        :rtype: ast_neuron
        """
        # set current processed neuron
        Logger.set_current_node(node)
        code, message = Messages.get_start_building_symbol_table()
        Logger.log_message(node=node, code=code, error_position=node.get_source_position(),
                           message=message, log_level=LoggingLevel.INFO)
        scope = Scope(scope_type=ScopeType.GLOBAL, source_position=node.get_source_position())
        node.update_scope(scope)
        node.get_body().update_scope(scope)
        # now first, we add all predefined elements to the scope
        variables = PredefinedVariables.get_variables()
        functions = PredefinedFunctions.get_function_symbols()
        types = PredefinedTypes.get_types()
        for symbol in variables.keys():
            node.get_scope().add_symbol(variables[symbol])
        for symbol in functions.keys():
            node.get_scope().add_symbol(functions[symbol])
        for symbol in types.keys():
            node.get_scope().add_symbol(types[symbol])

    def endvisit_neuron(self, node):
        # before following checks occur, we need to ensure several simple properties
        CoCosManager.post_symbol_table_builder_checks(node, after_ast_rewrite=self.after_ast_rewrite_)
        # the following part is done in order to mark conductance based buffers as such.
        if node.get_input_blocks() is not None and node.get_equations_blocks() is not None and \
                len(node.get_equations_blocks().get_declarations()) > 0:
            # this case should be prevented, since several input blocks result in  a incorrect model
            if isinstance(node.get_input_blocks(), list):
                buffers = (buffer for bufferA in node.get_input_blocks() for buffer in bufferA.get_input_ports())
            else:
                buffers = (buffer for buffer in node.get_input_blocks().get_input_ports())
            from pynestml.meta_model.ast_kernel import ASTKernel
            # todo: ode declarations are not used, is this correct?
            # ode_declarations = (decl for decl in node.get_equations_blocks().get_declarations() if
            #                    not isinstance(decl, ASTKernel))
        # now update the equations
        if node.get_equations_blocks() is not None and len(node.get_equations_blocks().get_declarations()) > 0:
            equation_block = node.get_equations_blocks()
            assign_ode_to_variables(equation_block)
        if not self.after_ast_rewrite_:
            CoCosManager.post_ode_specification_checks(node)
        Logger.set_current_node(None)
        return

    def visit_body(self, node):
        """
        Private method: Used to visit a single neuron body and create the corresponding scope.
        :param node: a single body element.
        :type node: ast_body
        """
        for bodyElement in node.get_body_elements():
            bodyElement.update_scope(node.get_scope())
        return

    def visit_function(self, node):
        """
        Private method: Used to visit a single function block and create the corresponding scope.
        :param node: a function block object.
        :type node: ast_function
        """
        self.block_type_stack.push(BlockType.LOCAL)  # before entering, update the current node type
        symbol = FunctionSymbol(scope=node.get_scope(), element_reference=node, param_types=list(),
                                name=node.get_name(), is_predefined=False, return_type=None)
        # put it on the stack for the endvisit method
        self.symbol_stack.push(symbol)
        symbol.set_comment(node.get_comment())
        node.get_scope().add_symbol(symbol)
        scope = Scope(scope_type=ScopeType.FUNCTION, enclosing_scope=node.get_scope(),
                      source_position=node.get_source_position())
        node.get_scope().add_scope(scope)
        # put it on the stack for the endvisit method
        self.scope_stack.push(scope)
        for arg in node.get_parameters():
            # first visit the data type to ensure that variable symbol can receive a combined data type
            arg.get_data_type().update_scope(scope)
        if node.has_return_type():
            node.get_return_type().update_scope(scope)

        if node.get_block() is not None:
            node.get_block().update_scope(scope)

    def endvisit_function(self, node):
        symbol = self.symbol_stack.pop()
        scope = self.scope_stack.pop()
        assert isinstance(symbol, FunctionSymbol), 'Not a function symbol'
        for arg in node.get_parameters():
            # given the fact that the name is not directly equivalent to the one as stated in the model,
            # we have to get it by the sub-visitor
            data_type_visitor = ASTDataTypeVisitor()
            arg.get_data_type().accept(data_type_visitor)
            type_name = data_type_visitor.result
            # first collect the types for the parameters of the function symbol
            symbol.add_parameter_type(PredefinedTypes.get_type(type_name))
            # update the scope of the arg
            arg.update_scope(scope)
            # create the corresponding variable symbol representing the parameter
            var_symbol = VariableSymbol(element_reference=arg, scope=scope, name=arg.get_name(),
                                        block_type=BlockType.LOCAL, is_predefined=False, is_function=False,
                                        is_recordable=False,
                                        type_symbol=PredefinedTypes.get_type(type_name),
                                        variable_type=VariableType.VARIABLE)
            assert isinstance(scope, Scope)
            scope.add_symbol(var_symbol)
        if node.has_return_type():
            data_type_visitor = ASTDataTypeVisitor()
            node.get_return_type().accept(data_type_visitor)
            symbol.set_return_type(PredefinedTypes.get_type(data_type_visitor.result))
        else:
            symbol.set_return_type(PredefinedTypes.get_void_type())
        self.block_type_stack.pop()  # before leaving update the type
        node.get_scope().delete_scope(scope)    # delete function-local scope

    def visit_update_block(self, node):
        """
        Private method: Used to visit a single update block and create the corresponding scope.
        :param node: an update block object.
        :type node: ASTDynamics
        """
        self.block_type_stack.push(BlockType.LOCAL)
        scope = Scope(scope_type=ScopeType.UPDATE, enclosing_scope=node.get_scope(),
                      source_position=node.get_source_position())
        node.get_scope().add_scope(scope)
        node.get_block().update_scope(scope)
        return

    def endvisit_update_block(self, node=None):
        self.block_type_stack.pop()
        return

    def visit_block(self, node):
        """
        Private method: Used to visit a single block of statements, create and update the corresponding scope.
        :param node: a block object.
        :type node: ast_block
        """
        for stmt in node.get_stmts():
            stmt.update_scope(node.get_scope())
        return

    def visit_small_stmt(self, node):
        """
        Private method: Used to visit a single small statement and create the corresponding sub-scope.
        :param node: a single small statement.
        :type node: ASTSmallStatement
        """
        if node.is_declaration():
            node.get_declaration().update_scope(node.get_scope())
        elif node.is_assignment():
            node.get_assignment().update_scope(node.get_scope())
        elif node.is_function_call():
            node.get_function_call().update_scope(node.get_scope())
        elif node.is_return_stmt():
            node.get_return_stmt().update_scope(node.get_scope())
        return

    def visit_compound_stmt(self, node):
        """
        Private method: Used to visit a single compound statement and create the corresponding sub-scope.
        :param node: a single compound statement.
        :type node: ASTCompoundStatement
        """
        if node.is_if_stmt():
            node.get_if_stmt().update_scope(node.get_scope())
        elif node.is_while_stmt():
            node.get_while_stmt().update_scope(node.get_scope())
        else:
            node.get_for_stmt().update_scope(node.get_scope())
        return

    def visit_assignment(self, node):
        """
        Private method: Used to visit a single node and update its corresponding scope.
        :param node: an node object.
        :type node: ast_assignment
        :return: no return value, since neither scope nor symbol is created
        :rtype: void
        """
        node.get_variable().update_scope(node.get_scope())
        node.get_expression().update_scope(node.get_scope())
        return

    def visit_function_call(self, node):
        """
        Private method: Used to visit a single function call and update its corresponding scope.
        :param node: a function call object.
        :type node: ast_function_call
        :return: no return value, since neither scope nor symbol is created
        :rtype: void
        """
        for arg in node.get_args():
            arg.update_scope(node.get_scope())
        return

    def visit_declaration(self, node):
        """
        Private method: Used to visit a single declaration, update its scope and return the corresponding set of
        symbols
        :param node: a declaration object.
        :type node: ast_declaration
        :return: the scope is update without a return value.
        :rtype: void
        """
        expression = node.get_expression() if node.has_expression() else None
        visitor = ASTDataTypeVisitor()
        node.get_data_type().accept(visitor)
        type_name = visitor.result
        # all declarations in the state block are recordable
        is_recordable = (node.is_recordable
                         or self.block_type_stack.top() == BlockType.STATE
                         or self.block_type_stack.top() == BlockType.INITIAL_VALUES)
        init_value = node.get_expression() if self.block_type_stack.top() == BlockType.INITIAL_VALUES else None
        vector_parameter = node.get_size_parameter()
        # now for each variable create a symbol and update the scope
        for var in node.get_variables():  # for all variables declared create a new symbol
            var.update_scope(node.get_scope())
            type_symbol = PredefinedTypes.get_type(type_name)
            symbol = VariableSymbol(element_reference=node,
                                    scope=node.get_scope(),
                                    name=var.get_complete_name(),
                                    block_type=self.block_type_stack.top(),
                                    declaring_expression=expression, is_predefined=False,
                                    is_function=node.is_function,
                                    is_recordable=is_recordable,
                                    type_symbol=type_symbol,
                                    initial_value=init_value,
                                    vector_parameter=vector_parameter,
                                    variable_type=VariableType.VARIABLE
                                    )
            symbol.set_comment(node.get_comment())
            node.get_scope().add_symbol(symbol)
            var.set_type_symbol(Either.value(type_symbol))
        # the data type
        node.get_data_type().update_scope(node.get_scope())
        # the rhs update
        if node.has_expression():
            node.get_expression().update_scope(node.get_scope())
        # the invariant update
        if node.has_invariant():
            node.get_invariant().update_scope(node.get_scope())
        return

    def visit_return_stmt(self, node):
        """
        Private method: Used to visit a single return statement and update its scope.
        :param node: a return statement object.
        :type node: ast_return_stmt
        """
        if node.has_expression():
            node.get_expression().update_scope(node.get_scope())
        return

    def visit_if_stmt(self, node):
        """
        Private method: Used to visit a single if-statement, update its scope and create the corresponding sub-scope.
        :param node: an if-statement object.
        :type node: ast_if_stmt
        """
        node.get_if_clause().update_scope(node.get_scope())
        for elIf in node.get_elif_clauses():
            elIf.update_scope(node.get_scope())
        if node.has_else_clause():
            node.get_else_clause().update_scope(node.get_scope())
        return

    def visit_if_clause(self, node):
        """
        Private method: Used to visit a single if-clause, update its scope and create the corresponding sub-scope.
        :param node: an if clause.
        :type node: ast_if_clause
        """
        node.get_condition().update_scope(node.get_scope())
        node.get_block().update_scope(node.get_scope())

    def visit_elif_clause(self, node):
        """
        Private method: Used to visit a single elif-clause, update its scope and create the corresponding sub-scope.
        :param node: an elif clause.
        :type node: ast_elif_clause
        """
        node.get_condition().update_scope(node.get_scope())
        node.get_block().update_scope(node.get_scope())

    def visit_else_clause(self, node):
        """
        Private method: Used to visit a single else-clause, update its scope and create the corresponding sub-scope.
        :param node: an else clause.
        :type node: ast_else_clause
        """
        node.get_block().update_scope(node.get_scope())

    def visit_for_stmt(self, node):
        """
        Private method: Used to visit a single for-stmt, update its scope and create the corresponding sub-scope.
        :param node: a for-statement.
        :type node: ast_for_stmt
        """
        node.get_start_from().update_scope(node.get_scope())
        node.get_end_at().update_scope(node.get_scope())
        node.get_block().update_scope(node.get_scope())

    def visit_while_stmt(self, node):
        """
        Private method: Used to visit a single while-stmt, update its scope and create the corresponding sub-scope.
        :param node: a while-statement.
        :type node: ast_while_stmt
        """
        node.get_condition().update_scope(node.get_scope())
        node.get_block().update_scope(node.get_scope())

    def visit_data_type(self, node):
        """
        Private method: Used to visit a single data-type and update its scope.
        :param node: a data-type.
        :type node: ast_data_type
        """
        if node.is_unit_type():
            node.get_unit_type().update_scope(node.get_scope())
            return self.visit_unit_type(node.get_unit_type())

    def visit_unit_type(self, node):
        """
        Private method: Used to visit a single unit-type and update its scope.
        :param node: a unit type.
        :type node: ast_unit_type
        """
        from pynestml.meta_model.ast_unit_type import ASTUnitType
        if node.is_pow:
            node.base.update_scope(node.get_scope())
        elif node.is_encapsulated:
            node.compound_unit.update_scope(node.get_scope())
        elif node.is_div or node.is_times:
            if isinstance(node.lhs, ASTUnitType):  # lhs can be a numeric Or a unit-type
                node.lhs.update_scope(node.get_scope())
            node.get_rhs().update_scope(node.get_scope())
        return

    def visit_expression(self, node):
        """
        Private method: Used to visit a single rhs and update its scope.
        :param node: an rhs.
        :type node: ast_expression
        """
        from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
        if isinstance(node, ASTSimpleExpression):
            return self.visit_simple_expression(node)
        if node.is_logical_not:
            node.get_expression().update_scope(node.get_scope())
        elif node.is_encapsulated:
            node.get_expression().update_scope(node.get_scope())
        elif node.is_unary_operator():
            node.get_unary_operator().update_scope(node.get_scope())
            node.get_expression().update_scope(node.get_scope())
        elif node.is_compound_expression():
            node.get_lhs().update_scope(node.get_scope())
            node.get_binary_operator().update_scope(node.get_scope())
            node.get_rhs().update_scope(node.get_scope())
        if node.is_ternary_operator():
            node.get_condition().update_scope(node.get_scope())
            node.get_if_true().update_scope(node.get_scope())
            node.get_if_not().update_scope(node.get_scope())
        return

    def visit_simple_expression(self, node):
        """
        Private method: Used to visit a single simple rhs and update its scope.
        :param node: a simple rhs.
        :type node: ast_simple_expression
        """
        if node.is_function_call():
            node.get_function_call().update_scope(node.get_scope())
        elif node.is_variable() or node.has_unit():
            node.get_variable().update_scope(node.get_scope())
        return

    def visit_inline_expression(self, node):
        """
        Private method: Used to visit a single ode-function, create the corresponding symbol and update the scope.
        :param node: a single inline expression.
        :type node: ASTInlineExpression
        """
        data_type_visitor = ASTDataTypeVisitor()
        node.get_data_type().accept(data_type_visitor)
        type_symbol = PredefinedTypes.get_type(data_type_visitor.result)
        # now a new symbol
        symbol = VariableSymbol(element_reference=node, scope=node.get_scope(),
                                name=node.get_variable_name(),
                                block_type=BlockType.EQUATION,
                                declaring_expression=node.get_expression(),
                                is_predefined=False, is_function=True,
                                is_recordable=node.is_recordable,
                                type_symbol=type_symbol,
                                variable_type=VariableType.VARIABLE)
        symbol.set_comment(node.get_comment())
        # now update the scopes
        node.get_scope().add_symbol(symbol)
        node.get_data_type().update_scope(node.get_scope())
        node.get_expression().update_scope(node.get_scope())

    def visit_kernel(self, node):
        """
        Private method: Used to visit a single kernel, create the corresponding symbol and update the scope.
        :param node: a kernel.
        :type node: ASTKernel
        """
        for var, expr in zip(node.get_variables(), node.get_expressions()):
            if var.get_differential_order() == 0 and \
                    node.get_scope().resolve_to_symbol(var.get_complete_name(), SymbolKind.VARIABLE) is None:
                symbol = VariableSymbol(element_reference=node, scope=node.get_scope(),
                                        name=var.get_name(),
                                        block_type=BlockType.EQUATION,
                                        declaring_expression=expr,
                                        is_predefined=False,
                                        is_function=False,
                                        is_recordable=True,
                                        type_symbol=PredefinedTypes.get_real_type(),
                                        variable_type=VariableType.KERNEL)
                symbol.set_comment(node.get_comment())
                node.get_scope().add_symbol(symbol)
            var.update_scope(node.get_scope())
            expr.update_scope(node.get_scope())

    def visit_ode_equation(self, node):
        """
        Private method: Used to visit a single ode-equation and update the corresponding scope.
        :param node: a single ode-equation.
        :type node: ast_ode_equation
        """
        node.get_lhs().update_scope(node.get_scope())
        node.get_rhs().update_scope(node.get_scope())

    def visit_block_with_variables(self, node):
        """
        Private method: Used to visit a single block of variables and update its scope.
        :param node: a block with declared variables.
        :type node: ast_block_with_variables
        """
        self.block_type_stack.push(
            BlockType.STATE if node.is_state else
            BlockType.INTERNALS if node.is_internals else
            BlockType.PARAMETERS if node.is_parameters else
            BlockType.INITIAL_VALUES)
        for decl in node.get_declarations():
            decl.update_scope(node.get_scope())
        return

    def endvisit_block_with_variables(self, node):
        self.block_type_stack.pop()
        return

    def visit_equations_block(self, node):
        """
        Private method: Used to visit a single equations block and update its scope.
        :param node: a single equations block.
        :type node: ast_equations_block
        """
        for decl in node.get_declarations():
            decl.update_scope(node.get_scope())

    def visit_input_block(self, node):
        """
        Private method: Used to visit a single input block and update its scope.
        :param node: a single input block.
        :type node: ast_input_block
        """
        for port in node.get_input_ports():
            port.update_scope(node.get_scope())

    def visit_input_port(self, node):
        """
        Private method: Used to visit a single input port, create the corresponding symbol and update the scope.
        :param node: a single input port.
        :type node: ASTInputPort
        """
        if not node.has_datatype():
            code, message = Messages.get_buffer_type_not_defined(node.get_name())
            Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                               log_level=LoggingLevel.ERROR)
        else:
            node.get_datatype().update_scope(node.get_scope())

        for qual in node.get_input_qualifiers():
            qual.update_scope(node.get_scope())

    def endvisit_input_port(self, node):
        buffer_type = BlockType.INPUT_BUFFER_SPIKE if node.is_spike() else BlockType.INPUT_BUFFER_CURRENT
        if not node.has_datatype():
            return
        type_symbol = node.get_datatype().get_type_symbol()
        type_symbol.is_buffer = True  # set it as a buffer
        symbol = VariableSymbol(element_reference=node, scope=node.get_scope(), name=node.get_name(),
                                block_type=buffer_type, vector_parameter=node.get_index_parameter(),
                                is_predefined=False, is_function=False, is_recordable=False,
                                type_symbol=type_symbol, variable_type=VariableType.BUFFER)
        symbol.set_comment(node.get_comment())
        node.get_scope().add_symbol(symbol)

    def visit_stmt(self, node):
        """
        Private method: Used to visit a single stmt and update its scope.
        :param node: a single statement
        :type node: ast_stmt
        """
        if node.is_small_stmt():
            node.small_stmt.update_scope(node.get_scope())
        if node.is_compound_stmt():
            node.compound_stmt.update_scope(node.get_scope())


def assign_ode_to_variables(ode_block):
    """
    Adds for each variable symbol the corresponding ode declaration if present.
    :param ode_block: a single block of ode declarations.
    :type ode_block: ASTEquations
    """
    from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
    from pynestml.meta_model.ast_kernel import ASTKernel
    for decl in ode_block.get_declarations():
        if isinstance(decl, ASTOdeEquation):
            add_ode_to_variable(decl)
        elif isinstance(decl, ASTKernel):
            add_kernel_to_variable(decl)


def add_ode_to_variable(ode_equation):
    """
    Resolves to the corresponding symbol and updates the corresponding ode-declaration.
    :param ode_equation: a single ode-equation
    :type ode_equation: ast_ode_equation
    """
    for diff_order in range(ode_equation.get_lhs().get_differential_order()):
        var_name = ode_equation.get_lhs().get_name() + "'" * diff_order
        existing_symbol = ode_equation.get_scope().resolve_to_symbol(var_name, SymbolKind.VARIABLE)

        if existing_symbol is None:
            code, message = Messages.get_no_variable_found(ode_equation.get_lhs().get_name_of_lhs())
            Logger.log_message(code=code, message=message, error_position=ode_equation.get_source_position(),
                               log_level=LoggingLevel.ERROR)
            return

        existing_symbol.set_ode_or_kernel(ode_equation)

        ode_equation.get_scope().update_variable_symbol(existing_symbol)
        code, message = Messages.get_ode_updated(ode_equation.get_lhs().get_name_of_lhs())
        Logger.log_message(error_position=existing_symbol.get_referenced_object().get_source_position(),
                           code=code, message=message, log_level=LoggingLevel.INFO)


def add_kernel_to_variable(kernel):
    """
    Adds the kernel as the defining equation.

    If the definition of the kernel is e.g. `g'' = ...` then variable symbols `g` and `g'` will have their kernel definition and variable type set.

    :param kernel: a single kernel object.
    :type kernel: ASTKernel
    """
    if len(kernel.get_variables()) == 1 \
            and kernel.get_variables()[0].get_differential_order() == 0:
        # we only update those which define an ODE; skip "direct function of time" specifications
        return

    for var, expr in zip(kernel.get_variables(), kernel.get_expressions()):
        for diff_order in range(var.get_differential_order()):
            var_name = var.get_name() + "'" * diff_order
            existing_symbol = kernel.get_scope().resolve_to_symbol(var_name, SymbolKind.VARIABLE)

            if existing_symbol is None:
                code, message = Messages.get_no_variable_found(var.get_name_of_lhs())
                Logger.log_message(code=code, message=message, error_position=kernel.get_source_position(), log_level=LoggingLevel.ERROR)
                return

            existing_symbol.set_ode_or_kernel(expr)
            existing_symbol.set_variable_type(VariableType.KERNEL)
            kernel.get_scope().update_variable_symbol(existing_symbol)
