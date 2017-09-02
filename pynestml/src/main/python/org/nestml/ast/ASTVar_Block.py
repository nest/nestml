"""
/*
 *  ASTVar_Block.py
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
@author kperun
"""


class ASTVar_Block:
    """
    This class is used to store a block of variable declarations.
    ASTVar_Block represent a block with variables, e.g.:
        state:
          y0, y1, y2, y3 mV [y1 > 0; y2 > 0]
        end

    @attribute state true if the varblock is a state.
    @attribute parameter true if the varblock is a parameter.
    @attribute internal true if the varblock is a state internal.
    @attribute AliasDecl a list with variable declarations
    Grammar:
        var_Block:
            ('state'|'parameters'|'internals')
            BLOCK_OPEN
              (declaration | NEWLINE)*
            BLOCK_CLOSE;
    """
    __isState = False
    __isParameters = False
    __isInternals = False
    __declarations = None

    def __init__(self, _isState, _isParameters=False, _isInternals=False, _declarations=list()):
        """
        Standard constructor.
        :param _isState: is a state block.
        :type _isState: bool
        :param _isParameters: is a parameter block.
        :type _isParameters: bool 
        :param _isInternals: is an internals block.
        :type _isInternals: bool
        :param _declarations: a list of declarations.
        :type _declarations: list(ASTDeclaration)
        """
        self.__declarations = _declarations
        self.__isInternals = _isInternals
        self.__isParameters = _isParameters
        self.__isState = _isState

    @classmethod
    def makeASTVar_Block(cls, _isState=False, _isParameters=False, _isInternals=False, _declarations=list()):
        """
        Factory method of the ASTVar_Block class.
        :param _isState: is a state block.
        :type _isState: bool
        :param _isParameters: is a parameter block.
        :type _isParameters: bool 
        :param _isInternals: is an internals block.
        :type _isInternals: bool
        :param _declarations: a list of declarations.
        :type _declarations: list(ASTDeclaration)
        :return: a new variable block object.
        :rtype: ASTVar_Block 
        """
        assert (_isInternals or _isParameters or _isState), '(PyNESTML.AST) Type of variable block not specified.'
        return cls(_isState, _isParameters, _isInternals, _declarations)

    def isState(self):
        """
        Returns whether it is a state block or not.
        :return: True if state block, otherwise False.
        :rtype: bool
        """
        return self.__isState

    def isParameters(self):
        """
        Returns whether it is a parameters block or not.
        :return: True if parameters block, otherwise False.
        :rtype: bool
        """
        return self.__isParameters

    def isInternals(self):
        """
        Returns whether it is an internals block or not.
        :return: True if internals block, otherwise False.
        :rtype: bool
        """
        return self.__isInternals

    def getDeclarations(self):
        """
        Returns the set of stored declarations.
        :return: set of declarations
        :rtype: set(ASTDeclaration)
        """
        return self.__declarations

    def printAST(self):
        """
        Returns a string representation of the variable block.
        :return: a string representation
        :rtype: str
        """
        ret = ''
        if self.isState():
            ret += 'state'
        elif self.isParameters():
            ret += 'parameters'
        else:
            ret += 'internals'
        ret += ':\n'
        if self.getDeclarations() is not None:
            for decl in self.getDeclarations():
                ret += decl.printAST() + '\n'
        ret += 'end'
        return ret
