# -*- coding: utf-8 -*-
#
# logger.py
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

from typing import List, Mapping, Tuple

from collections import OrderedDict
from enum import Enum
import json
from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.messages import MessageCode


class LoggingLevel(Enum):
    """
    Different types of logging levels, this part can be extended.
    """
    INFO = 0
    WARNING = 1
    ERROR = 2
    NO = 3


class Logger:
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
        log       Stores all messages as received during the execution. Map from id (int) to node,type,message
        curr_message A counter indicating the current message, this enables a sorting by the number of message
        logging_level Indicates messages of which level shall be printed to the screen.
        current_node The currently processed model. This enables to retrieve all messages belonging to a certain model
    """
    log = {}
    curr_message = None
    logging_level = None
    current_node = None
    no_print = False

    @classmethod
    def init_logger(cls, logging_level: LoggingLevel):
        """
        Initializes the logger.
        :param logging_level: the logging level as required
        """
        cls.logging_level = logging_level
        cls.curr_message = 0
        cls.log = {}
        cls.log_frozen = False

    def freeze_log(cls, do_freeze: bool = True):
        """
        Freeze the log: while log is frozen, all logging requests will be ignored.
        """
        cls.log_frozen = do_freeze

    @classmethod
    def get_log(cls) -> Mapping[int, Tuple[ASTNode, LoggingLevel, str]]:
        """
        Returns the overall log of messages. The structure of the log is: (NODE, LEVEL, MESSAGE)
        :return: mapping from id to ASTNode, log level and message.
        """
        return cls.log

    @classmethod
    def set_log(cls, log, counter):
        """
        Restores log from the 'log' variable
        :param log: the log
        :param counter: the counter
        """
        cls.log = log
        cls.curr_message = counter

    @classmethod
    def log_message(cls, node: ASTNode = None, code: MessageCode = None, message: str = None, error_position: ASTSourceLocation = None, log_level: LoggingLevel = None):
        """
        Logs the handed over message on the handed over. If the current logging is appropriate, the
        message is also printed.
        :param node: the node in which the error occurred
        :param code: a single error code
        :param error_position: the position on which the error occurred.
        :param message: a message.
        :param log_level: the corresponding log level.
        """
        if cls.log_frozen:
            return
        if cls.curr_message is None:
            cls.init_logger(LoggingLevel.INFO)
        from pynestml.meta_model.ast_node import ASTNode
        from pynestml.utils.ast_source_location import ASTSourceLocation
        assert (node is None or isinstance(node, ASTNode)), \
            '(PyNestML.Logger) Wrong type of node provided (%s)!' % type(node)
        assert (error_position is None or isinstance(error_position, ASTSourceLocation)), \
            '(PyNestML.Logger) Wrong type of error position provided (%s)!' % type(error_position)
        from pynestml.meta_model.ast_neuron import ASTNeuron
        if isinstance(node, ASTNeuron):
            cls.log[cls.curr_message] = (
                node.get_artifact_name(), node, log_level, code, error_position, message)
        elif cls.current_node is not None:
            cls.log[cls.curr_message] = (cls.current_node.get_artifact_name(), cls.current_node,
                                         log_level, code, error_position, message)
        cls.curr_message += 1
        if cls.no_print:
            return
        if cls.logging_level.value <= log_level.value:
            to_print = '[' + str(cls.curr_message) + ','
            to_print = (to_print + (node.get_name() + ', ' if node is not None else
                                    cls.current_node.get_name() + ', ' if cls.current_node is not None else 'GLOBAL, '))
            to_print = to_print + str(log_level.name)
            to_print = to_print + (', ' + str(error_position) if error_position is not None else '') + ']: '
            to_print = to_print + str(message)
            print(to_print)
        return

    @classmethod
    def string_to_level(cls, string: str) -> LoggingLevel:
        """
        Returns the logging level corresponding to the handed over string. If no such exits, returns None.
        :param string: a single string representing the level.
        :return: a single logging level.
        """
        if type(string) != str:
            return LoggingLevel.ERROR
        elif string == 'INFO':
            return LoggingLevel.INFO
        elif string == 'WARNING' or string == 'WARNINGS':
            return LoggingLevel.WARNING
        elif string == 'ERROR' or string == 'ERRORS':
            return LoggingLevel.ERROR
        elif string == 'NO' or string == 'NONE':
            return LoggingLevel.NO
        else:
            return LoggingLevel.ERROR

    @classmethod
    def set_logging_level(cls, level: LoggingLevel) -> None:
        """
        Updates the logging level to the handed over one.
        :param level: a new logging level.
        """
        if cls.log_frozen:
            return
        cls.logging_level = level

    @classmethod
    def set_current_node(cls, node: ASTNode) -> None:
        """
        Sets the handed over node as the currently processed one. This enables a retrieval of messages for a
        specific node.
        :param node:  a single node instance
        """
        cls.current_node = node

    @classmethod
    def get_all_messages_of_level_and_or_node(cls, node: ASTNode, level: LoggingLevel) -> List[Tuple[ASTNode, LoggingLevel, str]]:
        """
        Returns all messages which have a certain logging level, or have been reported for a certain node, or
        both.
        :param node: a single node instance
        :param level: a logging level
        :return: a list of messages with their levels.
        """
        if level is None and node is None:
            return cls.get_log()
        ret = list()
        for (artifactName, node_i, logLevel, code, errorPosition, message) in cls.log.values():
            if (level == logLevel if level is not None else True) and (
                    node if node is not None else True) and (
                    node.get_artifact_name() == artifactName if node is not None else True):
                ret.append((node, logLevel, message))
        return ret

    @classmethod
    def get_all_messages_of_level(cls, level: LoggingLevel) -> List[Tuple[ASTNode, LoggingLevel, str]]:
        """
        Returns all messages which have a certain logging level.
        :param level: a logging level
        :return: a list of messages with their levels.
        """
        if level is None:
            return cls.get_log()
        ret = list()
        for (artifactName, node, logLevel, code, errorPosition, message) in cls.log.values():
            if level == logLevel:
                ret.append((node, logLevel, message))
        return ret

    @classmethod
    def get_all_messages_of_node(cls, node: ASTNode) -> List[Tuple[ASTNode, LoggingLevel, str]]:
        """
        Returns all messages which have been reported for a certain node.
        :param node: a single node instance
        :return: a list of messages with their levels.
        """
        if node is None:
            return cls.get_log()
        ret = list()
        for (artifactName, node_i, logLevel, code, errorPosition, message) in cls.log.values():
            if (node_i == node if node is not None else True) and \
                    (node.get_artifact_name() == artifactName if node is not None else True):
                ret.append((node, logLevel, message))
        return ret

    @classmethod
    def has_errors(cls, node: ASTNode) -> bool:
        """
        Indicates whether the handed over node, thus the corresponding model, has errors.
        :param node: a single node instance.
        :return: True if errors detected, otherwise False
        """
        return len(cls.get_all_messages_of_level_and_or_node(node, LoggingLevel.ERROR)) > 0

    @classmethod
    def get_json_format(cls) -> str:
        """
        Returns the log in a format which can be used to be stored to a file.
        :return: a string containing the log
        """
        ret = '['
        for messageNr in cls.log.keys():
            (artifactName, node, logLevel, code, errorPosition, message) = cls.log[messageNr]
            ret += '{' + \
                   '"filename":"' + \
                   artifactName + \
                   '", ' + \
                   '"nodeName":"' + \
                   (node.get_name() if node is not None else 'GLOBAL') + '", ' + \
                   '"severity":"' \
                   + str(logLevel.name) + '", '
            if code is not None:
                ret += '"code":"' + \
                       code.name + \
                       '", '
            ret += '"row":"' + \
                   (str(errorPosition.get_start_line()) if errorPosition is not None else '') + \
                   '", ' + \
                   '"col":"' \
                   + (str(errorPosition.get_start_column()) if errorPosition is not None else '') + \
                   '", ' + \
                   '"message":"' + str(message).replace('"', "'") + '"}'
            ret += ','
        if len(cls.log.keys()) == 0:
            parsed = json.loads('[]', object_pairs_hook=OrderedDict)
        else:
            ret = ret[:-1]  # delete the last ","
            ret += ']'
            parsed = json.loads(ret, object_pairs_hook=OrderedDict)
        return json.dumps(parsed, indent=2, sort_keys=False)
