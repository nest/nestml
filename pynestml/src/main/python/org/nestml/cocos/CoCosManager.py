#
# CoCosManager.py
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
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron
from pynestml.src.main.python.org.nestml.cocos.CoCoFunctionUnique import CoCoFunctionUnique
from pynestml.src.main.python.org.nestml.cocos.CoCoEachBlockUniqueAndDefined import CoCoEachBlockUniqueAndDefined
from pynestml.src.main.python.org.nestml.cocos.CoCoFunctionCallsConsistent import CoCoFunctionCallsConsistent
from pynestml.src.main.python.org.nestml.cocos.CoCoAllVariablesDefined import CoCoAllVariablesDefined


class CoCosManager(object):
    """
    This class is used to ensure that a handed over list of cocos holds.
    """
    __functionDefinedUniquely = None
    __eachBlockUniqueAndDefined = None
    __functionCallDefinedAndTyped = None
    __variablesUnique = None

    @classmethod
    def initializeCoCosManager(cls):
        """
        Initializes the coco manager and initializes all individual cocos as function objects.
        """
        cls.__functionDefinedUniquely = CoCoFunctionUnique.checkCoCo
        cls.__eachBlockUniqueAndDefined = CoCoEachBlockUniqueAndDefined.checkCoCo
        cls.__functionCallDefinedAndTyped = CoCoFunctionCallsConsistent.checkCoCo
        cls.__variablesUnique = CoCoAllVariablesDefined.checkCoCo
        return

    @classmethod
    def checkCocos(cls, _neuron):
        """
        Checks for the handle over neuron, consisting of a AST and the corresponding symbol table, whether all currently
        active cocos hold or not. It is is left to the cocos to take correct, further processes, i.e., either stating
        a simple error message or terminate with an exception.
        :param _neuron: the neuron instance to check.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.checkEachBlockUniqueAndDefined(_neuron)
        cls.checkFunctionDefined(_neuron)
        cls.checkFunctionDeclaredAndCorrectlyTyped(_neuron)
        cls.checkVariablesUniqueInScope(_neuron)
        return

    @classmethod
    def checkFunctionDefined(cls, _neuron=None):
        """
        Checks for the handed over neuron that each used function it is defined.
        
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__functionDefinedUniquely(_neuron)
        return

    @classmethod
    def checkEachBlockUniqueAndDefined(cls, _neuron=None):
        """
        Checks if in the handed over neuron each block ist defined at most once and mandatory blocks are defined.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__eachBlockUniqueAndDefined(_neuron)
        return

    @classmethod
    def checkFunctionDeclaredAndCorrectlyTyped(cls, _neuron=None):
        """
        Checks if in the handed over neuron all function calls use existing functions and the argumets are 
        correctly typed.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__functionCallDefinedAndTyped(_neuron)
        return

    @classmethod
    def checkVariablesUniqueInScope(cls, _neuron=None):
        """
        Checks that all variables have been declared at most once per scope.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__variablesUnique(_neuron)
        return
