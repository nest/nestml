from pynestml.meta_model.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.meta_model.ASTAssignment import ASTAssignment
from pynestml.meta_model.ASTBitOperator import ASTBitOperator
from pynestml.meta_model.ASTBlock import ASTBlock
from pynestml.meta_model.ASTBlockWithVariables import ASTBlockWithVariables
from pynestml.meta_model.ASTBody import ASTBody
from pynestml.meta_model.ASTComparisonOperator import ASTComparisonOperator
from pynestml.meta_model.ASTCompoundStmt import ASTCompoundStmt
from pynestml.meta_model.ASTDataType import ASTDataType
from pynestml.meta_model.ASTDeclaration import ASTDeclaration
from pynestml.meta_model.ASTElifClause import ASTElifClause
from pynestml.meta_model.ASTElseClause import ASTElseClause
from pynestml.meta_model.ASTEquationsBlock import ASTEquationsBlock
from pynestml.meta_model.ASTExpression import ASTExpression
from pynestml.meta_model.ASTForStmt import ASTForStmt
from pynestml.meta_model.ASTFunction import ASTFunction
from pynestml.meta_model.ASTFunctionCall import ASTFunctionCall
from pynestml.meta_model.ASTIfClause import ASTIfClause
from pynestml.meta_model.ASTIfStmt import ASTIfStmt
from pynestml.meta_model.ASTInputBlock import ASTInputBlock
from pynestml.meta_model.ASTInputLine import ASTInputLine
from pynestml.meta_model.ASTInputType import ASTInputType
from pynestml.meta_model.ASTLogicalOperator import ASTLogicalOperator
from pynestml.meta_model.ASTNestMLCompilationUnit import ASTNestMLCompilationUnit
from pynestml.meta_model.ASTNeuron import ASTNeuron
from pynestml.meta_model.ASTOdeEquation import ASTOdeEquation
from pynestml.meta_model.ASTOdeFunction import ASTOdeFunction
from pynestml.meta_model.ASTOdeShape import ASTOdeShape
from pynestml.meta_model.ASTOutputBlock import ASTOutputBlock
from pynestml.meta_model.ASTParameter import ASTParameter
from pynestml.meta_model.ASTReturnStmt import ASTReturnStmt
from pynestml.meta_model.ASTSimpleExpression import ASTSimpleExpression
from pynestml.meta_model.ASTSmallStmt import ASTSmallStmt
from pynestml.meta_model.ASTStmt import ASTStmt
from pynestml.meta_model.ASTUnaryOperator import ASTUnaryOperator
from pynestml.meta_model.ASTUnitType import ASTUnitType
from pynestml.meta_model.ASTUpdateBlock import ASTUpdateBlock
from pynestml.meta_model.ASTVariable import ASTVariable
from pynestml.meta_model.ASTWhileStmt import ASTWhileStmt


