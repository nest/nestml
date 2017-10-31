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
from pynestml.nestml.CoCo import CoCo
from pynestml.nestml.ASTNeuron import ASTNeuron
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.Symbol import SymbolKind
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


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
    This visitor checks if somewhere in a declaration of a non-vector value, a vector is used.
    """

    def visitDeclaration(self, _declaration=None):
        """
        Checks the coco.
        :param _declaration: a single declaration.
        :type _declaration: ASTDeclaration
        """
        from pynestml.nestml.ASTDeclaration import ASTDeclaration
        assert (_declaration is not None and isinstance(_declaration, ASTDeclaration)), \
            '(PyNestML.CoCo.VectorInNonVectorDeclaration) No or wrong type of declaration provided (%s)!' % type(
                _declaration)
        if _declaration.hasExpression():
            variables = _declaration.getExpression().getVariables()
            for variable in variables:
                if variable is not None:
                    symbol = _declaration.getScope().resolveToSymbol(variable.getCompleteName(), SymbolKind.VARIABLE)
                    if symbol is not None and symbol.hasVectorParameter() and not _declaration.hasSizeParameter():
                        code, message = Messages.getVectorInNonVector(_vector=symbol.getSymbolName(),
                                                                      _nonVector=list(var.getCompleteName() for
                                                                                      var in
                                                                                      _declaration.getVariables()))

                        Logger.logMessage(_errorPosition=_declaration.getSourcePosition(),
                                          _code=code, _message=message,
                                          _logLevel=LOGGING_LEVEL.ERROR)
        return
