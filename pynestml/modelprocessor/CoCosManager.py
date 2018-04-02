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
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.CoCoFunctionUnique import CoCoFunctionUnique
from pynestml.modelprocessor.CoCoEachBlockUniqueAndDefined import CoCoEachBlockUniqueAndDefined
from pynestml.modelprocessor.CoCoFunctionCallsConsistent import CoCoFunctionCallsConsistent
from pynestml.modelprocessor.CoCoAllVariablesDefined import CoCoAllVariablesDefined
from pynestml.modelprocessor.CoCoVariableOncePerScope import CoCoVariableOncePerScope
from pynestml.modelprocessor.CoCoFunctionHaveRhs import CoCoFunctionHaveRhs
from pynestml.modelprocessor.CoCoFunctionMaxOneLhs import CoCoFunctionMaxOneLhs
from pynestml.modelprocessor.CoCoBufferNotAssigned import CoCoBufferNotAssigned
from pynestml.modelprocessor.CoCoCorrectOrderInEquation import CoCoCorrectOrderInEquation
from pynestml.modelprocessor.CoCoCorrectNumeratorOfUnit import CoCoCorrectNumeratorOfUnit
from pynestml.modelprocessor.CoCoNeuronNameUnique import CoCoNeuronNameUnique
from pynestml.modelprocessor.CoCoNoNestNameSpaceCollision import CoCoNoNestNameSpaceCollision
from pynestml.modelprocessor.CoCoTypeOfBufferUnique import CoCoTypeOfBufferUnique
from pynestml.modelprocessor.CoCoParametersAssignedOnlyInParameterBlock import CoCoParametersAssignedOnlyInParameterBlock
from pynestml.modelprocessor.CoCoCurrentBuffersNotSpecified import CoCoCurrentBuffersNotSpecified
from pynestml.modelprocessor.CoCoOnlySpikeBufferDatatypes import CoCoOnlySpikeBufferDatatypes
from pynestml.modelprocessor.CoCoInitVarsWithOdesProvided import CoCoInitVarsWithOdesProvided
from pynestml.modelprocessor.CoCoUserDefinedFunctionCorrectlyDefined import CoCoUserDefinedFunctionCorrectlyDefined
from pynestml.modelprocessor.CoCoEquationsOnlyForInitValues import CoCoEquationsOnlyForInitValues
from pynestml.modelprocessor.CoCoConvolveCondCorrectlyBuilt import CoCoConvolveCondCorrectlyBuilt
from pynestml.modelprocessor.CoCoNoShapesExceptInConvolve import CoCoNoShapesExceptInConvolve
from pynestml.modelprocessor.CoCoNoTwoNeuronsInSetOfCompilationUnits import CoCoNoTwoNeuronsInSetOfCompilationUnits
from pynestml.modelprocessor.CoCoInvariantIsBoolean import CoCoInvariantIsBoolean
from pynestml.modelprocessor.CoCoVectorVariableInNonVectorDeclaration import CoCoVectorVariableInNonVectorDeclaration
from pynestml.modelprocessor.CoCoSumHasCorrectParameter import CoCoSumHasCorrectParameter
from pynestml.modelprocessor.CoCoIllegalExpression import CoCoIllegalExpression


