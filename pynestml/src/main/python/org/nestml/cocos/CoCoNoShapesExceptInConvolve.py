#
# CoCoNoShapesExceptInConvolve.py
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
from pynestml.src.main.python.org.nestml.ast.ASTOdeShape import ASTOdeShape
from pynestml.src.main.python.org.nestml.ast.ASTFunctionCall import ASTFunctionCall
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind


class CoCoNoShapesExceptInConvolve(CoCo):
    """
    This CoCo ensures that shape variables do not occur on the right hand side except in convolve/curr_sum and
    cond_sum.
    Allowed:
        shape g_ex ...
        function I_syn_exc pA = cond_sum(g_ex, spikeExc) * ( V_m - E_ex )

    Not allowed
        shape g_ex ...
        function I_syn_exc pA = g_ex * ( V_m - E_ex )

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
        shapeCollectorVisitor = ShapeCollectingVisitor()
        shapeNames = shapeCollectorVisitor.collectShapes(_neuron=_neuron)
        shapeUsageVisitor = ShapeUsageVisitor(_shapes=shapeNames)
        shapeUsageVisitor.workOn(_neuron)
        return


class ShapeUsageVisitor(NESTMLVisitor):
    __shapes = None
    __neuronNode = None

    def __init__(self, _shapes=None):
        """
        Standard constructor.
        :param _shapes: a list of shapes.
        :type _shapes: list(ASTOdeShape)
        """
        super(ShapeUsageVisitor, self).__init__()
        self.__shapes = _shapes
        return

    def workOn(self, _neuron=None):
        self.__neuronNode = _neuron
        _neuron.accept(self)
        return

    def visitVariable(self, _variable=None):
        """
        Visits each shape and checks if it is used correctly.
        :param _variable: a single node.
        :type _variable: AST_
        """
        for shapeName in self.__shapes:
            # in order to allow shadowing by local scopes, we first check if the element has been declared locally
            symbol = _variable.getScope().resolveToSymbol(shapeName, SymbolKind.VARIABLE)
            # if it is not a shape just continue
            if not symbol.isShape():
                continue
            if _variable.getCompleteName() == shapeName:
                parent = self.__neuronNode.getParent(_variable)
                if parent is not None:
                    if isinstance(parent, ASTOdeShape):
                        continue
                    grandparent = self.__neuronNode.getParent(parent)
                    if grandparent is not None and isinstance(grandparent, ASTFunctionCall):
                        grandparentFuncName = grandparent.getName()
                        if grandparentFuncName == 'curr_sum' or grandparentFuncName == 'cond_sum' or \
                                        grandparentFuncName == 'convolve':
                            continue
                Logger.logMessage(
                    'Shape "%s" used outside convolve at %s!'
                    % (shapeName, _variable.getSourcePosition().printSourcePosition()),
                    LOGGING_LEVEL.ERROR)
        return


class ShapeCollectingVisitor(NESTMLVisitor):
    __shapeNames = None

    def collectShapes(self, _neuron=None):
        """
        Collects all shapes in the model.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :return: a list of shapes.
        :rtype: list(str)
        """
        self.__shapeNames = list()
        _neuron.accept(self)
        return self.__shapeNames

    def visitOdeShape(self, _odeShape=None):
        """
        Collects the shape.
        :param _odeShape: a single shape node.
        :type _odeShape: ASTOdeShape
        """
        self.__shapeNames.append(_odeShape.getVariable().getCompleteName())
        return
