#
# ASTExpressionCollectorVisitor.py
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


class ASTExpressionCollectorVisitor(object):
    """
    Traverses through the complete neuron and collects all rhs as used. This visitor is used to ensure
    certain properties, e.g., that all variables are declared and no functions redeclared.
    This visitor can not be directly implemented by the NESTML visitor given the fact, that only the most top
    level rhs, but not its subexpression shall be visited.
    """

    @classmethod
    def collectExpressionsInNeuron(cls, _neuron=None):
        """
        Collects all expressions located in the overall neuron declaration. Caution: This collector assures 
        that for each type of block, at most one block exists. This should be ensured by cocos. Except for 
        function block, which can be defined more than once.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        :return: a list of rhs objects.
        :rtype: list(ASTExpression)
        """
        from pynestml.modelprocessor.ASTNeuron import ASTNeuron
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of neuron provided (%s)!' % type(_neuron)
        ret = list()
        if _neuron.get_state_blocks() is not None:
            ret.extend(cls.collectExpressionsInStateBlock(_neuron.get_state_blocks()))
        if _neuron.get_initial_blocks() is not None:
            ret.extend(cls.collectExpressionsInInitialBlock(_neuron.get_initial_blocks()))
        if _neuron.get_input_blocks() is not None:
            ret.extend(cls.collectExpressionsInInternalsBlock(_neuron.get_internals_blocks()))
        if _neuron.get_parameter_blocks():
            ret.extend(cls.collectExpressionsInParametersBlock(_neuron.get_parameter_blocks()))
        if _neuron.get_update_blocks() is not None:
            ret.extend(cls.collectExpressionInUpdateBlock(_neuron.get_update_blocks()))
        if _neuron.get_equations_blocks() is not None:
            ret.extend(cls.collectExpressionsInEquationsBlock(_neuron.get_equations_blocks()))
        if _neuron.get_functions() is not None:
            for func in _neuron.get_functions():
                ret.extend(cls.collectExpressionsInFunctionBlock(func))
        ret = (x for x in ret if x is not None)
        return ret

    @classmethod
    def collectExpressionsInStateBlock(cls, _block=None):
        """
        Collects all expressions in the state block.
        :param _block: a single state block.
        :type _block: ASTBlockWithVariables
        :return: a list of all rhs in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
        assert (_block is not None and (isinstance(_block, ASTBlockWithVariables) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of state block provided (%s)!' % type(_block)
        assert (isinstance(_block, list) or _block.isState()), \
            '(PyNestML.Visitor.ExpressionCollector) Not a state block provided (%s)!' % type(_block)
        ret = list()
        if isinstance(_block, list):
            for block in _block:
                for decl in block.getDeclarations():
                    ret.append(decl.get_expression())
        else:
            for decl in _block.getDeclarations():
                ret.append(decl.get_expression())
        return ret

    @classmethod
    def collectExpressionsInInitialBlock(cls, _block=None):
        """
        Collects all expressions in the state block.
        :param _block: a single state block.
        :type _block: ASTBlockWithVariables
        :return: a list of all rhs in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
        assert (_block is not None and (isinstance(_block, ASTBlockWithVariables) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of state block provided (%s)!' % type(_block)
        assert (isinstance(_block, list) or _block.isInitialValues()), \
            '(PyNestML.Visitor.ExpressionCollector) Not a initial block provided (%s)!' % type(_block)
        ret = list()
        if isinstance(_block, list):
            for block in _block:
                for decl in block.getDeclarations():
                    ret.append(decl.get_expression())
        else:
            for decl in _block.getDeclarations():
                ret.append(decl.get_expression())
        return ret

    @classmethod
    def collectExpressionsInParametersBlock(cls, _block=None):
        """
        Collects all rhs in the parameters block
        :param _block: a single parameters block.
        :type _block: ASTBlockWithVariables
        :return: a list of all rhs in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
        assert (_block is not None and (isinstance(_block, ASTBlockWithVariables) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of parameters block provided (%s)!' % type(_block)
        assert (isinstance(_block, list) or _block.isParameters()), \
            '(PyNestML.Visitor.ExpressionCollector) Not a parameters block provided (%s)!' % type(_block)
        ret = list()
        if isinstance(_block, list):
            for block in _block:
                for decl in block.getDeclarations():
                    ret.append(decl.get_expression())
        else:
            for decl in _block.getDeclarations():
                ret.append(decl.get_expression())
        return ret

    @classmethod
    def collectExpressionsInInternalsBlock(cls, _block=None):
        """
        Collects all rhs in the internals block.
        :param _block: a single internals block
        :type _block: ASTBlockWithVariables
        :return: a list of all rhs in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
        assert (_block is not None and (isinstance(_block, ASTBlockWithVariables) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of internals block provided (%s)!' % type(_block)
        assert (isinstance(_block, list) or _block.isInternals()), \
            '(PyNestML.Visitor.ExpressionCollector) Not a internals block provided (%s)!' % type(_block)
        ret = list()
        if isinstance(_block, list):
            for block in _block:
                for decl in block.getDeclarations():
                    ret.append(decl.get_expression())
        else:
            for decl in _block.getDeclarations():
                ret.append(decl.get_expression())
        return ret

    @classmethod
    def collectExpressionInUpdateBlock(cls, _block=None):
        """
        Collects all expressions in the update block.
        :param _block: a single update block
        :type _block: ASTUpdateBlock
        :return: a list of all rhs in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.modelprocessor.ASTUpdateBlock import ASTUpdateBlock
        assert (_block is not None and (isinstance(_block, ASTUpdateBlock) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of update block provided (%s)!' % type(_block)
        if isinstance(_block, list):
            ret = list()
            for block in _block:
                ret.extend(cls.collectExpressionInBlock(block.get_block()))
            return ret
        else:
            return cls.collectExpressionInBlock(_block.get_block())

    @classmethod
    def collectExpressionsInEquationsBlock(cls, _block=None):
        """
        Collects all expressions in the equations block.
        :param _block: 
        :type _block: 
        :return: a list of all rhs in the block
        :rtype: list(ASTExpression) 
        """
        if _block is None:
            return list()
        from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
        from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
        assert (_block is not None and (isinstance(_block, ASTEquationsBlock) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of equations block provided (%s)!' % type(_block)
        ret = list()
        if isinstance(_block, list):
            for block in _block:
                for decl in block.getDeclarations():
                    if isinstance(decl, ASTOdeFunction):
                        ret.append(decl.get_expression())
                    elif isinstance(decl, ASTOdeShape):
                        ret.append(decl.get_expression())
                    elif isinstance(decl, ASTOdeEquation):
                        ret.append(decl.get_rhs())
        else:
            for decl in _block.getDeclarations():
                if isinstance(decl, ASTOdeFunction):
                    ret.append(decl.get_expression())
                elif isinstance(decl, ASTOdeShape):
                    ret.append(decl.get_expression())
                elif isinstance(decl, ASTOdeEquation):
                    ret.append(decl.get_rhs())
        return ret

    @classmethod
    def collectExpressionsInFunctionBlock(cls, _block=None):
        """
        Collects all expressions in the function block.
        :param _block: a single function block
        :type _block: ASTFunction
        :return: a list of all rhs in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.modelprocessor.ASTFunction import ASTFunction
        assert (_block is not None and (isinstance(_block, ASTFunction) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of function block provided (%s)!' % type(_block)
        if isinstance(_block, list):
            ret = list()
            for block in _block:
                ret.extend(cls.collectExpressionInBlock(block.get_block()))
            return ret
        else:
            return cls.collectExpressionInBlock(_block.get_block())

    @classmethod
    def collectExpressionInBlock(cls, _block=None):
        """
        Collects all expressions in the  block.
        :param _block: a single block.
        :type _block: ASTBlock
        :return: a list of all rhs in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.modelprocessor.ASTBlock import ASTBlock
        from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
        from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
        assert (_block is not None and isinstance(_block, ASTBlock)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of block provided (%s)!' % type(_block)
        ret = list()
        for stmt in _block.get_stmts():
            ret.extend(cls.collectExpressionsInStmt(stmt))
        return ret

    @classmethod
    def collectExpressionsInCompoundStmt(cls, _stmt=None):
        """
        Collects all expressions in a compound rhs.
        :param _stmt: a single compound statement.
        :type _stmt: ASTCompoundStmt
        :return: a list of all expressions in the compound statement.
        :rtype: list(ASTExpression)
        """
        if _stmt is None:
            return list()
        from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
        assert (_stmt is not None and isinstance(_stmt, ASTCompoundStmt)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of statement provided (%s)!' % type(_stmt)
        if _stmt.isIfStmt():
            return cls.collectExpressionsInIfStmt(_stmt.getIfStmt())
        elif _stmt.isWhileStmt():
            return cls.collectExpressionsInWhileStmt(_stmt.getWhileStmt())
        elif _stmt.isForStmt():
            return cls.collectExpressionsInForStmt(_stmt.getForStmt())
        else:
            return list()

    @classmethod
    def collectExpressionsInSmallStmt(cls, _stmt=None):
        """
        Collects all expressions in a compound rhs.
        :param _stmt: a single small statement.
        :type _stmt: ASTSmallStmt
        :return: a list of all expressions in the compound statement.
        :rtype: list(ASTExpression)
        """
        if _stmt is None:
            return list()
        from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
        assert (_stmt is not None and isinstance(_stmt, ASTSmallStmt)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of statement provided (%s)!' % type(_stmt)
        ret = list()
        if _stmt.is_assignment():
            ret.append(_stmt.get_assignment().get_expression())
        elif _stmt.is_declaration():
            if _stmt.get_declaration().has_expression():
                ret.append(_stmt.get_declaration().get_expression())
            if _stmt.get_declaration().has_invariant():
                ret.append((_stmt.get_declaration().get_invariant()))
        elif _stmt.is_return_stmt():
            if _stmt.get_return_stmt().has_expression():
                ret.append(_stmt.get_return_stmt().get_expression())
        elif _stmt.is_function_call():
            if _stmt.get_function_call().has_args():
                ret.extend(_stmt.get_function_call().get_args())
        return ret

    @classmethod
    def collectExpressionsInIfStmt(cls, _stmt=None):
        """
        Collects all expressions located in the if-stmt.
        :param _stmt: a single if statement.
        :type _stmt: ASTIfStmt
        :return: a list of all expressions
        :rtype: list(ASTExpression)
        """
        if _stmt is None:
            return list()
        from pynestml.modelprocessor.ASTIfStmt import ASTIfStmt
        assert (_stmt is not None and isinstance(_stmt, ASTIfStmt)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of statement provided (%s)!' % type(_stmt)
        ret = list()
        ret.append(_stmt.getIfClause().get_condition())
        ret.extend(cls.collectExpressionInBlock(_stmt.getIfClause().get_block()))
        for clause in _stmt.getElifClauses():
            ret.append(clause.get_condition())
            ret.extend(cls.collectExpressionInBlock(clause.get_block()))
        if _stmt.hasElseClause():
            ret.extend(cls.collectExpressionInBlock(_stmt.getElseClause().get_block()))
        return ret

    @classmethod
    def collectExpressionsInWhileStmt(cls, _stmt=None):
        """
        Collects all expressions located in the while-stmt.
        :param _stmt: a single while statement.
        :type _stmt: ASTWhileStmt
        :return: a list of all expressions
        :rtype: list(ASTExpression)
        """
        if _stmt is None:
            return list()
        from pynestml.modelprocessor.ASTWhileStmt import ASTWhileStmt
        assert (_stmt is not None and isinstance(_stmt, ASTWhileStmt)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of statement provided (%s)!' % type(_stmt)
        ret = list()
        ret.append(_stmt.get_condition())
        ret.extend(cls.collectExpressionInBlock(_stmt.get_block()))
        return ret

    @classmethod
    def collectExpressionsInForStmt(cls, _stmt=None):
        """
        Collects all expressions located in the for-stmt.
        :param _stmt: a single for stmt.
        :type _stmt: ASTForStmt
        :return: a list of all expressions
        :rtype: list(ASTExpression)
        """
        if _stmt is None:
            return list()
        from pynestml.modelprocessor.ASTForStmt import ASTForStmt
        assert (_stmt is not None and isinstance(_stmt, ASTForStmt)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of statement provided (%s)!' % type(_stmt)
        ret = list()
        ret.append(_stmt.get_start_from())
        ret.append(_stmt.get_end_at())
        ret.extend(cls.collectExpressionInBlock(_stmt.get_block()))
        return ret

    @classmethod
    def collectExpressionsInStmt(cls, stmt):
        """
        Collects all expressions located in the stmt.
        :param stmt: a single stmt
        :type stmt: ASTStmt
        :return: list(ASTExpression)
        """
        from pynestml.modelprocessor.ASTStmt import ASTStmt
        if stmt is None:
            return list()
        ret = list()
        if isinstance(stmt, ASTStmt):
            if stmt.is_small_stmt():
                ret.extend(cls.collectExpressionsInSmallStmt(stmt.small_stmt))
            if stmt.is_compound_stmt():
                ret.extend(cls.collectExpressionsInCompoundStmt(stmt.compound_stmt))
        return ret
