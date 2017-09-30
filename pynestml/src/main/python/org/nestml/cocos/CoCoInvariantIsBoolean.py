#
# CoCoInvariantIsBoolean.py
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
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedTypes import PredefinedTypes
from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor


class CoCoInvariantIsBoolean(CoCo):
    """
    This coco checks that all invariants are of type boolean

    """
    neuronName = None

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.BufferNotAssigned) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.neuronName = _neuron.getName()
        visitor = InvariantTypeVisitor()
        _neuron.accept(visitor)
        return


class InvariantTypeVisitor(NESTMLVisitor):
    """
    Checks if for each invariant, the type is boolean.
    """

    def visitDeclaration(self, _declaration=None):
        """
        Checks the coco for a declaration.
        :param _declaration: a single declaration.
        :type _declaration: ASTDeclaration
        """
        if _declaration.hasInvariant():
            #todo
            return
            invariantType = _declaration.getInvariant().getTypeEither()
            if invariantType is None or invariantType.isError():
                Logger.logMessage(
                    '[' + CoCoInvariantIsBoolean.neuronName + '.nestml] Type of invariant "%s" at %s not derivable!'
                    % (
                        _declaration.getInvariant().printAST(),
                        _declaration.getInvariant().getSourcePosition().printSourcePosition()),
                    LOGGING_LEVEL.ERROR)
            elif not invariantType.getValue().equals(PredefinedTypes.getBooleanType()):
                Logger.logMessage(
                    '[' + CoCoInvariantIsBoolean.neuronName + '.nestml] Type of invariant "%s" at %s wrong! '
                                                              'Expected boolean, got %s'
                    % (
                        _declaration.getInvariant().printAST(),
                        _declaration.getInvariant().getSourcePosition().printSourcePosition(),
                        invariantType.getValue().printSymbol()),
                    LOGGING_LEVEL.ERROR)

        return
