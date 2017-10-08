#
# SymPySolver.py
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
from pynestml.nestml.ASTEquationsBlock import ASTEquationsBlock
from pynestml.solver.SolverInput import SolverInput
from pynestml.solver.OdeAnalyzer import OdeAnalyzer
from pynestml.solver.SolverOutput import SolverOutput


class SymPySolver(object):
    """
    This class represents a collection of concepts as used to solve equations.
    """

    @classmethod
    def solveOdeWithShapes(self, _odeDeclaration=None):
        """
        Solves the odes for the handed over declarations block.
        :param _odeDeclaration: a single block of declarations.
        :type _odeDeclaration: ASTEquationsBlock
        :return: the output of the solver
        :rtype: SolverOutput
        """
        inputProcessor = SolverInput()
        inputJSON = inputProcessor.SolverInputComplete(_odeDeclaration)
        output = OdeAnalyzer.compute_solution(inputJSON.toJSON())
        toOutput = SolverOutput()
        return toOutput.fromJSON(output)
