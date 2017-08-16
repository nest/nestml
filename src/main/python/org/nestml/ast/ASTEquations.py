"""
@author kperun
TODO header
"""
from src.main.python.org.nestml.ast.ASTBlock import *


class ASTEquations:
    """
    This class is used to store an equations block.
    ASTEquations a special function definition:
       equations:
         G = (e/tau_syn) * t * exp(-1/tau_syn*t)
         V' = -1/Tau * V + 1/C_m * (I_sum(G, spikes) + I_e + currents)
       end
     @attribute odeDeclaration Block with equations and differential equations.
     Grammar:
          equations:
            'equations'
            BLOCK_OPEN
              odeDeclaration
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
    def makeASTEquations(cls, _block=None):
        """
        Factory method of the ASTEquations class.
        :param _block: a block of definitions.
        :type _block: ASTBlock
        :return: a new ASTEquations object.
        :rtype: ASTEquations
        """
        return cls(_block)

    def getBlock(self):
        """
        Returns the block of definitions.
        :return: the block
        :rtype: ASTBlock
        """
        return self.__block
