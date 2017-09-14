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


from pynestml.src.main.python.org.nestml.cocos.CoCo import CoCo


class CoCosManager:
    """
    This class is used to ensure that a handed over list of cocos holds.
    """
    __cocosToCheck = None

    def __init__(self, _cocos=list()):
        """
        Standard constructor.
        :param _cocos: a list of cocos.
        :type _cocos: list(CoCo)
        """
        assert (_cocos is not None and isinstance(_cocos, list)), \
            '(PyNestML.CoCos.Manager) No or wrong type of CoCos-list handed over!'
        self.__cocosToCheck = _cocos
        return

    def addCoco(self, _coco=None):
        """
        Used to add a single coco to the set of cocos to check.
        :param _coco: a single coco object.
        :type _coco
        """
        assert (_coco is not None and isinstance(_coco, CoCo)), \
            '(PyNestML.CoCo.Manager) No or wrong type of coco provided!'
        self.__cocosToCheck.append(_coco)
        return

    def deleteCoco(self, _coco=None):
        """
        Deletes a single coco from the set of cocos to check.
        :param _coco: the coco to delete
        :type _coco: CoCo
        """
        assert (_coco is not None and isinstance(_coco, CoCo)), \
            '(PyNestML.CoCo.Manager) No or wrong type of coco provided!'
        self.__cocosToCheck.remove(_coco)
        return

    def getCoCos(self):
        """
        Returns the list of all currently active cocos.        
        :return: a list of active cocos.
        :rtype: list(CoCo)
        """
        return self.__cocosToCheck

    def checkCocos(self, _neuron):
        """
        Checks for the handle over neuron, consisting of a AST and the corresponding symbol table, whether all currently
        active cocos hold or not. It is is left to the cocos to take correct, further processes, i.e., either stating
        a simple error message or terminate with an exception.
        :param _neuron: the neuron instance to check.
        :type _neuron: ASTNeuron
        """
        for coco in self.__cocosToCheck:
            coco.checkCoCo(_neuron)
        return
