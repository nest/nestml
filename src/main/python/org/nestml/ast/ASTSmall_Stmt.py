"""
@author kperun
TODO header
"""
from src.main.python.org.nestml.ast.ASTAssignment import ASTAssignment
from src.main.python.org.nestml.ast.ASTFunctionCall import ASTFunctionCall
from src.main.python.org.nestml.ast.ASTReturnStmt import ASTReturnStmt
from src.main.python.org.nestml.ast.ASTDeclaration import ASTDeclaration


class ASTSmall_Stmt:
    """
    This class is used to store small statements, e.g., a declaration.
    Grammar:
        small_Stmt : assignment
                 | functionCall
                 | declaration
                 | returnStmt;
    """
    __assignment = None
    __functionCall = None
    __declaration = None
    __returnStmt = None

    def __init__(self, _assignment: ASTAssignment = None, _functionCall: ASTFunctionCall = None,
                 _declaration: ASTDeclaration = None, _returnStmt: ASTReturnStmt = None):
        """
        Standard constructor.
        :param _assignment: an ast-assignment object.
        :type _assignment: ASTAssignment
        :param _functionCall: an ast-function call object.
        :type _functionCall: ASTFunctionCall
        :param _declaration: an ast-declaration object.
        :type _declaration: ASTDeclaration
        :param _returnStmt: an ast-return statement object.
        :type _returnStmt: ASTReturnStmt
        """
        self.__assignment = _assignment
        self.__functionCall = _functionCall
        self.__declaration = _declaration
        self.__returnStmt = _returnStmt

    @classmethod
    def makeASTSmall_Stmt(cls, _assignment: ASTAssignment = None, _functionCall: ASTFunctionCall = None,
                          _declaration: ASTDeclaration = None, _returnStmt: ASTReturnStmt = None):
        """
        Factory method of the ASTSmall_Stmt class.
        :param _assignment: an ast-assignment object.
        :type _assignment: ASTAssignment
        :param _functionCall: an ast-function call object.
        :type _functionCall: ASTFunctionCall
        :param _declaration: an ast-declaration object.
        :type _declaration: ASTDeclaration
        :param _returnStmt: an ast-return statement object.
        :type _returnStmt: ASTReturnStmt
        :return: a new ASTSmall_Stmt object. 
        :rtype: ASTSmall_Stmt
        """
        return cls(_assignment, _functionCall, _declaration, _returnStmt)

    def isAssignment(self) -> bool:
        """
        Returns whether it is an assignment statement or not.
        :return: True if assignment, False else.
        :rtype: bool
        """
        return self.__assignment is not None

    def getAssignment(self):
        """
        Returns the assignment.
        :return: the assignment statement.
        :rtype: ASTAssignment
        """
        return self.__assignment

    def isFunctionCall(self) -> bool:
        """
        Returns whether it is an function call or not.
        :return: True if function call, False else.
        :rtype: bool
        """
        return self.__functionCall is not None

    def getFunctionCall(self):
        """
        Returns the function call.
        :return: the function call statement.
        :rtype: ASTFunctionCall
        """
        return self.__functionCall

    def isDeclaration(self) -> bool:
        """
        Returns whether it is a declaration statement or not.
        :return: True if declaration, False else.
        :rtype: bool
        """
        return self.__declaration is not None

    def getDeclaration(self):
        """
        Returns the assignment.
        :return: the declaration statement.
        :rtype: ASTDeclaration
        """
        return self.__declaration

    def isReturnStmt(self) -> bool:
        """
        Returns whether it is a return statement or not.
        :return: True if return stmt, False else.
        :rtype: bool
        """
        return self.__returnStmt is not None

    def getReturnStmt(self):
        """
        Returns the return statement.
        :return: the return statement.
        :rtype: ASTReturn_Stmt
        """
        return self.__returnStmt
