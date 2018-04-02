#
# SolverInput.py
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
from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
from pynestml.utils.OdeTransformer import OdeTransformer
from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter
from copy import deepcopy


class SolverInput(object):
    """
    Captures the ODE block for the processing in the SymPy. Generates corresponding json representation.
    """
    __functions = None
    __shapes = None
    __ode = None
    __printer = None

    def __init__(self):
        """
        Standard constructor.
        """
        self.__printer = ExpressionsPrettyPrinter()
        return

    def SolverInputComplete(self, _equationsBlock=None):
        """
        Standard constructor providing the basic functionality to transform equation blocks to json format.
        :param _equationsBlock: a single equation block.
        :type _equationsBlock: ASTEquationsBlock
        """
        assert (_equationsBlock is not None and isinstance(_equationsBlock, ASTEquationsBlock)), \
            '(PyNestML.Solver.Input) No or wrong type of equations block provided (%s)!' % _equationsBlock
        workingCopy = OdeTransformer.replaceSumCalls(deepcopy(_equationsBlock))
        self.__ode = self.printEquation(workingCopy.getOdeEquations()[0])
        self.__functions = list()
        for func in workingCopy.getOdeFunctions():
            self.__functions.append(self.printFunction(func))

        self.__shapes = list()
        for shape in workingCopy.getOdeShapes():
            self.__shapes.append(self.printShape(shape))
        return self

    def SolverInputShapes(self, _shapes=None):
        """
        The same functionality as in the case of SolverInputComplete, but now only shapes are solved
        :param _shapes: a list of shapes
        :type _shapes: list(ASTOdeShape)
        """
        self.__shapes = list()
        for shape in _shapes:
            self.__shapes.append(self.printShape(shape))
        self.__ode = None
        self.__functions = list()
        return self

    def printEquation(self, _equation=None):
        """
        Prints an equation to a processable format.
        :param _equation: a single equation
        :type _equation: ASTOdeEquation
        :return: the corresponding string representation
        :rtype: str
        """
        assert (_equation is not None and isinstance(_equation, ASTOdeEquation)), \
            '(PyNestML.Solver.Input) No or wrong type of equation provided (%s)!' % type(_equation)
        return _equation.get_lhs().get_complete_name() + ' = ' + self.__printer.printExpression(_equation.get_rhs())

    def printShape(self, _shape=None):
        """
        Prints a single shape to a processable format.
        :param _shape: a single shape
        :type _shape: ASTOdeShape
        :return: the corresponding string representation
        :rtype: str
        """
        assert (_shape is not None and isinstance(_shape, ASTOdeShape)), \
            '(PyNestML.Solver.Input) No or wrong type of shape provided (%s)!' % type(_shape)
        return _shape.get_variable().get_complete_name() + ' = ' \
               + self.__printer.printExpression(_shape.get_expression())

    def printFunction(self, _function=None):
        """
        Prints a single function to a processable format.
        :param _function: a single function
        :type _function: ASTOdeFunction
        :return: the corresponding string representation
        :rtype: str
        """
        assert (_function is not None and isinstance(_function, ASTOdeFunction)), \
            '(PyNestML.Solver.Input) No or wrong type of function provided (%s)!' % type(_function)
        return _function.get_variable_name() + ' = ' + self.__printer.printExpression(_function.get_expression())

    def toJSON(self):
        """
        Returns a json format string of all currently stored shapes,functions and equations.
        :return: a string representation.
        :rtype: str
        """
        temp = '{'
        if self.__ode is not None:
            temp += '"ode":"' + self.__ode + '",'
        else:
            temp += '"ode": null,'
        temp += '"shapes":['
        for shape in self.__shapes:
            temp += '"' + shape + '",'
        if len(self.__shapes) > 0:
            temp = temp[:-1]
        temp += '], "functions":['
        for func in self.__functions:
            temp += '"' + func + '",'
        if len(self.__functions) > 0:
            temp = temp[:-1]
        return temp + ']}'
