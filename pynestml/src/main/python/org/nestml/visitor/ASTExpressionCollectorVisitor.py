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
    Traverses through the complete neuron and collects all expression as used. This visitor is used to ensure 
    certain properties, e.g., that all variables are declared and no functions redeclared.
    """

    @classmethod
    def collectExpressionsInNeuron(cls, _neuron=None):
        """
        Collects all expressions located in the overall neuron declaration. Caution: This collector assures 
        that for each type of block, at most one block exists. This should be ensured by cocos. Except for 
        function block, which can be defined more than once.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        :return: a list of expression objects.
        :rtype: list(ASTExpression)
        """
        from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of neuron provided (%s)!' % type(_neuron)
        ret = list()
        if _neuron.getStateBlocks() is not None:
            ret.extend(cls.collectExpressionsInStateBlock(_neuron.getStateBlocks()))
        if _neuron.getInputBlocks() is not None:
            ret.extend(cls.collectExpressionsInInternalsBlock(_neuron.getInternalsBlocks()))
        if _neuron.getParameterBlocks():
            ret.extend(cls.collectExpressionsInParametersBlock(_neuron.getParameterBlocks()))
        if _neuron.getUpdateBlocks() is not None:
            ret.extend(cls.collectExpressionInUpdateBlock(_neuron.getUpdateBlocks()))
        if _neuron.getEquationsBlocks() is not None:
            ret.extend(cls.collectExpressionsInEquationsBlock(_neuron.getEquationsBlocks()))
        if _neuron.getFunctions() is not None:
            for func in _neuron.getFunctions():
                ret.extend(cls.collectExpressionsInFunctionBlock(func))
        ret = (x for x in ret if x is not None)
        return ret

    @classmethod
    def collectExpressionsInStateBlock(cls, _block=None):
        """
        Collects all expressions in the state block.
        :param _block: a single state block.
        :type _block: ASTBlockWithVariables
        :return: a list of all expression in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.src.main.python.org.nestml.ast.ASTBlockWithVariables import ASTBlockWithVariables
        assert (_block is not None and (isinstance(_block, ASTBlockWithVariables) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of state block provided (%s)!' % type(_block)
        assert (isinstance(_block, list) or _block.isState()), \
            '(PyNestML.Visitor.ExpressionCollector) Not a state block provided!'
        ret = list()
        if isinstance(_block, list):
            for block in _block:
                for decl in block.getDeclarations():
                    ret.append(decl.getExpr())
        else:
            for decl in _block.getDeclarations():
                ret.append(decl.getExpr())
        return ret

    @classmethod
    def collectExpressionsInParametersBlock(cls, _block=None):
        """
        Collects all expression in the parameters block
        :param _block: a single parameters block.
        :type _block: ASTBlockWithVariables
        :return: a list of all expression in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.src.main.python.org.nestml.ast.ASTBlockWithVariables import ASTBlockWithVariables
        assert (_block is not None and (isinstance(_block, ASTBlockWithVariables) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of parameters block provided (%s)!' % type(_block)
        assert (isinstance(_block, list) or _block.isParameters()), \
            '(PyNestML.Visitor.ExpressionCollector) Not a parameters block provided!'
        ret = list()
        if isinstance(_block, list):
            for block in _block:
                for decl in block.getDeclarations():
                    ret.append(decl.getExpr())
        else:
            for decl in _block.getDeclarations():
                ret.append(decl.getExpr())
        return ret

    @classmethod
    def collectExpressionsInInternalsBlock(cls, _block=None):
        """
        Collects all expression in the internals block.
        :param _block: a single internals block
        :type _block: ASTBlockWithVariables
        :return: a list of all expression in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.src.main.python.org.nestml.ast.ASTBlockWithVariables import ASTBlockWithVariables
        assert (_block is not None and (isinstance(_block, ASTBlockWithVariables) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of internals block provided (%s)!' % type(_block)
        assert (isinstance(_block, list) or _block.isInternals()), \
            '(PyNestML.Visitor.ExpressionCollector) Not a internals block provided!'
        ret = list()
        if isinstance(_block, list):
            for block in _block:
                for decl in block.getDeclarations():
                    ret.append(decl.getExpr())
        else:
            for decl in _block.getDeclarations():
                ret.append(decl.getExpr())
        return ret

    @classmethod
    def collectExpressionInUpdateBlock(cls, _block=None):
        """
        Collects all expressions in the update block.
        :param _block: a single update block
        :type _block: ASTUpdateBlock
        :return: a list of all expression in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.src.main.python.org.nestml.ast.ASTUpdateBlock import ASTUpdateBlock
        assert (_block is not None and (isinstance(_block, ASTUpdateBlock) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of update block provided (%s)!' % type(_block)
        if isinstance(_block, list):
            ret = list()
            for block in _block:
                ret.extend(cls.collectExpressionInBlock(block))
            return ret
        else:
            return cls.collectExpressionInBlock(_block.getBlock())

    @classmethod
    def collectExpressionsInEquationsBlock(cls, _block=None):
        """
        Collects all expressions in the equations block.
        :param _block: 
        :type _block: 
        :return: a list of all expression in the block
        :rtype: list(ASTExpression) 
        """
        if _block is None:
            return list()
        from pynestml.src.main.python.org.nestml.ast.ASTEquationsBlock import ASTEquationsBlock
        from pynestml.src.main.python.org.nestml.ast.ASTOdeEquation import ASTOdeEquation
        from pynestml.src.main.python.org.nestml.ast.ASTOdeShape import ASTOdeShape
        from pynestml.src.main.python.org.nestml.ast.ASTOdeFunction import ASTOdeFunction
        assert (_block is not None and (isinstance(_block, ASTEquationsBlock) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of equations block provided (%s)!' % type(_block)
        ret = list()
        if isinstance(_block, list):
            for block in _block:
                for decl in block.getDeclarations():
                    if isinstance(decl, ASTOdeFunction):
                        ret.append(decl.getExpression())
                    elif isinstance(decl, ASTOdeShape):
                        ret.append(decl.getExpression())
                    elif isinstance(decl, ASTOdeEquation):
                        ret.append(decl.getRhs())
        else:
            for decl in _block.getDeclarations():
                if isinstance(decl, ASTOdeFunction):
                    ret.append(decl.getExpression())
                elif isinstance(decl, ASTOdeShape):
                    ret.append(decl.getExpression())
                elif isinstance(decl, ASTOdeEquation):
                    ret.append(decl.getRhs())
        return ret

    @classmethod
    def collectExpressionsInFunctionBlock(cls, _block=None):
        """
        Collects all expressions in the function block.
        :param _block: a single function block
        :type _block: ASTFunction
        :return: a list of all expression in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.src.main.python.org.nestml.ast.ASTFunction import ASTFunction
        assert (_block is not None and (isinstance(_block, ASTFunction) or isinstance(_block, list))), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of function block provided (%s)!' % type(_block)
        if isinstance(_block, list):
            ret = list()
            for block in _block:
                ret.extend(cls.collectExpressionInBlock(block.getBlock()))
            return ret
        else:
            return cls.collectExpressionInBlock(_block.getBlock())

    @classmethod
    def collectExpressionInBlock(cls, _block=None):
        """
        Collects all expressions in the  block.
        :param _block: a single block.
        :type _block: ASTBlock
        :return: a list of all expression in the block
        :rtype: list(ASTExpression)
        """
        if _block is None:
            return list()
        from pynestml.src.main.python.org.nestml.ast.ASTBlock import ASTBlock
        assert (_block is not None and isinstance(_block, ASTBlock)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of block provided (%s)!' % type(_block)
        ret = list()
        for stmt in _block.getStmts():
            if stmt.isSmallStmt():
                ret.extend(cls.collectExpressionsInSmallStmt(stmt.getSmallStmt()))
            else:
                ret.extend(cls.collectExpressionsInCompoundStmt(stmt.getCompoundStmt()))
        return ret

    @classmethod
    def collectExpressionsInCompoundStmt(cls, _stmt=None):
        """
        Collects all expressions in a compound expression.
        :param _stmt: a single compound statement.
        :type _stmt: ASTCompoundStmt
        :return: a list of all expressions in the compound statement.
        :rtype: list(ASTExpression)
        """
        if _stmt is None:
            return list()
        from pynestml.src.main.python.org.nestml.ast.ASTCompoundStmt import ASTCompoundStmt
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
        Collects all expressions in a compound expression.
        :param _stmt: a single small statement.
        :type _stmt: ASTSmallStmt
        :return: a list of all expressions in the compound statement.
        :rtype: list(ASTExpression)
        """
        if _stmt is None:
            return list()
        from pynestml.src.main.python.org.nestml.ast.ASTSmallStmt import ASTSmallStmt
        assert (_stmt is not None and isinstance(_stmt, ASTSmallStmt)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of statement provided (%s)!' % type(_stmt)
        ret = list()
        if _stmt.isAssignment():
            ret.append(_stmt.getAssignment().getExpression())
        elif _stmt.isDeclaration():
            if _stmt.getDeclaration().hasExpression():
                ret.append(_stmt.getDeclaration().getExpr())
            if _stmt.getDeclaration().hasInvariant():
                ret.append((_stmt.getDeclaration().getInvariant()))
        elif _stmt.isReturnStmt():
            if _stmt.getReturnStmt().hasExpr():
                ret.append(_stmt.getReturnStmt().getExpr())
        elif _stmt.isFunctionCall():
            if _stmt.getFunctionCall().hasArgs():
                ret.extend(_stmt.getFunctionCall().getArgs())
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
        from pynestml.src.main.python.org.nestml.ast.ASTIfStmt import ASTIfStmt
        assert (_stmt is not None and isinstance(_stmt, ASTIfStmt)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of statement provided (%s)!' % type(_stmt)
        ret = list()
        ret.append(_stmt.getIfClause().getCondition())
        ret.extend(cls.collectExpressionInBlock(_stmt.getIfClause().getBlock()))
        for clause in _stmt.getElifClauses():
            ret.append(clause.getCondition())
            ret.extend(cls.collectExpressionInBlock(clause.getBlock()))
        if _stmt.hasElseClause():
            ret.extend(cls.collectExpressionInBlock(_stmt.getElseClause().getBlock()))
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
        from pynestml.src.main.python.org.nestml.ast.ASTWhileStmt import ASTWhileStmt
        assert (_stmt is not None and isinstance(_stmt, ASTWhileStmt)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of statement provided (%s)!' % type(_stmt)
        ret = list()
        ret.append(_stmt.getCondition())
        ret.extend(cls.collectExpressionInBlock(_stmt.getBlock()))
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
        from pynestml.src.main.python.org.nestml.ast.ASTForStmt import ASTForStmt
        assert (_stmt is not None and isinstance(_stmt, ASTForStmt)), \
            '(PyNestML.Visitor.ExpressionCollector) No or wrong type of statement provided (%s)!' % type(_stmt)
        ret = list()
        ret.append(_stmt.getFrom())
        ret.append(_stmt.getTo())
        ret.extend(cls.collectExpressionInBlock(_stmt.getBlock()))
        return ret
