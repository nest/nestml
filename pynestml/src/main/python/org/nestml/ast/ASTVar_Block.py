"""
@author kperun
TODO header
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
