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
from pynestml.src.main.python.org.nestml.cocos.CoCoVariableOncePerScope import CoCoVariableOncePerScope
from pynestml.src.main.python.org.nestml.cocos.CoCoFunctionHaveRhs import CoCoFunctionHaveRhs
from pynestml.src.main.python.org.nestml.cocos.CoCoFunctionMaxOneLhs import CoCoFunctionMaxOneLhs
from pynestml.src.main.python.org.nestml.cocos.CoCoBufferNotAssigned import CoCoBufferNotAssigned
from pynestml.src.main.python.org.nestml.cocos.CoCoCorrectOrderInEquation import CoCoCorrectOrderInEquation
from pynestml.src.main.python.org.nestml.cocos.CoCoCorrectNumeratorOfUnit import CoCoCorrectNumeratorOfUnit
from pynestml.src.main.python.org.nestml.cocos.CoCoNeuronNameUnique import CoCoNeuronNameUnique
from pynestml.src.main.python.org.nestml.cocos.CoCoNoNestNameSpaceCollision import CoCoNoNestNameSpaceCollision
from pynestml.src.main.python.org.nestml.cocos.CoCoTypeOfBufferUnique import CoCoTypeOfBufferUnique
from pynestml.src.main.python.org.nestml.cocos.CoCoParametersAssignedOnlyInParameterBlock import \
    CoCoParametersAssignedOnlyInParameterBlock
from pynestml.src.main.python.org.nestml.cocos.CoCoCurrentBuffersNotSpecified import CoCoCurrentBuffersNotSpecified
from pynestml.src.main.python.org.nestml.cocos.CoCoOnlySpikeBufferDatatypes import CoCoOnlySpikeBufferDatatypes
from pynestml.src.main.python.org.nestml.cocos.CoCoInitVarsWithOdesProvided import CoCoInitVarsWithOdesProvided
from pynestml.src.main.python.org.nestml.cocos.CoCoUserDefinedFunctionCorrectlyDefined import \
    CoCoUserDefinedFunctionCorrectlyDefined
from pynestml.src.main.python.org.nestml.cocos.CoCoEquationsOnlyForInitValues import CoCoEquationsOnlyForInitValues
from pynestml.src.main.python.org.nestml.cocos.CoCoConvolveCondCorrectlyBuilt import CoCoConvolveCondCorrectlyBuilt
from pynestml.src.main.python.org.nestml.cocos.CoCoNoShapesExceptInConvolve import CoCoNoShapesExceptInConvolve
from pynestml.src.main.python.org.nestml.cocos.CoCoNoTwoNeuronsInSetOfCompilationUnits import \
    CoCoNoTwoNeuronsInSetOfCompilationUnits
from pynestml.src.main.python.org.nestml.cocos.CoCoInvariantIsBoolean import CoCoInvariantIsBoolean


