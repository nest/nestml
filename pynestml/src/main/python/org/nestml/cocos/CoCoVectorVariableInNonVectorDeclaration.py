#
# CoCoVectorVariableInNonVectorDeclaration.py
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
from pynestml.src.main.python.org.nestml.cocos.CoCo import CoCo
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron
from pynestml.src.main.python.org.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind


class CoCoVectorVariableInNonVectorDeclaration(CoCo):
    """
    This coco ensures that vector variables are not used in non vector declarations.
    Not allowed:
        function three integer[n] = 3
        threePlusFour integer = three + 4 <- error: threePlusFour is not a vector
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.BufferNotAssigned) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(VectorInDeclarationVisitor())
        return


class VectorInDeclarationVisitor(NESTMLVisitor):
    """
    This visitor checks if somewhere in a declaration of a non vector value, a vector is used.
    """

    def visitDeclaration(self, _declaration=None):
        """
        Checks the coco.
        :param _declaration: a single declaration.
        :type _declaration: ASTDeclaration
        """
        if _declaration.hasExpression():
            variables = _declaration.getExpr().getVariables()
            for variable in variables:
                if variable is not None:
                    symbol = _declaration.getScope().resolveToSymbol(variable.getCompleteName(), SymbolKind.VARIABLE)
                    if symbol is not None and symbol.hasVectorParameter() and not _declaration.hasSizeParameter():
                        Logger.logMessage(
                            'Vector value "%s" used in a non-vector declaration of variables "%s" at %s!'
                            % (symbol.getSymbolName(),
                                list(var.getCompleteName() for var in _declaration.getVariables()),
                               _declaration.getSourcePosition().printSourcePosition()),
                            LOGGING_LEVEL.ERROR)
        return
