# -*- coding: utf-8 -*-
#
# precompute_reciprocals_transformer.py
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

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Union

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.transformers.transformer import Transformer
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor


class PrecomputeReciprocalsTransformer(Transformer):
    r"""Replace divisions by constants in propagator expressions with multiplications by precomputed reciprocals.

    For every propagator (an internal whose name starts with ``__P__``, as added after ODE-toolbox analysis), each division ``a / b`` whose denominator ``b`` is constant during the simulation is rewritten as ``a * __inv_b``, and a new internal ``__inv_b real = 1 / b`` is inserted into the internals block, before the first propagator. A denominator is considered constant if all of its variables are (scalar) parameters of the model, and it contains no function calls. A division ``1 / b`` is replaced by ``__inv_b`` altogether.

    For example, the propagator

    .. code-block:: nestml

       __P__x__x real = exp(-__h / tau)

    becomes

    .. code-block:: nestml

       __inv_tau real = 1.0 / tau
       __P__x__x real = exp(-__h * __inv_tau)

    This is useful for targets without a hardware divider or floating-point unit (such as SpiNNaker), where the propagators have to be evaluated at runtime for a variable timestep ``__h`` (for instance, the time since the last spike in a synapse), and a (software) division is expensive. The reciprocals only depend on parameters, so they can be computed once, ahead of time (for instance, on the host).

    This transformer must run after ODE-toolbox analysis, and after the propagators have been added to the internals block of the model.

    For each model, the new reciprocals are stored in the metadata under the key ``precomputed_reciprocals``, as a mapping from the name of the new internal variable to the AST of its denominator.

    Options:

    - **skip_exp_arguments**: If True, do not rewrite divisions inside the argument of ``exp()``. This is needed when ``exp()`` calls are replaced by look-up tables that rely on the argument being of the form ``-a / b`` (default: False).
    - **prefix**: Prefix for the names of the newly created internals (default: ``"__inv_"``).
    """

    _default_options = {
        "skip_exp_arguments": False,
        "prefix": "__inv_"
    }

    PROPAGATOR_PREFIX = "__P__"

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    @override
    def transform(self,
                  models: Union[ASTModel, Iterable[ASTModel]],
                  metadata: Optional[Dict[str, Dict[str, Any]]] = None) -> Union[ASTModel, Iterable[ASTModel]]:
        single = isinstance(models, ASTModel)
        if single:
            models = [models]

        for model in models:
            reciprocals = self._transform_model(model)
            if metadata is not None:
                if model.get_name() not in metadata.keys():
                    metadata[model.get_name()] = {}

                metadata[model.get_name()]["precomputed_reciprocals"] = reciprocals

        if single:
            return models[0]

        return models

    def _transform_model(self, model: ASTModel) -> Dict[str, Union[ASTExpression, ASTSimpleExpression]]:
        r"""Rewrite the propagators of a single model. Return a mapping from the name of each newly added internal to the AST of its denominator."""
        reciprocals: Dict[str, Union[ASTExpression, ASTSimpleExpression]] = {}

        if len(model.get_internals_blocks()) != 1:
            return reciprocals

        internals_block = model.get_internals_blocks()[0]
        propagator_decls = [decl for decl in internals_block.get_declarations()
                            if any(var.get_name().startswith(PrecomputeReciprocalsTransformer.PROPAGATOR_PREFIX) for var in decl.get_variables())]
        if not propagator_decls:
            return reciprocals

        parameter_names = set([var.get_name() for var in model.get_parameter_variables()])
        used_names = self._collect_declared_names(model)

        # map from the (NESTML) string representation of the denominator to the name of its reciprocal; used to reuse the same reciprocal for identical denominators
        denominator_to_name: Dict[str, str] = {}

        for decl in propagator_decls:
            new_expr = self._rewrite(decl.get_expression(), model, parameter_names, used_names, denominator_to_name, reciprocals)
            if new_expr is not decl.get_expression():
                decl.set_expression(new_expr)

        if not reciprocals:
            return reciprocals

        # insert the new declarations before the first propagator, so that they are computed before they are used
        insert_idx = internals_block.get_declarations().index(propagator_decls[0])
        for name, denominator in reciprocals.items():
            decl = ModelParser.parse_declaration(name + " real = 1.0 / (" + str(denominator) + ")")
            decl.update_scope(internals_block.get_scope())
            internals_block.get_declarations().insert(insert_idx, decl)
            insert_idx += 1

            Logger.log_message(model, None, "Precomputing reciprocal " + name + " = 1 / (" + str(denominator) + ")", None, LoggingLevel.INFO)

        model.accept(ASTParentVisitor())
        model.accept(ASTSymbolTableVisitor())

        return reciprocals

    def _rewrite(self, node, model: ASTModel, parameter_names: Set[str], used_names: Set[str], denominator_to_name: Dict[str, str], reciprocals: Dict[str, Any]):
        r"""Recursively rewrite divisions by constants in ``node``. Return the node that should replace ``node`` in its parent (this is ``node`` itself, unless the whole node was replaced)."""
        if node is None:
            return None

        if isinstance(node, ASTSimpleExpression):
            if node.is_function_call():
                self._rewrite_function_call(node.get_function_call(), model, parameter_names, used_names, denominator_to_name, reciprocals)

            return node

        assert isinstance(node, ASTExpression)

        # first rewrite children, then this node (so that nested divisions are handled bottom-up)
        node.expression = self._rewrite(node.expression, model, parameter_names, used_names, denominator_to_name, reciprocals)
        node.lhs = self._rewrite(node.lhs, model, parameter_names, used_names, denominator_to_name, reciprocals)
        node.rhs = self._rewrite(node.rhs, model, parameter_names, used_names, denominator_to_name, reciprocals)
        node.condition = self._rewrite(node.condition, model, parameter_names, used_names, denominator_to_name, reciprocals)
        node.if_true = self._rewrite(node.if_true, model, parameter_names, used_names, denominator_to_name, reciprocals)
        node.if_not = self._rewrite(node.if_not, model, parameter_names, used_names, denominator_to_name, reciprocals)

        if not (isinstance(node.binary_operator, ASTArithmeticOperator) and node.binary_operator.is_div_op):
            return node

        if not self._is_constant(node.rhs, parameter_names):
            return node

        name = self._get_reciprocal_name(node.rhs, used_names, denominator_to_name, reciprocals)
        reciprocal_var = ASTNodeFactory.create_ast_simple_expression(variable=ASTVariable(name, scope=node.get_scope()),
                                                                     source_position=node.get_source_position())
        reciprocal_var.update_scope(node.get_scope())

        if self._is_numeric_literal_one(node.lhs):
            # ``1 / b`` becomes ``__inv_b``
            if node.is_encapsulated:
                node.binary_operator = None
                node.lhs = None
                node.rhs = None
                node.expression = reciprocal_var
                return node

            return reciprocal_var

        # ``a / b`` becomes ``a * __inv_b``
        node.binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True, source_position=node.binary_operator.get_source_position())
        node.rhs = reciprocal_var

        return node

    def _rewrite_function_call(self, function_call: ASTFunctionCall, model: ASTModel, parameter_names: Set[str], used_names: Set[str], denominator_to_name: Dict[str, str], reciprocals: Dict[str, Any]) -> None:
        if self.get_option("skip_exp_arguments") and function_call.get_name() == PredefinedFunctions.EXP:
            return

        for i, arg in enumerate(function_call.get_args()):
            function_call.args[i] = self._rewrite(arg, model, parameter_names, used_names, denominator_to_name, reciprocals)

    def _is_constant(self, node, parameter_names: Set[str]) -> bool:
        r"""Return True if ``node`` depends only on scalar parameters and numeric literals."""
        variables: List[ASTVariable] = []
        function_calls: List[ASTFunctionCall] = []

        def collect(_node):
            if isinstance(_node, ASTVariable):
                variables.append(_node)
            elif isinstance(_node, ASTFunctionCall):
                function_calls.append(_node)

        node.accept(ASTHigherOrderVisitor(visit_funcs=collect))

        if function_calls:
            return False

        for var in variables:
            if var.get_name() not in parameter_names:
                return False

            if var.has_vector_parameter() or var.is_delay_variable() or var.get_differential_order() > 0:
                return False

        return True

    @classmethod
    def _strip_parentheses(cls, node):
        r"""Remove any redundant parentheses around ``node``, e.g. ``((tau))`` becomes ``tau``."""
        while isinstance(node, ASTExpression) and node.is_encapsulated and node.get_expression() is not None \
                and node.unary_operator is None and not node.is_logical_not:
            node = node.get_expression()

        return node

    def _is_numeric_literal_one(self, node) -> bool:
        node = self._strip_parentheses(node)

        return isinstance(node, ASTSimpleExpression) and node.is_numeric_literal() and not node.is_variable() and node.get_numeric_literal() == 1

    def _get_reciprocal_name(self, denominator, used_names: Set[str], denominator_to_name: Dict[str, str], reciprocals: Dict[str, Any]) -> str:
        denominator = self._strip_parentheses(denominator)
        key = str(denominator).strip()
        if key in denominator_to_name.keys():
            return denominator_to_name[key]

        if isinstance(denominator, ASTSimpleExpression) and denominator.is_variable():
            base_name = self.get_option("prefix") + denominator.get_variable().get_name()
        else:
            base_name = self.get_option("prefix") + "expr" + str(len([n for n in reciprocals.keys() if n.startswith(self.get_option("prefix") + "expr")]))

        name = base_name
        i = 0
        while name in used_names:
            i += 1
            name = base_name + "_" + str(i)

        used_names.add(name)
        denominator_to_name[key] = name
        reciprocals[name] = denominator.clone()

        return name

    def _collect_declared_names(self, model: ASTModel) -> Set[str]:
        names = set()

        def collect(_node):
            if isinstance(_node, ASTDeclaration):
                names.update([var.get_name() for var in _node.get_variables()])

        model.accept(ASTHigherOrderVisitor(visit_funcs=collect))

        return names

    @classmethod
    def strip_suffix_from_variable_names(cls, node, suffix: str):
        r"""Return a clone of ``node`` in which ``suffix`` is removed from the end of every variable name."""
        node = node.clone()

        def rename(_node):
            if isinstance(_node, ASTVariable) and _node.get_name().endswith(suffix):
                _node.set_name(_node.get_name()[:-len(suffix)])

        node.accept(ASTHigherOrderVisitor(visit_funcs=rename))

        return node