class ASTNestMLPrinter(object):
    tab_size = 2

    def __init__(self):
        self.indent = 0

    def print_node(self, node):
        if isinstance(node, ASTArithmeticOperator):
            return self.print_arithmetic_operator(node)
        if isinstance(node, ASTAssignment):
            return self.print_assignment(node)
        if isinstance(node, ASTBitOperator):
            return self.print_bit_operator(node)
        if isinstance(node, ASTBlock):
            return self.print_block(node)
        if isinstance(node, ASTBlockWithVariables):
            return self.print_block_with_variables(node)
        if isinstance(node, ASTBody):
            return self.print_body(node)
        if isinstance(node, ASTComparisonOperator):
            return self.print_comparison_operator(node)
        if isinstance(node, ASTCompoundStmt):
            return self.print_compound_stmt(node)
        if isinstance(node, ASTDataType):
            return self.print_data_type(node)
        if isinstance(node, ASTDeclaration):
            return self.print_declaration(node)
        if isinstance(node, ASTElifClause):
            return self.print_elif_clause(node)
        if isinstance(node, ASTElseClause):
            return self.print_else_clause(node)
        if isinstance(node, ASTEquationsBlock):
            return self.print_equations_block(node)
        if isinstance(node, ASTExpression):
            return self.print_expression(node)
        if isinstance(node, ASTForStmt):
            return self.print_for_stmt(node)
        if isinstance(node, ASTFunction):
            return self.print_function(node)
        if isinstance(node, ASTFunctionCall):
            return self.print_function_call(node)
        if isinstance(node, ASTIfClause):
            return self.print_if_clause(node)
        if isinstance(node, ASTIfStmt):
            return self.print_if_stmt(node)
        if isinstance(node, ASTInputBlock):
            return self.print_input_block(node)
        if isinstance(node, ASTInputLine):
            return self.print_input_line(node)
        if isinstance(node, ASTInputType):
            return self.print_input_type(node)
        if isinstance(node, ASTLogicalOperator):
            return self.print_logical_operator(node)
        if isinstance(node, ASTNestMLCompilationUnit):
            return self.print_compilation_unit(node)
        if isinstance(node, ASTNeuron):
            return self.print_neuron(node)
        if isinstance(node, ASTOdeEquation):
            return self.print_ode_equation(node)
        if isinstance(node, ASTOdeFunction):
            return self.print_ode_function(node)
        if isinstance(node, ASTOdeShape):
            return self.print_ode_shape(node)
        if isinstance(node, ASTOutputBlock):
            return self.print_output_block(node)
        if isinstance(node, ASTParameter):
            return self.print_parameter(node)
        if isinstance(node, ASTReturnStmt):
            return self.print_return_stmt(node)
        if isinstance(node, ASTSimpleExpression):
            return self.print_simple_expression(node)
        if isinstance(node, ASTSmallStmt):
            return self.print_small_stmt(node)
        if isinstance(node, ASTUnaryOperator):
            return self.print_unary_operator(node)
        if isinstance(node, ASTUnitType):
            return self.print_unit_type(node)
        if isinstance(node, ASTUpdateBlock):
            return self.print_update_block(node)
        if isinstance(node, ASTVariable):
            return self.print_variable(node)
        if isinstance(node, ASTWhileStmt):
            return self.print_while_stmt(node)
        if isinstance(node, ASTStmt):
            return self.print_stmt(node)
        return ''

    def print_neuron(self, node):
        # type: (ASTNeuron) -> str
        self.inc_indent()
        ret = 'neuron ' + node.get_name() + ':\n' + self.print_node(node.get_body()) + 'end' + '\n'
        self.dec_indent()
        return ret

    def print_arithmetic_operator(self, node):
        # type: (ASTArithmeticOperator) -> str
        if node.is_times_op:
            return ' * '
        elif node.is_div_op:
            return ' / '
        elif node.is_modulo_op:
            return ' % '
        elif node.is_plus_op:
            return ' + '
        elif node.is_minus_op:
            return ' - '
        elif node.is_pow_op:
            return ' ** '
        else:
            raise RuntimeError('(PyNestML.ArithmeticOperator.Print) Arithmetic operator not specified.')

    def print_assignment(self, node):
        # type: (ASTAssignment) -> str
        ret = self.print_node(node.lhs)
        if node.is_compound_quotient:
            ret += '/='
        elif node.is_compound_product:
            ret += '*='
        elif node.is_compound_minus:
            ret += '-='
        elif node.is_compound_sum:
            ret += '+='
        else:
            ret += '='
        ret += self.print_node(node.rhs)
        return ret

    def print_bit_operator(self, node):
        # type: (ASTBitOperator) -> str
        if node.isBitAnd():
            return ' & '
        elif node.isBitOr():
            return ' ^ '
        elif node.isBitOr():
            return ' | '
        elif node.isBitShiftLeft():
            return ' << '
        elif node.isBitShiftRight():
            return ' >> '
        else:
            raise RuntimeError('(PyNestML.BitOperator.Print) Type of bit operator not specified!')

    def print_block(self, node):
        # type: (ASTBlock) -> str
        ret = ''
        self.inc_indent()
        for stmt in node.stmts:
            ret += self.print_node(stmt)
            ret += '\n'
        self.dec_indent()
        return ret

    def print_block_with_variables(self, node):
        # type: (ASTBlockWithVariables) -> str
        temp_indent = self.indent
        self.inc_indent()
        ret = self.print_n_spaces(temp_indent)
        if node.is_state():
            ret += 'state'
        elif node.is_parameters():
            ret += 'parameters'
        elif node.is_internals():
            ret += 'internals'
        else:
            ret += 'initial_values'
        ret += ':\n'
        if node.get_declarations() is not None:
            for decl in node.get_declarations():
                ret += self.print_node(decl) + '\n'
        ret += self.print_n_spaces(temp_indent) + 'end'
        self.dec_indent()
        return ret

    def print_body(self, node):
        # type: (ASTBody) -> str
        ret = '\n'
        for elem in node.bodyElements:
            ret += self.print_node(elem)
            ret += '\n\n'
        return ret

    def print_comparison_operator(self, node):
        # type: (ASTComparisonOperator) -> str
        if node.isLt():
            return ' < '
        elif node.isLe():
            return ' <= '
        elif node.isEq():
            return ' == '
        elif node.isNe():
            return ' != '
        elif node.isNe2():
            return ' <> '
        elif node.isGe():
            return ' >= '
        elif node.isGt():
            return ' > '
        else:
            raise RuntimeError('(PyNestML.ComparisonOperator.Print) Type of comparison operator not specified!')

    def print_compound_stmt(self, node):
        # type: (ASTCompoundStmt) -> str
        if node.is_if_stmt():
            return self.print_node(node.get_if_stmt())
        elif node.is_for_stmt():
            return self.print_node(node.get_for_stmt())
        elif node.is_while_stmt():
            return self.print_node(node.get_while_stmt())
        else:
            raise RuntimeError('(PyNestML.CompoundStmt.Print) Type of compound statement not specified!')

    def print_data_type(self, node):
        # type: (ASTDataType) -> str
        if node.is_void():
            return 'void'
        elif node.is_string():
            return 'string'
        elif node.is_boolean():
            return 'boolean'
        elif node.is_integer():
            return 'integer'
        elif node.is_real():
            return 'real'
        elif node.is_unit_type():
            return self.print_node(node.get_unit_type())
        else:
            raise RuntimeError('Type of datatype not specified!')

    def print_declaration(self, node):
        # type: (ASTDeclaration) -> str
        ret = ''
        if node.is_recordable():
            ret += 'recordable '
        if node.is_function:
            ret += 'function '
        for var in node.get_variables():
            ret += self.print_node(var)
            if node.get_variables().index(var) < len(node.get_variables()) - 1:
                ret += ','
        ret += ' ' + self.print_node(node.get_data_type()) + ' '
        if node.has_size_parameter():
            ret += '[' + node.get_size_parameter() + ']'
        if node.has_expression():
            ret += ' = ' + self.print_node(node.get_expression()) + ' '
        if node.has_invariant():
            ret += ' [[' + self.print_node(node.get_invariant()) + ']]'
        return ' ' * self.indent + ret

    def print_elif_clause(self, node):
        # type: (ASTElifClause) -> str
        return (self.print_n_spaces(self.indent) + 'elif ' + self.print_node(node.get_condition()) + ':\n'
                + self.print_node(node.get_block()))

    def print_else_clause(self, node):
        # type: (ASTElseClause) -> str
        return self.print_n_spaces(self.indent) + 'else:\n' + self.print_node(node.get_block())

    def print_equations_block(self, node):
        # type: (ASTEquationsBlock) -> str
        temp_indent = self.indent
        self.inc_indent()
        ret = self.print_n_spaces(temp_indent)
        ret += 'equations:\n'
        for decl in node.get_declarations():
            ret += self.print_n_spaces(self.indent) + self.print_node(decl) + '\n'
        self.dec_indent()
        return ret + self.print_n_spaces(temp_indent) + 'end'

    def print_expression(self, node):
        # type: (ASTExpression) -> str
        ret = ''
        if node.is_expression():
            if node.is_encapsulated:
                ret += '('
            if node.is_logical_not:
                ret += 'not '
            if node.is_unary_operator():
                ret += self.print_node(node.get_unary_operator())
            ret += self.print_node(node.get_expression())
            if node.is_encapsulated:
                ret += ')'
        elif node.is_compound_expression():
            ret += self.print_node(node.get_lhs())
            ret += self.print_node(node.get_binary_operator())
            ret += self.print_node(node.get_rhs())
        elif node.is_ternary_operator():
            ret += self.print_node(node.get_condition()) + '?' + self.print_node(
                node.get_if_true()) + ':' + self.print_node(node.get_if_not())
        return ret

    def print_for_stmt(self, node):
        # type: (ASTForStmt) -> str
        return ('for ' + node.get_variable() + ' in ' + self.print_node(node.get_start_from()) + '...'
                + self.print_node(node.get_end_at()) + ' step ' +
                str(node.get_step()) + ':\n' + self.print_node(node.get_block()) + '\nend')

    def print_function(self, node):
        # type: (ASTFunction) -> str
        ret = 'function ' + node.get_name() + '('
        if node.has_parameters():
            for par in node.get_parameters():
                ret += self.print_node(par)
        ret += ')'
        if node.has_return_type():
            ret += self.print_node(node.get_return_type())
        ret += ':\n' + self.print_node(node.get_block()) + '\nend'
        return ret

    def print_function_call(self, node):
        # type: (ASTFunctionCall) -> str
        ret = str(node.get_name()) + '('
        for i in range(0, len(node.get_args())):
            ret += self.print_node(node.get_args()[i])
            if i < len(node.get_args()) - 1:  # in the case that it is not the last arg, print also a comma
                ret += ','
        ret += ')'
        return ret

    def print_if_clause(self, node):
        # type: (ASTIfClause) -> str
        return (self.print_n_spaces(self.indent) + 'if ' + self.print_node(node.get_condition()) + ':\n'
                + self.print_node(node.get_block()))

    def print_if_stmt(self, node):
        # type: (ASTIfStmt) -> str
        ret = self.print_node(node.get_if_clause())
        if node.get_elif_clauses() is not None:
            for clause in node.get_elif_clauses():
                ret += self.print_node(clause)
        if node.get_else_clause() is not None:
            ret += self.print_node(node.get_else_clause())
        ret += self.print_n_spaces(self.indent) + 'end'
        return ret

    def print_input_block(self, node):
        # type: (ASTInputBlock) -> str
        temp_indent = self.indent
        self.inc_indent()
        ret = self.print_n_spaces(temp_indent) + 'input:\n'
        if node.getInputLines() is not None:
            for inputDef in node.getInputLines():
                ret += self.print_n_spaces(self.indent) + self.print_node(inputDef) + '\n'
        ret += self.print_n_spaces(temp_indent) + 'end'
        self.dec_indent()
        return ret

    def print_input_line(self, node):
        # type: (ASTInputLine) -> str
        ret = node.get_name()
        if node.has_datatype():
            ret += ' ' + self.print_node(node.get_datatype()) + ' '
        if node.has_index_parameter():
            ret += '[' + node.get_index_parameter() + ']'
        ret += '<-'
        if node.has_input_types():
            for iType in node.get_input_types():
                ret += self.print_node(iType) + ' '
        if node.is_spike():
            ret += 'spike'
        else:
            ret += 'current'
        return ret

    def print_input_type(self, node):
        # type: (ASTInputType) -> str
        if node.is_inhibitory:
            return 'inhibitory'
        else:
            return 'excitatory'

    def print_logical_operator(self, node):
        # type: (ASTLogicalOperator) -> str
        if node.is_and():
            return ' and '
        else:
            return ' or '

    def print_compilation_unit(self, node):
        # type: (ASTNestMLCompilationUnit) -> str
        ret = ''
        if node.get_neuron_list() is not None:
            for neuron in node.get_neuron_list():
                ret += self.print_node(neuron) + '\n'
        return ret

    def print_ode_equation(self, node):
        # type: (ASTOdeEquation) -> str
        return self.print_node(node.get_lhs()) + '=' + self.print_node(node.get_rhs())

    def print_ode_function(self, node):
        # type: (ASTOdeFunction) -> str
        ret = ''
        if node.isRecordable():
            ret += 'recordable'
        ret += 'function ' + str(node.get_variable_name()) + ' ' + self.print_node(node.get_data_type()) + \
               ' = ' + self.print_node(node.get_expression())
        return ret

    def print_ode_shape(self, node):
        # type: (ASTOdeShape) -> str
        return 'shape ' + self.print_node(node.get_variable()) + ' = ' + self.print_node(node.get_expression())

    def print_output_block(self, node):
        # type: (ASTOutputBlock) -> str
        return self.print_n_spaces(self.indent) + 'output: ' + ('spike' if node.is_spike() else 'current')

    def print_parameter(self, node):
        # type: (ASTParameter) -> str
        return node.get_name() + ' ' + self.print_node(node.get_data_type())

    def print_return_stmt(self, node):
        # type: (ASTReturnStmt) -> str
        return 'return ' + (self.print_node(node.get_expression()) if node.has_expression() else '')

    def print_simple_expression(self, node):
        # type: (ASTSimpleExpression) -> str
        if node.is_function_call():
            return self.print_node(node.function_call)
        elif node.is_boolean_true():
            return 'True'
        elif node.is_boolean_false():
            return 'False'
        elif node.is_inf_literal():
            return 'inf'
        elif node.is_numeric_literal():
            if node.variable is not None:
                return str(node.numeric_literal) + self.print_node(node.variable)
            else:
                return str(node.numeric_literal)
        elif node.is_variable():
            return self.print_node(node.variable)
        elif node.is_string():
            return node.get_string()
        else:
            raise RuntimeError('Simple rhs at %s not specified!' % str(node.get_source_position()))

    def print_small_stmt(self, node):
        # type: (ASTSmallStmt) -> str
        if node.is_assignment():
            ret = self.print_n_spaces(self.indent) + self.print_node(node.get_assignment())
        elif node.is_function_call():
            ret = self.print_n_spaces(self.indent) + self.print_node(node.get_function_call())
        elif node.is_declaration():
            ret = self.print_n_spaces(self.indent) + self.print_node(node.get_declaration())
        else:
            ret = self.print_n_spaces(self.indent) + self.print_node(node.get_return_stmt())
        return ret

    def print_stmt(self, node):
        # type: (ASTStmt) -> str
        if node.is_small_stmt():
            return self.print_node(node.small_stmt)
        else:
            return self.print_node(node.compound_stmt)

    def print_unary_operator(self, node):
        # type: (ASTUnaryOperator) -> str
        if node.is_unary_plus:
            return '+'
        elif node.is_unary_minus:
            return '-'
        elif node.is_unary_tilde:
            return '~'
        else:
            raise RuntimeError('Type of unary operator not specified!')

    def print_unit_type(self, node):
        # type: (ASTUnitType) -> str
        if node.is_encapsulated:
            return '(' + self.print_node(node.compound_unit) + ')'
        elif node.is_pow:
            return self.print_node(node.base) + '**' + str(node.exponent)
        elif node.is_arithmetic_expression():
            t_lhs = (self.print_node(node.get_lhs()) if isinstance(node.get_lhs(), ASTUnitType) else node.get_lhs())
            if node.is_times:
                return self.print_node(t_lhs) + '*' + self.print_node(node.get_rhs())
            else:
                return self.print_node(t_lhs) + '/' + self.print_node(node.get_rhs())
        else:
            return node.unit

    def print_update_block(self, node):
        # type: (ASTUpdateBlock) -> str
        ret = (self.print_n_spaces(self.indent) + 'update:\n' +
               self.print_node(node.get_block()) +
               self.print_n_spaces(self.indent) + 'end')
        return ret

    def print_variable(self, node):
        # type: (ASTVariable) -> str
        ret = node.name
        for i in range(1, node.differential_order + 1):
            ret += "'"
        return ret

    def print_while_stmt(self, node):
        # type: (ASTWhileStmt) -> str
        temp_indent = self.indent
        self.inc_indent()
        ret = self.print_n_spaces(temp_indent) + 'while ' + self.print_node(
            node.get_condition()) + ':\n' + self.print_node(node.get_block()) + '\n' + self.print_n_spaces(
            temp_indent) + 'end'
        self.dec_indent()
        return ret

    def inc_indent(self):
        self.indent += self.tab_size

    def dec_indent(self):
        self.indent -= self.tab_size

    def print_n_spaces(self, n):
        return ' ' * n