class CoCosManager(object):
    """
    This class is used to ensure that a handed over list of cocos holds.
    Attributes:
        __functionDefinedUniquely: This coco checks if each function is defined uniquely.
        __eachBlockUniqueAndDefined: This coco checks if each block is defined correctly.
        __functionCallDefinedAndTyped: This coco checks if all function calls are correctly defined.
        __variablesUnique: This coco checks if all variables are uniquely defined.
        __variablesDefinedBeforeUsage: This coco checks if all variables are defined before usage.
        __functionsHaveRhs: This coco checks if all function declarations have a rhs.
        __functionsHaveMaxOneLhs: This coco checks that all functions have exactly one lhs.
        __noValuesAssignedToBuffers: This coco checks that no values are assigned to buffers.
        __orderOfEquationsCorrect: This coco checks that orders of equations are correct.
        __numeratorOfUnitIsOne: This coco checks that the numerator of units is 1.
        __multipleNeuronsWithSameName: This coco checks if no two neurons with the same name are processed.
        __nestNameSpaceCollision: This coco checks that there are no collisions with NEST namespace.
        __bufferTypesDefinedUniquely: This coco checks if buffer keyword are not redundant.
        __parametersNotAssignedOutsideCorrespondingBlock: This coco checks that no parameters are assigned outside
                                                            the parameters block.
        __currentBuffersNotSpecified: This coco checks current buffers are not specified with a type.
        __buffersDatatypeCorrect: This coco checks that data types for buffers are correctly stated.
        __initialValuesCorrect: This coco checks that all initial values are correctly defined.
        __returnStmtCorrect: This coco checks tha all return statements in user defined function are correctly stated.
        __equationsOnlyForInits: This coco checks that equitation are only given for variables in the initial values
                                block.
        __convolveCorrectlyBuilt: This coco checks that the convolve rhs is correctly typed.
        __noShapesExceptInConvolve: This coco checks that shapes are only used inside convolve expressions.
        __noCollisionAcrossUnits: This coco checks that no collision of types occurs.
        __invariantCorrectlyTyped: This coco checks that invariants are correctly typed.
        __vectorInNonVectorDetected: This coco checks that no vectors are used in non-vector declaration.
        __sumIsCorrect: This coco checks that sum rhs are correctly used.
        __expressionCorrect: This checks that types of rhs etc. are correctly stated.
    """
    __functionDefinedUniquely = CoCoFunctionUnique.checkCoCo
    __eachBlockUniqueAndDefined = CoCoEachBlockUniqueAndDefined.checkCoCo
    __functionCallDefinedAndTyped = CoCoFunctionCallsConsistent.checkCoCo
    __variablesUnique = CoCoVariableOncePerScope.checkCoCo
    __variablesDefinedBeforeUsage = CoCoAllVariablesDefined.checkCoCo
    __functionsHaveRhs = CoCoFunctionHaveRhs.checkCoCo
    __functionsHaveMaxOneLhs = CoCoFunctionMaxOneLhs.checkCoCo
    __noValuesAssignedToBuffers = CoCoBufferNotAssigned.checkCoCo
    __orderOfEquationsCorrect = CoCoCorrectOrderInEquation.checkCoCo
    __numeratorOfUnitIsOne = CoCoCorrectNumeratorOfUnit.checkCoCo
    __multipleNeuronsWithSameName = CoCoNeuronNameUnique.checkCoCo
    __nestNameSpaceCollision = CoCoNoNestNameSpaceCollision.checkCoCo
    __bufferTypesDefinedUniquely = CoCoTypeOfBufferUnique.checkCoCo
    __parametersNotAssignedOutsideCorrespondingBlock = CoCoParametersAssignedOnlyInParameterBlock.checkCoCo
    __currentBuffersNotSpecified = CoCoCurrentBuffersNotSpecified.checkCoCo
    __buffersDatatypeCorrect = CoCoOnlySpikeBufferDatatypes.checkCoCo
    __initialValuesCorrect = CoCoInitVarsWithOdesProvided.checkCoCo
    __returnStmtCorrect = CoCoUserDefinedFunctionCorrectlyDefined.checkCoCo
    __equationsOnlyForInits = CoCoEquationsOnlyForInitValues.checkCoCo
    __convolveCorrectlyBuilt = CoCoConvolveCondCorrectlyBuilt.checkCoCo
    __noShapesExceptInConvolve = CoCoNoShapesExceptInConvolve.checkCoCo
    __noCollisionAcrossUnits = CoCoNoTwoNeuronsInSetOfCompilationUnits.checkCoCo
    __invariantCorrectlyTyped = CoCoInvariantIsBoolean.checkCoCo
    __vectorInNonVectorDetected = CoCoVectorVariableInNonVectorDeclaration.checkCoCo
    __sumIsCorrect = CoCoSumHasCorrectParameter.checkCoCo
    __expressionCorrect = CoCoIllegalExpression.checkCoCo

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
        from pynestml.modelprocessor.ASTNestMLCompilationUnit import ASTNestMLCompilationUnit
        assert (_compilationUnit is not None and isinstance(_compilationUnit, ASTNestMLCompilationUnit)), \
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
        Checks if all convolve/curr_sum/cond_sum rhs are correctly provided with arguments.
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
        :type _compilationUnits: list(ASTNestMLCompilationUnit)
        """
        assert (_compilationUnits is not None and isinstance(_compilationUnits, list)), \
            '(PyNestML.CoCo.Manager) No or wrong type of compilation unit provided (%s)!' % type(list)
        cls.__noCollisionAcrossUnits(_compilationUnits)
        return

    @classmethod
    def checkInvariantTypeCorrect(cls, _neuron=None):
        """
        Checks if all invariants are of type boolean.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__invariantCorrectlyTyped(_neuron)
        return

    @classmethod
    def checkVectorInNonVectorDeclarationDetected(cls, _neuron=None):
        """
        Checks if no declaration a vector value is added to a non vector one.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__vectorInNonVectorDetected(_neuron)
        return

    @classmethod
    def checkSumHasCorrectParameter(cls, _neuron=None):
        """
        Checks that all cond_sum,cur_sum and convolve have variables as arguments.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__sumIsCorrect(_neuron)
        return

    @classmethod
    def checkExpressionCorrect(cls, _neuron=None):
        """
        Checks that all rhs in the model are correctly constructed, e.g. type(lhs)==type(rhs).
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__expressionCorrect(_neuron)
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
            cls.checkVectorInNonVectorDeclarationDetected(_neuron)
            cls.checkSumHasCorrectParameter(_neuron)
            cls.checkExpressionCorrect(_neuron)
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
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
        cls.checkVectorInNonVectorDeclarationDetected(_neuron)
        cls.checkSumHasCorrectParameter(_neuron)
        cls.checkExpressionCorrect(_neuron)
        return

    @classmethod
    def postOdeSpecificationChecks(cls, _neuron=None):
        """
        Checks the following constraints:
            cls.checkInitVarsWithOdesProvided
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.Manager) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.checkInitVarsWithOdesProvided(_neuron)
        return
