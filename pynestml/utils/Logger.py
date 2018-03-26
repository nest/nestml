#
# Logger.py
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
from pynestml.utils.Messages import MessageCode
from enum import Enum
from collections import OrderedDict
import json


class Logger(object):
    """
    This class represents a logger which can be used to print messages to the screen depending on the logging 
    level.
        LEVELS:
            INFO         Print all received messages.
            WARNING     Print all received warning.
            ERROR       Print all received errors.
            NO          Print no messages
    Hereby, errors are the most specific level, thus no warnings and non critical messages are shown. If logging 
    level is set to WARNING, only warnings and errors are printed. Only if level is set to ALL, all messages 
    are printed.
    Attributes:
        __log       Stores all messages as received during the execution. Map from id (int) to neuron,type,message
        __currMessage A counter indicating the current message, this enables a sorting by the number of message
        __loggingLevel Indicates messages of which level shall be printed to the screen.
        __currentNeuron The currently processed model. This enables to retrieve all messages belonging to a certain model
    """
    __log = {}
    __currMessage = None
    __loggingLevel = None
    __currentNeuron = None

    @classmethod
    def initLogger(cls, _loggingLevel=None):
        """
        Initializes the logger.
        :param _loggingLevel: the logging level as required
        :type _loggingLevel: LOGGING_LEVEL
        """
        assert (_loggingLevel is not None and isinstance(_loggingLevel, LOGGING_LEVEL)), \
            '(PyNestML.Logger) No or wrong type of logging-level provided (%s)!' % type(_loggingLevel)
        cls.__loggingLevel = _loggingLevel
        cls.__currMessage = 0
        cls.__log = {}
        return

    @classmethod
    def getLog(cls):
        """
        Returns the overall log of messages. The structure of the log is: (NEURON,LEVEL,MESSAGE)
        :return: dict from id to neuron+message+type.
        :rtype: dict(int->neuron,level,str)
        """
        return cls.__log

    @classmethod
    def logMessage(cls, _neuron=None, _code=None, _message=None, _errorPosition=None, _logLevel=None):
        """
        Logs the handed over message on the handed over. If the current logging is appropriate, the 
        message is also printed.
        :param _neuron: the neuron in which the error occurred
        :type _neuron: ASTNeuron
        :param _code: a single error code
        :type _code: ErrorCode
        :param _errorPosition: the position on which the error occurred.
        :type _errorPosition: SourcePosition
        :param _message: a message.
        :type _message: str
        :param _logLevel: the corresponding log level.
        :type _logLevel: LOGGING_LEVEL
        """
        if cls.__currMessage is None:
            cls.initLogger(LOGGING_LEVEL.INFO)
        from pynestml.modelprocessor.ASTNeuron import ASTNeuron
        from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
        assert (_message is not None and isinstance(_message, str)), \
            '(PyNestML.Logger) No or wrong type of message provided (%s)!' % type(_message)
        assert (_logLevel is not None and isinstance(_logLevel, LOGGING_LEVEL)), \
            '(PyNestML.Logger) No or wrong type of logging-level provided (%s)!' % type(_logLevel)
        assert (_neuron is None or isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Logger) Wrong type of neuron provided (%s)!' % type(_neuron)
        assert (_errorPosition is None or isinstance(_errorPosition, ASTSourcePosition)), \
            '(PyNestML.Logger) Wrong type of error position provided (%s)!' % type(_errorPosition)
        assert (_code is not None and isinstance(_code, MessageCode)), \
            '(PyNestML.Logger) Wrong type of code provided (%s)!' % type(_code)
        if isinstance(_neuron, ASTNeuron):
            cls.__log[cls.__currMessage] = (
                _neuron.getArtifactName(), _neuron, _logLevel, _code, _errorPosition, _message)
        elif cls.__currentNeuron is not None:
            cls.__log[cls.__currMessage] = (cls.__currentNeuron.getArtifactName(), cls.__currentNeuron,
                                            _logLevel, _code, _errorPosition, _message)
        cls.__currMessage += 1
        if cls.__loggingLevel.value <= _logLevel.value:
            print('[' + str(cls.__currMessage) + ','
                  + (_neuron.getName() + ', ' if _neuron is not None else
                     cls.__currentNeuron.getName() + ', ' if cls.__currentNeuron is not None else 'GLOBAL, ')
                  + str(_logLevel.name) + ', ' + str(_code.name) +
                  (', ' + str(_errorPosition) if _errorPosition is not None else '') + ']:'
                  + str(_message))
        return

    @classmethod
    def stringToLevel(cls, _string=None):
        """
        Returns the logging level corresponding to the handed over string. If no such exits, returns None.
        :param _string: a single string representing the level.
        :type _string: str
        :return: a single logging level.
        :rtype: LOGGING_LEVEL
        """
        if type(_string) != str:
            return LOGGING_LEVEL.ERROR
        elif _string == 'INFO':
            return LOGGING_LEVEL.INFO
        elif _string == 'WARNING' or _string == 'WARNINGS':
            return LOGGING_LEVEL.WARNING
        elif _string == 'ERROR' or _string == 'ERRORS':
            return LOGGING_LEVEL.ERROR
        elif _string == 'NO':
            return LOGGING_LEVEL.NO
        else:
            return LOGGING_LEVEL.ERROR

    @classmethod
    def setLoggingLevel(cls, _level=None):
        """
        Updates the logging level to the handed over one.
        :param _level: a new logging level.
        :type _level: LOGGING_LEVEL
        """
        assert (_level is not None and isinstance(_level, LOGGING_LEVEL)), \
            '(PyNestML.Utils.Logger) No or wrong type of logging-level provided (%s)!' % type(_level)
        cls.__loggingLevel = _level
        return

    @classmethod
    def setCurrentNeuron(cls, _neuron=None):
        """
        Sets the handed over neuron as the currently processed one. This enables a retrieval of messages for a
        specific neuron.
        :param _neuron:  a single neuron instance
        :type _neuron: ASTNeuron
        """
        from pynestml.modelprocessor.ASTNeuron import ASTNeuron
        assert (_neuron is None or isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Utils.Logger) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__currentNeuron = _neuron
        return

    @classmethod
    def getAllMessagesOfLevelAndOrNeuron(cls, _neuron=None, _level=None):
        """
        Returns all messages which have a certain logging level, or have been reported for a certain neuron, or
        both.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeron
        :param _level: a logging level
        :type _level: LOGGING_LEVEL
        :return: a list of messages with their levels.
        :rtype: list((str,Logging_Level)
        """
        from pynestml.modelprocessor.ASTNeuron import ASTNeuron
        assert (_level is None or isinstance(_level, LOGGING_LEVEL)), \
            '(PyNestML.Utils.Logger) Wrong type of logging level provided (%s)!' % (_level)
        assert (_neuron is None or isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Utils.Logger) Wrong type of neuron provided (%s)!' % type(_neuron)
        if _level is None and _neuron is None:
            return cls.getLog()
        ret = list()
        for (artifactName, neuron, logLevel, code, errorPosition, message) in cls.__log.values():
            if (_level == logLevel if _level is not None else True) and (
                    _neuron if _neuron is not None else True) and (_neuron.getArtifactName() == artifactName
                                                                   if _neuron is not None else True):
                ret.append((neuron, logLevel, message))
        return ret

    @classmethod
    def hasErrors(cls, _neuron=None):
        """
        Indicates whether the handed over neuron, thus the corresponding model, has errors.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        :return: True if errors detected, otherwise False
        :rtype: bool
        """
        return len(cls.getAllMessagesOfLevelAndOrNeuron(_neuron, LOGGING_LEVEL.ERROR)) > 0

    @classmethod
    def getPrintableFormat(cls):
        """
        Returns the log in a format which can be used to be stored to a file.
        :return: a str containing the log
        :rtype: str
        """
        ret = '['
        for messageNr in cls.__log.keys():
            (artifactName, neuron, logLevel, code, errorPosition, message) = cls.__log[messageNr]
            ret += '{' + \
                   '"filename":"' + \
                   artifactName + \
                   '", ' + \
                   '"neuronName":"' + \
                   (neuron.getName() if neuron is not None else 'GLOBAL') + '", ' + \
                   '"severity":"' \
                   + str(logLevel.name) + '", ' \
                   + '"code":"' \
                   + code.name + \
                   '", ' + \
                   '"row":"' + \
                   (str(errorPosition.getStartLine()) if errorPosition is not None else '') + \
                   '", ' + \
                   '"col":"' \
                   + (str(errorPosition.getStartColumn()) if errorPosition is not None else '') + \
                   '", ' + \
                   '"message":"' + str(message).replace('"', "'") + '"}'
            ret += ','
        if len(cls.__log.keys()) == 0:
            parsed = json.loads('[]', object_pairs_hook=OrderedDict)
        else:
            ret = ret[:-1]  # delete the last ","
            ret += ']'
            parsed = json.loads(ret, object_pairs_hook=OrderedDict)
        return json.dumps(parsed, indent=2, sort_keys=False)


class LOGGING_LEVEL(Enum):
    """
    Different types of logging levels, this part can be extended.
    """
    INFO = 0
    WARNING = 1
    ERROR = 2
    NO = 3
