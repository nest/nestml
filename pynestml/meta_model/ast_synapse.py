#
# ast_synapse.py
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

from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_ode_shape import ASTOdeShape
from pynestml.meta_model.ast_synapse_body import ASTSynapseBody
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.symbols.variable_symbol import BlockType
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages


class ASTSynapse(ASTNode):
    """
    This class is used to store instances of synapses.
    ASTSynapse represents synapse.
    @attribute Name    The name of the synapse
    @attribute Body    The body of the synapse, e.g. internal, state, parameter...
    Grammar:
        synapse : 'synapse' NAME body;
    Attributes:
        name = None
        body = None
        artifact_name = None
    """

    def __init__(self, name, body, source_position=None, artifact_name=None):
        """
        Standard constructor.
        :param name: the name of the synapse.
        :type name: str
        :param body: the body containing the definitions.
        :type body: ASTBody
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        :param artifact_name: the name of the file this synapse is contained in
        :type artifact_name: str
        """
        print("In ASTSynapse::__init__()")

        assert isinstance(name, str), \
            '(PyNestML.AST.Synapse) No  or wrong type of synapse name provided (%s)!' % type(name)
        assert isinstance(body, ASTSynapseBody), \
            '(PyNestML.AST.Synapse) No or wrong type of synapse body provided (%s)!' % type(body)
        assert (artifact_name is not None and isinstance(artifact_name, str)), \
            '(PyNestML.AST.Synapse) No or wrong type of artifact name provided (%s)!' % type(artifact_name)
        super(ASTSynapse, self).__init__(source_position)
        self.name = name
        self.body = body
        self.artifact_name = artifact_name
        self._default_weight = None
        self.find_default_weight_and_delay()


    def find_default_weight_and_delay(self):
        import pdb;pdb.set_trace() #nb. look at self.body


    def get_name(self):
        """
        Returns the name of the synapse.
        :return: the name of the synapse.
        :rtype: str
        """
        return self.name

    def set_default_weight(self, w):
        self._default_weight = w

    def set_default_delay(self, var, expr, dtype):
        self._default_delay_variable = var
        self._default_delay_expression = expr
        self._default_delay_dtype = dtype

    def get_default_delay_expression(self):
        return self._default_delay_expression

    def get_default_delay_variable(self):
        return self._default_delay_variable

    def get_default_delay_dtype(self):
        return self._default_delay_dtype

    def get_weight_variable(self):
        return self._default_weight

    def get_default_weight(self):
        return self._default_weight


    def get_body(self):
        """
        Return the body of the synapse.
        :return: the body containing the definitions.
        :rtype: ASTSynapseBody
        """
        return self.body

    def get_artifact_name(self):
        """
        Returns the name of the artifact this synapse has been stored in.
        :return: the name of the file
        :rtype: str
        """
        return self.artifact_name

    def get_functions(self):
        """
        Returns a list of all function block declarations in this body.
        :return: a list of function declarations.
        :rtype: list(ASTFunction)
        """
        ret = list()
        from pynestml.meta_model.ast_function import ASTFunction
        for elem in self.get_body().get_synapse_body_elements():
            if isinstance(elem, ASTFunction):
                ret.append(elem)
        return ret


    def get_parameter_blocks(self):
        """
        Returns a list of all parameter blocks defined in this body.
        :return: a list of parameters-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body().get_synapse_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_parameters:
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret

    def get_internals_blocks(self):
        """
        Returns a list of all internals blocks defined in this body.
        :return: a list of internals-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body().get_synapse_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_internals:
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret

    def get_parameter_symbols(self):
        """
        Returns a list of all parameter symbol defined in the model.
        :return: a list of parameter symbols.
        :rtype: list(VariableSymbol)
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and symbol.block_type == BlockType.PARAMETERS and \
                    not symbol.is_predefined:
                ret.append(symbol)
        return ret

    def get_internal_symbols(self):
        """
        Returns a list of all internals symbol defined in the model.
        :return: a list of internals symbols.
        :rtype: list(VariableSymbol)
        """
        from pynestml.symbols.variable_symbol import BlockType
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and symbol.block_type == BlockType.INTERNALS and \
                    not symbol.is_predefined:
                ret.append(symbol)
        return ret

    def get_parameter_non_alias_symbols(self):
        """
        Returns a list of all variable symbols representing non-function parameter variables.
        :return: a list of variable symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for param in self.get_parameter_symbols():
            if not param.is_function and not param.is_predefined:
                ret.append(param)
        return ret

    def get_internal_non_alias_symbols(self):
        """
        Returns a list of all variable symbols representing non-function internal variables.
        :return: a list of variable symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for param in self.get_internal_symbols():
            if not param.is_function and not param.is_predefined:
                ret.append(param)

        return ret


    def get_parameter_invariants(self):
        """
        Returns a list of all invariants of all parameters.
        :return: a list of rhs representing invariants
        :rtype: list(ASTExpression)
        """
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        ret = list()
        blocks = self.get_parameter_blocks()
        # the get parameters block is not deterministic method, it can return a list or a single object.
        if isinstance(blocks, list):
            for block in blocks:
                for decl in block.get_declarations():
                    if decl.has_invariant():
                        ret.append(decl.get_invariant())
        elif isinstance(blocks, ASTBlockWithVariables):
            for decl in blocks.get_declarations():
                if decl.has_invariant():
                    ret.append(decl.get_invariant())
        return ret

    def add_to_internal_block(self, declaration):
        # todo by KP: factor me out to utils
        """
        Adds the handed over declaration the internal block
        :param declaration: a single declaration
        :type declaration: ast_declaration
        """
        if self.get_internals_blocks() is None:
            ASTUtils.create_internal_block(self)
        self.get_internals_blocks().get_declarations().append(declaration)
        return

    def print_parameter_comment(self, prefix=None):
        """
        Prints the update block comment.
        :param prefix: a prefix string
        :type prefix: str
        :return: the corresponding comment.
        :rtype: str
        """
        block = self.get_parameter_blocks()
        if block is None:
            return prefix if prefix is not None else ''
        return block.print_comment(prefix)

    def print_internal_comment(self, prefix=None):
        """
        Prints the internal block comment.
        :param prefix: a prefix string
        :type prefix: str
        :return: the corresponding comment.
        :rtype: str
        """
        block = self.get_internals_blocks()
        if block is None:
            return prefix if prefix is not None else ''
        return block.print_comment(prefix)

    def print_comment(self, prefix=None):
        """
        Prints the header information of this synapse.
        :param prefix: a prefix string
        :type prefix: str
        :return: the comment.
        :rtype: str
        """
        ret = ''
        if self.get_comment() is None or len(self.get_comment()) == 0:
            return prefix if prefix is not None else ''
        for comment in self.get_comment():
            ret += (prefix if prefix is not None else '') + comment + '\n'
        return ret

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.get_body() is ast:
            return self
        elif self.get_body().get_parent(ast) is not None:
            return self.get_body().get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTSynapse):
            return False
        return self.get_name() == other.get_name() and self.get_body().equals(other.get_body())
