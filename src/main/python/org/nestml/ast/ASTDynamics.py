"""
@author kperun
TODO header
"""
from src.main.python.org.nestml.ast.ASTBlock import *


class ASTDynamics:
    """
    This class is used to store dynamic blocks.
    ASTDynamics a special function definition:
      update:
        if r == 0: # not refractory
          integrate(V)
        end
      end
     @attribute block Implementation of the dynamics.
   
    Grammar:
        dynamics:
            'update'
            BLOCK_OPEN
              block
            BLOCK_CLOSE;
    """
    __block = None

    def __init__(self, _block=None):
        """
        Standard constructor.
        :param _block: a block of definitions.
        :type _block: ASTBlock
        """
        assert (_block is not None)
        self.__block = _block

    @classmethod
    def makeASTDynamics(cls, _block=None):
        """
        Factory method of the ASTDynamics class.
        :param _block: a block of definitions.
        :type _block: ASTBlock
        :return: a new ASTDynamics object.
        :rtype: ASTDynamics
        """
        return cls(_block)

    def getBlock(self):
        """
        Returns the block of definitions.
        :return: the block
        :rtype: ASTBlock
        """
        return self.__block