class CoCosManager(object):
    """
    This class is used to ensure that a handed over list of cocos holds.
    """
    __functionDefinedUniquely = None
    __eachBlockUniqueAndDefined = None
    __functionCallDefinedAndTyped = None
    __variablesUnique = None
    __variablesDefinedBeforeUsage = None
    __functionsHaveRhs = None
    __functionsHaveMaxOneLhs = None
    __noValuesAssignedToBuffers = None
    __orderOfEquationsCorrect = None
    __numeratorOfUnitIsOne = None
    __multipleNeuronsWithSameName = None
    __nestNameSpaceCollision = None
    __bufferTypesDefinedUniquely = None
    __parametersNotAssignedOutsideCorrespondingBlock = None
    __currentBuffersNotSpecified = None
    __buffersDatatypeCorrect = None
    __initialValuesCorrect = None
    __returnStmtCorrect = None
    __equationsOnlyForInits = None
    __convolveCorrectlyBuilt = None
    __noShapesExceptInConvolve = None
    __noCollisionAcrossUnits = None
    __invariantCorrectlyTyped = None

    @classmethod
    def initializeCoCosManager(cls):
        """
        Initializes the coco manager and initializes all individual cocos as function objects.
        """
        cls.__functionDefinedUniquely = CoCoFunctionUnique.checkCoCo
        cls.__eachBlockUniqueAndDefined = CoCoEachBlockUniqueAndDefined.checkCoCo
        cls.__functionCallDefinedAndTyped = CoCoFunctionCallsConsistent.checkCoCo
        cls.__variablesUnique = CoCoVariableOncePerScope.checkCoCo
        cls.__variablesDefinedBeforeUsage = CoCoAllVariablesDefined.checkCoCo
        cls.__functionsHaveRhs = CoCoFunctionHaveRhs.checkCoCo
        cls.__functionsHaveMaxOneLhs = CoCoFunctionMaxOneLhs.checkCoCo
        cls.__noValuesAssignedToBuffers = CoCoBufferNotAssigned.checkCoCo
        cls.__orderOfEquationsCorrect = CoCoCorrectOrderInEquation.checkCoCo
        cls.__numeratorOfUnitIsOne = CoCoCorrectNumeratorOfUnit.checkCoCo
        cls.__multipleNeuronsWithSameName = CoCoNeuronNameUnique.checkCoCo
        cls.__nestNameSpaceCollision = CoCoNoNestNameSpaceCollision.checkCoCo
        cls.__bufferTypesDefinedUniquely = CoCoTypeOfBufferUnique.checkCoCo
        cls.__parametersNotAssignedOutsideCorrespondingBlock = CoCoParametersAssignedOnlyInParameterBlock.checkCoCo
        cls.__currentBuffersNotSpecified = CoCoCurrentBuffersNotSpecified.checkCoCo
        cls.__buffersDatatypeCorrect = CoCoOnlySpikeBufferDatatypes.checkCoCo
        cls.__initialValuesCorrect = CoCoInitVarsWithOdesProvided.checkCoCo
        cls.__returnStmtCorrect = CoCoUserDefinedFunctionCorrectlyDefined.checkCoCo
        cls.__equationsOnlyForInits = CoCoEquationsOnlyForInitValues.checkCoCo
        cls.__convolveCorrectlyBuilt = CoCoConvolveCondCorrectlyBuilt.checkCoCo
        cls.__noShapesExceptInConvolve = CoCoNoShapesExceptInConvolve.checkCoCo
        cls.__noCollisionAcrossUnits = CoCoNoTwoNeuronsInSetOfCompilationUnits.checkCoCo
        cls.__invariantCorrectlyTyped = CoCoInvariantIsBoolean.checkCoCo
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
        cls.checkFunctionDefined(_neuron)
        cls.checkFunctionDeclaredAndCorrectlyTyped(_neuron)
        cls.checkVariablesUniqueInScope(_neuron)
        cls.checkVariablesDefinedBeforeUsage(_neuron)
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

    @classmethod
    def checkVariablesDefinedBeforeUsage(cls, _neuron=None):
        """
        Checks that all variables are defined before being used.
        :param _neuron: a single neuron.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__variablesDefinedBeforeUsage(_neuron)
        return

    @classmethod
    def checkFunctionsHaveRhs(cls, _neuron=None):
        """
        Checks that all functions have a right-hand side, e.g., function V_reset mV = V_m - 55mV 
        :param _neuron: a single neuron object
        :type _neuron: ASTNeuron 
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__functionsHaveRhs(_neuron)
        return

    @classmethod
    def checkFunctionHasMaxOneLhs(cls, _neuron=None):
        """
        Checks that all functions have exactly one left-hand side, e.g., function V_reset mV = V_m - 55mV 
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__functionsHaveMaxOneLhs(_neuron)
        return

    @classmethod
    def checkNoValuesAssignedToBuffers(cls, _neuron=None):
        """
        Checks that no values are assigned to buffers.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__noValuesAssignedToBuffers(_neuron)
        return

    @classmethod
    def checkOrderOfEquationsCorrect(cls, _neuron=None):
        """
        Checks that all equations specify the order of the variable.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__orderOfEquationsCorrect(_neuron)
        return

    @classmethod
    def checkNumeratorOfUnitIsOneIfNumeric(cls, _neuron=None):
        """
        Checks that all units which have a numeric numerator use 1.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__numeratorOfUnitIsOne(_neuron)
        return

    @classmethod
    def checkNeuronNamesUnique(cls, _compilationUnit=None):
        """
        Checks that all declared neurons in a compilation unit have a unique name.
        :param _compilationUnit: a single compilation unit.
        :type _compilationUnit: ASTCompilationUnit
        """
        from pynestml.src.main.python.org.nestml.ast.ASTNESTMLCompilationUnit import ASTNESTMLCompilationUnit
        assert (_compilationUnit is not None and isinstance(_compilationUnit, ASTNESTMLCompilationUnit)), \
            '(PyNestML.CoCo.Manager) No or wrong type of compilation unit provided (%s)!' % type(_compilationUnit)
        cls.__multipleNeuronsWithSameName(_compilationUnit)
        return

    @classmethod
    def checkNoNestNamespaceCollisions(cls, _neuron=None):
        """
        Checks that all units which have a numeric numerator use 1.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__nestNameSpaceCollision(_neuron)
        return

    @classmethod
    def checkTypeOfBufferUnique(cls, _neuron=None):
        """
        Checks that all spike buffers have a unique type, i.e., no buffer is defined with redundant keywords.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__bufferTypesDefinedUniquely(_neuron)
        return

    @classmethod
    def checkParametersNotAssignedOutsideParametersBlock(cls, _neuron=None):
        """
        Checks that parameters are not assigned outside the parameters block.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__parametersNotAssignedOutsideCorrespondingBlock(_neuron)
        return

    @classmethod
    def checkCurrentBuffersNoKeywords(cls, _neuron=None):
        """
        Checks that input current buffers have not been specified with keywords, e.g., inhibitory.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__currentBuffersNotSpecified(_neuron)
        return

    @classmethod
    def checkBufferTypesAreCorrect(cls, _neuron=None):
        """
        Checks that input buffers have specified the data type if required an no data type if not allowed.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__buffersDatatypeCorrect(_neuron)
        return

    @classmethod
    def checkInitVarsWithOdesProvided(cls, _neuron=None):
        """
        Checks that all initial variables have a rhs and are provided with the corresponding ode declaration.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__initialValuesCorrect(_neuron)
        return

    @classmethod
    def checkUserDefinedFunctionCorrectlyBuilt(cls, _neuron=None):
        """
        Checks that all user defined functions are correctly constructed, i.e., have a return statement if declared
        and that the type corresponds to the declared one.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__returnStmtCorrect(_neuron)
        return

    @classmethod
    def checkInitialOdeInitialValues(cls, _neuron=None):
        """
        Checks if variables of odes are declared in the initial_values block.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__equationsOnlyForInits(_neuron)
        return

    @classmethod
    def checkConvolveCondCurrIsCorrect(cls, _neuron=None):
        """
        Checks if all convolve/curr_sum/cond_sum expression are correctly provided with arguments.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__convolveCorrectlyBuilt(_neuron)
        return

    @classmethod
    def checkCorrectUsageOfShapes(cls, _neuron=None):
        """
        Checks if all shapes are only used in cond_sum, cur_sum, convolve.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__noShapesExceptInConvolve(_neuron)
        return

    @classmethod
    def checkNotTwoNeuronsAcrossUnits(cls, _compilationUnits=list()):
        """
        Checks if in a set of compilation units, two neurons have the same name.
        :param _compilationUnits: a  list of compilation units
        :type _compilationUnits: list(ASTNESTMLCompilationUnit)
        """
        assert (_compilationUnits is not None and isinstance(_compilationUnits, list)), \
            '(PyNestML.CoCo.Manager) No or wrong type of compilation unit provided (%s)!' % type(list)
        cls.__noCollisionAcrossUnits(_compilationUnits)
        return

    @classmethod
    def checkInvariantTypeCorrect(cls, _neuron=None):
        """
        Checks if all invariants are of type boolean
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__invariantCorrectlyTyped(_neuron)
        return

    @classmethod
    def postSymbolTableBuilderChecks(cls, _neuron=None):
        """
        Checks the following constraints:
            cls.checkFunctionDefined(_neuron)
            cls.checkFunctionDeclaredAndCorrectlyTyped(_neuron)
            cls.checkVariablesUniqueInScope(_neuron)
            cls.checkVariablesDefinedBeforeUsage(_neuron)
            cls.checkFunctionsHaveRhs(_neuron)
            cls.checkFunctionHasMaxOneLhs(_neuron)
            cls.checkNoValuesAssignedToBuffers(_neuron)
            cls.checkOrderOfEquationsCorrect(_neuron)
            cls.checkNumeratorOfUnitIsOneIfNumeric(_neuron)
            cls.checkNoNestNamespaceCollisions(_neuron)
            cls.checkTypeOfBufferUnique(_neuron)
            cls.checkParametersNotAssignedOutsideParametersBlock(_neuron)
            cls.checkCurrentBuffersNoKeywords(_neuron)
            cls.checkBufferTypesAreCorrect(_neuron)
            cls.checkUsedDefinedFunctionCorrectlyBuilt(_neuron)
            cls.checkInitialOdeInitialValues(_neuron)
            cls.checkInvariantTypeCorrect(_neuron)
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        cls.checkFunctionDefined(_neuron)
        cls.checkFunctionDeclaredAndCorrectlyTyped(_neuron)
        cls.checkVariablesUniqueInScope(_neuron)
        cls.checkVariablesDefinedBeforeUsage(_neuron)
        cls.checkFunctionsHaveRhs(_neuron)
        cls.checkFunctionHasMaxOneLhs(_neuron)
        cls.checkNoValuesAssignedToBuffers(_neuron)
        cls.checkOrderOfEquationsCorrect(_neuron)
        cls.checkNumeratorOfUnitIsOneIfNumeric(_neuron)
        cls.checkNoNestNamespaceCollisions(_neuron)
        cls.checkTypeOfBufferUnique(_neuron)
        cls.checkParametersNotAssignedOutsideParametersBlock(_neuron)
        cls.checkCurrentBuffersNoKeywords(_neuron)
        cls.checkBufferTypesAreCorrect(_neuron)
        cls.checkUserDefinedFunctionCorrectlyBuilt(_neuron)
        cls.checkInitialOdeInitialValues(_neuron)
        cls.checkConvolveCondCurrIsCorrect(_neuron)
        cls.checkCorrectUsageOfShapes(_neuron)
        cls.checkInvariantTypeCorrect(_neuron)
        return

    @classmethod
    def postOdeSpecificationChecks(cls, _neuron=None):
        """
        Checks the following constraints:
            cls.checkInitVarsWithOdesProvided
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        cls.checkInitVarsWithOdesProvided(_neuron)
        return
