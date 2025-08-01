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

from typing import List, Mapping, Optional, Tuple, Union

from collections import OrderedDict
from enum import Enum
import json

from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.messages import MessageCode
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression


class LoggingLevel(Enum):
    """
    Different types of logging levels, this part can be extended.
    """
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    NO = 4


class Logger:
    """
    This class represents a logger which can be used to print messages to the screen depending on the logging
    level.

        LEVELS:
            DEBUG       Print all received messages.
            INFO        Print all received information messages, warnings and errors.
            WARNING     Print all received warnings and errors.
            ERROR       Print all received errors.
            NO          Print no messages.

    Hereby, errors are the most specific level, thus no warnings and non critical messages are shown. If logging
    level is set to WARNING, only warnings and errors are printed. Only if level is set to DEBUG, all messages
    are printed.

    Attributes:
        log Stores all messages as received during the execution. The log is a map from ID (int) to a tuple: (artifact_name, current_node, log_level, code, error_position, message).
        curr_message A counter indicating the current message, this enables a sorting by the number of message
        logging_level Indicates messages of which level shall be printed to the screen.
        current_node The currently processed model. This enables to retrieve all messages belonging to a certain model
    """
    log = {}
    curr_message = None
    log_frozen = False
    logging_level = None
    current_node = None
    no_print = False

    @classmethod
    def init_logger(cls, logging_level: LoggingLevel):
        """
        Initializes the logger.

        :param logging_level: the logging level as required
        :type logging_level: LoggingLevel
        """
        cls.logging_level = logging_level
        cls.curr_message = 0
        cls.log = {}
        cls.log_frozen = False

    @classmethod
    def freeze_log(cls, do_freeze: bool = True):
        """
        Freeze the log: while log is frozen, all logging requests will be ignored.
        """
        cls.log_frozen = do_freeze

    @classmethod
    def get_log(cls) -> Mapping[int, Tuple[ASTNode, LoggingLevel, str]]:
        """
        Returns the overall log of messages.

        The log is a map from ID (int) to a tuple: (artifact_name, current_node, log_level, code, error_position, message).

        :return: the log
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
    def log_message(cls, node: ASTNode = None, code: MessageCode = None, message: str = None, error_position: ASTSourceLocation = None, log_level: LoggingLevel = None, allow_duplicates: bool = False):
        """
        Logs the handed over message on the handed over node. If the current logging is appropriate, the message is also printed.

        :param node: the node in which the error occurred
        :param code: a single error code
        :param error_position: the position on which the error occurred.
        :param message: a message.
        :param log_level: the corresponding log level.
        :param allow_duplicates: whether to ignore or suppress duplicate messages.
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
        from pynestml.meta_model.ast_model import ASTModel

        if isinstance(node, ASTModel):
            new_log_entry = (node.get_artifact_name(), node, log_level, code, error_position, message)
        else:
            if cls.current_node is not None:
                artifact_name = cls.current_node.get_artifact_name()
            else:
                artifact_name = ""

            new_log_entry = (artifact_name, cls.current_node, log_level, code, error_position, message)

        if not allow_duplicates and new_log_entry in cls.log.values():
            return

        cls.log[cls.curr_message] = new_log_entry

        cls.curr_message += 1
        if cls.no_print:
            return

        if cls.logging_level.value <= log_level.value:
            if isinstance(node, ASTInlineExpression):
                node_name = node.variable_name
            elif node is None:
                node_name = "unknown node"
            else:
                node_name = node.get_name()

            to_print = '[' + str(cls.curr_message) + ','
            to_print = (to_print + (node_name + ', ' if node is not None else
                                    cls.current_node.get_name() + ', ' if cls.current_node is not None else 'GLOBAL, '))
            to_print = to_print + str(log_level.name)
            to_print = to_print + (', ' + str(error_position) if error_position is not None else '') + ']: '
            to_print = to_print + str(message)
            print(to_print)

    @classmethod
    def string_to_level(cls, string: str) -> LoggingLevel:
        """
        Returns the logging level corresponding to the handed over string. If no such exits, returns None.

        :param string: a single string representing the level.
        :return: a single logging level.
        """
        if string == 'DEBUG':
            return LoggingLevel.DEBUG

        if string == 'INFO':
            return LoggingLevel.INFO

        if string == 'WARNING' or string == 'WARNINGS':
            return LoggingLevel.WARNING

        if string == 'ERROR' or string == 'ERRORS':
            return LoggingLevel.ERROR

        if string == 'NO' or string == 'NONE':
            return LoggingLevel.NO

        raise Exception("Tried to convert unknown string '" + string + "' to logging level")

    @classmethod
    def level_to_string(cls, level: LoggingLevel) -> str:
        """
        Returns a string representation of the handed over logging level.
        :param level: LoggingLevel to convert.
        :return: a string representing the logging level.
        """
        if level == LoggingLevel.DEBUG:
            return 'DEBUG'

        if level == LoggingLevel.INFO:
            return 'INFO'

        if level == LoggingLevel.WARNING:
            return 'WARNING'

        if level == LoggingLevel.ERROR:
            return 'ERROR'

        if level == LoggingLevel.NO:
            return 'NO'

        raise Exception("Tried to convert unknown logging level '" + str(level) + "' to string")

    @classmethod
    def set_logging_level(cls, level: LoggingLevel) -> None:
        """
        Updates the logging level to the handed over one.
        :param level: a new logging level.
        :type level: LoggingLevel
        """
        if cls.log_frozen:
            return

        cls.logging_level = level

    @classmethod
    def set_current_node(cls, node: Optional[ASTNode]) -> None:
        """
        Sets the handed over node as the currently processed one. This enables a retrieval of messages for a specific node.

        :param node: a single node instance
        """
        cls.current_node = node

    @classmethod
    def get_messages(cls, node: Optional[Union[ASTNode, str]] = None, level: Optional[LoggingLevel] = None, message_code: Optional[int] = None) -> List[Tuple[ASTNode, LoggingLevel, str]]:
        """
        Returns all messages which have a certain logging level, or have been reported for a certain node, or both.

        :param node: a single node instance
        :param level: a logging level
        :return: a list of messages with their levels.
        """
        if level is None and node is None:
            return cls.get_log()

        if isinstance(node, str):
            # search by artifact name
            node_artifact_name = node
            node = None
        else:
            # search by artifact class object
            node_artifact_name = None

        ret = list()
        for (artifactName, node_i, logLevel, code, errorPosition, message) in cls.log.values():
            if (level == logLevel if level is not None else True) and (node if node is not None else True) and (node_artifact_name == artifactName if node is not None else True) and (code == message_code if message_code is not None else True):
                ret.append((node, logLevel, message))

        return ret

    @classmethod
    def has_errors(cls, node: ASTNode) -> bool:
        """
        Indicates whether the handed over node, thus the corresponding model, has errors.

        :param node: a single node instance.
        :return: True if errors detected, otherwise False
        """
        return len(cls.get_messages(node, LoggingLevel.ERROR)) > 0

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
