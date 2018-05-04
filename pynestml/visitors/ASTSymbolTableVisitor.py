#
# ASTSymbolTableVisitor.py
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
from pynestml.meta_model.ASTNodeFactory import ASTNodeFactory
from pynestml.meta_model.ASTSourceLocation import ASTSourceLocation
from pynestml.cocos.CoCosManager import CoCosManager
from pynestml.symbol_table.Scope import Scope, ScopeType
from pynestml.symbols.FunctionSymbol import FunctionSymbol
from pynestml.symbols.PredefinedFunctions import PredefinedFunctions
from pynestml.symbols.PredefinedTypes import PredefinedTypes
from pynestml.symbols.PredefinedVariables import PredefinedVariables
from pynestml.symbols.Symbol import SymbolKind
from pynestml.symbols.VariableSymbol import VariableSymbol, BlockType, VariableType
from pynestml.utils.Either import Either
from pynestml.utils.Logger import Logger, LoggingLevel
from pynestml.utils.Messages import Messages
from pynestml.utils.Stack import Stack
from pynestml.visitors.ASTDataTypeVisitor import ASTDataTypeVisitor
from pynestml.visitors.ASTVisitor import ASTVisitor


class ASTSymbolTableVisitor(ASTVisitor):
    """
    This class is used to create a symbol table from a handed over AST.
    """

    def __init__(self):
        super(ASTSymbolTableVisitor, self).__init__()
        self.symbol_stack = Stack()
        self.scope_stack = Stack()
        self.block_type_stack = Stack()

    def visit_neuron(self, node):
        """
        Private method: Used to visit a single neuron and create the corresponding global as well as local scopes.
        :return: a single neuron.
        :rtype: ASTNeuron
        """
        # set current processed neuron
        Logger.set_current_neuron(node)
        code, message = Messages.get_start_building_symbol_table()
        Logger.log_message(neuron=node, code=code, error_position=node.get_source_position(),
                           message=message, log_level=LoggingLevel.INFO)
        # before starting the work on the neuron, make everything which was implicit explicit
        # but if we have a model without an equations block, just skip this step
        if node.get_equations_blocks() is not None:
            make_implicit_odes_explicit(node.get_equations_blocks())
        scope = Scope(scope_type=ScopeType.GLOBAL, source_position=node.get_source_position())
        node.update_scope(scope)
        node.get_body().update_scope(scope)
        # now first, we add all predefined elements to the scope
        variables = PredefinedVariables.get_variables()
        functions = PredefinedFunctions.get_function_symbols()
        for symbol in variables.keys():
            node.get_scope().add_symbol(variables[symbol])
        for symbol in functions.keys():
            node.get_scope().add_symbol(functions[symbol])
        return

    def endvisit_neuron(self, node):
        # before following checks occur, we need to ensure several simple properties
        CoCosManager.post_symbol_table_builder_checks(node)
        # the following part is done in order to mark conductance based buffers as such.
        if node.get_input_blocks() is not None and node.get_equations_blocks() is not None and \
                len(node.get_equations_blocks().get_declarations()) > 0:
            # this case should be prevented, since several input blocks result in  a incorrect model
            if isinstance(node.get_input_blocks(), list):
                buffers = (buffer for bufferA in node.get_input_blocks() for buffer in bufferA.getInputLines())
            else:
                buffers = (buffer for buffer in node.get_input_blocks().getInputLines())
            from pynestml.meta_model.ASTOdeShape import ASTOdeShape
            # todo by KP: ode declarations are not used, is this correct?
            # ode_declarations = (decl for decl in node.get_equations_blocks().get_declarations() if
            #                    not isinstance(decl, ASTOdeShape))
            mark_conductance_based_buffers(input_lines=buffers)
        # now update the equations
        if node.get_equations_blocks() is not None and len(node.get_equations_blocks().get_declarations()) > 0:
            equation_block = node.get_equations_blocks()
            assign_ode_to_variables(equation_block)
        CoCosManager.post_ode_specification_checks(node)
        Logger.set_current_neuron(None)
        return

    def visit_body(self, node):
        """
        Private method: Used to visit a single neuron body and create the corresponding scope.
        :param node: a single body element.
        :type node: ASTBody
        """
        for bodyElement in node.get_body_elements():
            bodyElement.update_scope(node.get_scope())
        return

    def visit_function(self, node):
        """
        Private method: Used to visit a single function block and create the corresponding scope.
        :param node: a function block object.
        :type node: ASTFunction
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
        node.get_block().update_scope(scope)
        return

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
        :type node: ASTBlock
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
        Private method: Used to visit a single node and update the its corresponding scope.
        :param node: an node object.
        :type node: ASTAssignment
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
        :type node: ASTFunctionCall
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
        :type node: ASTDeclaration
        :return: the scope is update without a return value.
        :rtype: void
        """
        expression = node.get_expression() if node.has_expression() else None
        visitor = ASTDataTypeVisitor()
        node.get_data_type().accept(visitor)
        type_name = visitor.result
        # all declarations in the state block are recordable
        is_recordable = (node.is_recordable() or
                         self.block_type_stack.top() == BlockType.STATE or
                         self.block_type_stack.top() == BlockType.INITIAL_VALUES)
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
        :type node: ASTReturnStmt
        """
        if node.has_expression():
            node.get_expression().update_scope(node.get_scope())
        return

    def visit_if_stmt(self, node):
        """
        Private method: Used to visit a single if-statement, update its scope and create the corresponding sub-scope.
        :param node: an if-statement object.
        :type node: ASTIfStmt
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
        :type node: ASTIfClause
        """
        node.get_condition().update_scope(node.get_scope())
        node.get_block().update_scope(node.get_scope())

    def visit_elif_clause(self, node):
        """
        Private method: Used to visit a single elif-clause, update its scope and create the corresponding sub-scope.
        :param node: an elif clause.
        :type node: ASTElifClause
        """
        node.get_condition().update_scope(node.get_scope())
        node.get_block().update_scope(node.get_scope())

    def visit_else_clause(self, node):
        """
        Private method: Used to visit a single else-clause, update its scope and create the corresponding sub-scope.
        :param node: an else clause.
        :type node: ASTElseClause
        """
        node.get_block().update_scope(node.get_scope())

    def visit_for_stmt(self, node):
        """
        Private method: Used to visit a single for-stmt, update its scope and create the corresponding sub-scope.
        :param node: a for-statement.
        :type node: ASTForStmt
        """
        node.get_start_from().update_scope(node.get_scope())
        node.get_end_at().update_scope(node.get_scope())
        node.get_block().update_scope(node.get_scope())

    def visit_while_stmt(self, node):
        """
        Private method: Used to visit a single while-stmt, update its scope and create the corresponding sub-scope.
        :param node: a while-statement.
        :type node: ASTWhileStmt
        """
        node.get_condition().update_scope(node.get_scope())
        node.get_block().update_scope(node.get_scope())

    def visit_data_type(self, node):
        """
        Private method: Used to visit a single data-type and update its scope.
        :param node: a data-type.
        :type node: ASTDataType
        """
        if node.is_unit_type():
            node.get_unit_type().update_scope(node.get_scope())
            return self.visit_unit_type(node.get_unit_type())

    def visit_unit_type(self, node):
        """
        Private method: Used to visit a single unit-type and update its scope.
        :param node: a unit type.
        :type node: ASTUnitType
        """
        from pynestml.meta_model.ASTUnitType import ASTUnitType
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
        :type node: ASTExpression
        """
        from pynestml.meta_model.ASTSimpleExpression import ASTSimpleExpression
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
        :type node: ASTSimpleExpression
        """
        if node.is_function_call():
            node.get_function_call().update_scope(node.get_scope())
        elif node.is_variable() or node.has_unit():
            node.get_variable().update_scope(node.get_scope())
        return

    def visit_ode_function(self, node):
        """
        Private method: Used to visit a single ode-function, create the corresponding symbol and update the scope.
        :param node: a single ode-function.
        :type node: ASTOdeFunction
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
                                is_recordable=node.isRecordable(),
                                type_symbol=type_symbol,
                                variable_type=VariableType.VARIABLE)
        symbol.set_comment(node.get_comment())
        # now update the scopes
        node.get_scope().add_symbol(symbol)
        node.get_data_type().update_scope(node.get_scope())
        node.get_expression().update_scope(node.get_scope())

    def visit_ode_shape(self, node):
        """
        Private method: Used to visit a single ode-shape, create the corresponding symbol and update the scope.
        :param node: a single ode-shape.
        :type node: ASTOdeShape
        """
        if node.get_variable().get_differential_order() == 0 and \
                node.get_scope().resolve_to_symbol(node.get_variable().get_complete_name(),
                                                   SymbolKind.VARIABLE) is None:
            symbol = VariableSymbol(element_reference=node, scope=node.get_scope(),
                                    name=node.get_variable().get_name(),
                                    block_type=BlockType.EQUATION,
                                    declaring_expression=node.get_expression(),
                                    is_predefined=False, is_function=False,
                                    is_recordable=True,
                                    type_symbol=PredefinedTypes.get_real_type(), variable_type=VariableType.SHAPE)
            symbol.set_comment(node.get_comment())
            node.get_scope().add_symbol(symbol)
        node.get_variable().update_scope(node.get_scope())
        node.get_expression().update_scope(node.get_scope())

    def visit_ode_equation(self, node):
        """
        Private method: Used to visit a single ode-equation and update the corresponding scope.
        :param node: a single ode-equation.
        :type node: ASTOdeEquation
        """
        node.get_lhs().update_scope(node.get_scope())
        node.get_rhs().update_scope(node.get_scope())

    def visit_block_with_variables(self, node):
        """
        Private method: Used to visit a single block of variables and update its scope.
        :param node: a block with declared variables.
        :type node: ASTBlockWithVariables
        """
        self.block_type_stack.push(
            BlockType.STATE if node.is_state() else
            BlockType.INTERNALS if node.is_internals() else
            BlockType.PARAMETERS if node.is_parameters() else
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
        :type node: ASTEquationsBlock
        """
        for decl in node.get_declarations():
            decl.update_scope(node.get_scope())

    def visit_input_block(self, node):
        """
        Private method: Used to visit a single input block and update its scope.
        :param node: a single input block.
        :type node: ASTInputBlock
        """
        for line in node.getInputLines():
            line.update_scope(node.get_scope())

    def visit_input_line(self, node):
        """
        Private method: Used to visit a single input line, create the corresponding symbol and update the scope.
        :param node: a single input line.
        :type node: ASTInputLine
        """
        if node.is_spike() and node.has_datatype():
            node.get_datatype().update_scope(node.get_scope())
        elif node.is_spike():
            code, message = Messages.get_buffer_type_not_defined(node.get_name())
            Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                               log_level=LoggingLevel.WARNING)
        for inputType in node.get_input_types():
            inputType.update_scope(node.get_scope())

    def endvisit_input_line(self, node):
        buffer_type = BlockType.INPUT_BUFFER_SPIKE if node.is_spike() else BlockType.INPUT_BUFFER_CURRENT
        if node.is_spike() and node.has_datatype():
            type_symbol = node.get_datatype().get_type_symbol()
        elif node.is_spike():
            code, message = Messages.get_buffer_type_not_defined(node.get_name())
            Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                               log_level=LoggingLevel.WARNING)
            type_symbol = PredefinedTypes.get_type('nS')
        else:
            type_symbol = PredefinedTypes.get_type('pA')
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
        :type node: ASTStmt
        """
        if node.is_small_stmt():
            node.small_stmt.update_scope(node.get_scope())
        if node.is_compound_stmt():
            node.compound_stmt.update_scope(node.get_scope())


def make_implicit_odes_explicit(equations_block):
    """
    This method inspects a handed over block of equations and makes all implicit declarations of odes explicit.
    E.g. the declaration g_in'' implies that there have to be, either implicit or explicit, g_in' and g_in
    stated somewhere. This method collects all non explicitly defined elements and adds them to the model.
    :param equations_block: a single equations block
    :type equations_block: ASTEquationsBlock
    """
    from pynestml.meta_model.ASTOdeShape import ASTOdeShape
    from pynestml.meta_model.ASTOdeEquation import ASTOdeEquation
    checked = list()  # used to avoid redundant checking
    for declaration in equations_block.get_declarations():
        if declaration in checked:
            continue
        if isinstance(declaration, ASTOdeShape) and declaration.get_variable().get_differential_order() > 0:
            # now we found a variable with order > 0, thus check if all previous orders have been defined
            order = declaration.get_variable().get_differential_order()
            # check for each smaller order if it is defined
            for i in range(1, order):
                found = False
                for shape in equations_block.get_ode_shapes():
                    if shape.get_variable().get_name() == declaration.get_variable().get_name() and \
                            shape.get_variable().get_differential_order() == i:
                        found = True
                        break
                # now if we did not found the corresponding declaration, we have to add it by hand
                if not found:
                    lhs_variable = ASTNodeFactory.create_ast_variable(name=declaration.get_variable().get_name(),
                                                                      differential_order=i,
                                                                      source_position=ASTSourceLocation.
                                                                      get_added_source_position())
                    rhs_variable = ASTNodeFactory.create_ast_variable(name=declaration.get_variable().get_name(),
                                                                      differential_order=i,
                                                                      source_position=ASTSourceLocation.
                                                                      get_added_source_position())
                    expression = ASTNodeFactory.create_ast_simple_expression(variable=rhs_variable,
                                                                             source_position=ASTSourceLocation.
                                                                             get_added_source_position())
                    source_loc = ASTSourceLocation.get_added_source_position()
                    equations_block.get_declarations().append(
                        ASTNodeFactory.create_ast_ode_shape(lhs=lhs_variable,
                                                            rhs=expression,
                                                            source_position=source_loc))
        if isinstance(declaration, ASTOdeEquation):
            # now we found a variable with order > 0, thus check if all previous orders have been defined
            order = declaration.get_lhs().get_differential_order()
            # check for each smaller order if it is defined
            for i in range(1, order):
                found = False
                for ode in equations_block.get_ode_equations():
                    if (ode.get_lhs().get_name() == declaration.get_lhs().get_name() and
                            ode.get_lhs().get_differential_order() == i):
                        found = True
                        break
                # now if we did not found the corresponding declaration, we have to add it by hand
                if not found:
                    lhs_variable = ASTNodeFactory.create_ast_variable(name=declaration.get_lhs().get_name(),
                                                                      differential_order=i,
                                                                      source_position=ASTSourceLocation.
                                                                      get_added_source_position())
                    rhs_variable = ASTNodeFactory.create_ast_variable(name=declaration.get_lhs().get_name(),
                                                                      differential_order=i,
                                                                      source_position=ASTSourceLocation.
                                                                      get_added_source_position())
                    expression = ASTNodeFactory.create_ast_simple_expression(variable=rhs_variable,
                                                                             source_position=ASTSourceLocation.
                                                                             get_added_source_position(),
                                                                             function_call=None,
                                                                             boolean_literal=None,
                                                                             is_inf=False,
                                                                             string=None,
                                                                             numeric_literal=None)

                    ode_eq_pos = ASTSourceLocation.get_added_source_position()
                    ode_eq = ASTNodeFactory.create_ast_ode_equation(lhs=lhs_variable, rhs=expression,
                                                                    source_position=ode_eq_pos)
                    equations_block.get_declarations().append(ode_eq)
        checked.append(declaration)


def mark_conductance_based_buffers(input_lines):
    """
    Inspects all handed over buffer definitions and updates them to conductance based if they occur as part of
    a cond_sum rhs.
    :param input_lines: a set of input buffers.
    :type input_lines: ASTInputLine
    """
    # this is the updated version, where nS buffers are marked as conductance based
    for bufferDeclaration in input_lines:
        if bufferDeclaration.is_spike():
            symbol = bufferDeclaration.get_scope().resolve_to_symbol(bufferDeclaration.get_name(),
                                                                     SymbolKind.VARIABLE)
            if symbol is not None and symbol.get_type_symbol().equals(PredefinedTypes.get_buffer_type_if_exists('nS')):
                symbol.set_conductance_based(True)
    return


def assign_ode_to_variables(ode_block):
    """
    Adds for each variable symbol the corresponding ode declaration if present.
    :param ode_block: a single block of ode declarations.
    :type ode_block: ASTEquations
    """
    from pynestml.meta_model.ASTOdeEquation import ASTOdeEquation
    from pynestml.meta_model.ASTOdeShape import ASTOdeShape
    for decl in ode_block.get_declarations():
        if isinstance(decl, ASTOdeEquation):
            add_ode_to_variable(decl)
        if isinstance(decl, ASTOdeShape):
            add_ode_shape_to_variable(decl)
    return


def add_ode_to_variable(ode_equation):
    """
    Resolves to the corresponding symbol and updates the corresponding ode-declaration. In the case that
    :param ode_equation: a single ode-equation
    :type ode_equation: ASTOdeEquation
    """
    # the definition of a differential equations is defined by stating the derivation, thus derive the actual order
    diff_order = ode_equation.get_lhs().get_differential_order() - 1
    # we check if the corresponding symbol already exists, e.g. V_m' has already been declared
    existing_symbol = (ode_equation.get_scope().resolve_to_symbol(ode_equation.get_lhs().get_name() + '\'' * diff_order,
                                                                  SymbolKind.VARIABLE))
    if existing_symbol is not None:
        existing_symbol.set_ode_definition(ode_equation.get_rhs())
        code, message = Messages.get_ode_updated(ode_equation.get_lhs().get_name_of_lhs())
        Logger.log_message(error_position=existing_symbol.get_referenced_object().get_source_position(),
                           code=code, message=message, log_level=LoggingLevel.INFO)
    else:
        code, message = Messages.get_no_variable_found(ode_equation.get_lhs().get_name_of_lhs())
        Logger.log_message(code=code, message=message, error_position=ode_equation.get_source_position(),
                           log_level=LoggingLevel.ERROR)
    return


def add_ode_shape_to_variable(ode_shape):
    """
    Adds the shape as the defining equation.
    :param ode_shape: a single shape object.
    :type ode_shape: ASTOdeShape
    """
    if ode_shape.get_variable().get_differential_order() == 0:
        # we only update those which define an ode
        return
    # we check if the corresponding symbol already exists, e.g. V_m' has already been declared
    existing_symbol = ode_shape.get_scope().resolve_to_symbol(ode_shape.get_variable().get_name_of_lhs(),
                                                              SymbolKind.VARIABLE)
    if existing_symbol is not None:
        existing_symbol.set_ode_definition(ode_shape.get_expression())
        existing_symbol.set_variable_type(VariableType.SHAPE)
        ode_shape.get_scope().update_variable_symbol(existing_symbol)
        code, message = Messages.get_ode_updated(ode_shape.get_variable().get_name_of_lhs())
        Logger.log_message(error_position=existing_symbol.get_referenced_object().get_source_position(),
                           code=code, message=message, log_level=LoggingLevel.INFO)
    else:
        code, message = Messages.get_no_variable_found(ode_shape.get_variable().get_name_of_lhs())
        Logger.log_message(code=code, message=message, error_position=ode_shape.get_source_position(),
                           log_level=LoggingLevel.ERROR)
    return
