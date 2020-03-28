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
import json
from collections import OrderedDict
from enum import Enum


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
        log       Stores all messages as received during the execution. Map from id (int) to astnode,type,message
        curr_message A counter indicating the current message, this enables a sorting by the number of message
        logging_level Indicates messages of which level shall be printed to the screen.
        current_astnode The currently processed model. This enables to retrieve all messages belonging to a certain model
    """
    log = {}
    curr_message = None
    log_frozen = False
    logging_level = None
    current_astnode = None
    no_print = False

    @classmethod
    def init_logger(cls, logging_level):
        """
        Initializes the logger.
        :param logging_level: the logging level as required
        :type logging_level: LoggingLevel
        """
        cls.logging_level = logging_level
        cls.curr_message = 0
        cls.log = {}
        cls.log_frozen = False
        return

    @classmethod
    def freeze_log(cls, do_freeze=True):
        """
        Freeze the log: while log is frozen, all logging requests will be ignored.
        """
        cls.log_frozen = do_freeze

    @classmethod
    def get_log(cls):
        """
        Returns the overall log of messages.
        :return: dict from entry id to (astnode, message, type) tuple.
        :rtype: dict(int -> tuple(astnode, level, str))
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
    def log_message(cls, astnode=None, code=None, message=None, error_position=None, log_level=None):
        """
        Logs the handed over message on the handed over. If the current logging is appropriate, the
        message is also printed.
        :param astnode: the node in which the error occurred
        :type astnode: ASTNeuron or ASTSynapse
        :param code: a single error code
        :type code: ErrorCode
        :param error_position: the position on which the error occurred.
        :type error_position: SourcePosition
        :param message: a message.
        :type message: str
        :param log_level: the corresponding log level.
        :type log_level: LoggingLevel
        """
        if cls.log_frozen:
            return
        if cls.curr_message is None:
            cls.init_logger(LoggingLevel.INFO)
        from pynestml.meta_model.ast_neuron import ASTNeuron
        from pynestml.meta_model.ast_synapse import ASTSynapse
        from pynestml.meta_model.ast_source_location import ASTSourceLocation
        assert astnode is None or isinstance(astnode, ASTNeuron) or isinstance(astnode, ASTSynapse), \
            '(PyNestML.Logger) Wrong type of neuron or synapse provided (%s)!' % type(astnode)
        assert (error_position is None or isinstance(error_position, ASTSourceLocation)), \
            '(PyNestML.Logger) Wrong type of error position provided (%s)!' % type(error_position)
        if isinstance(astnode, ASTNeuron) or isinstance(astnode, ASTSynapse):
            cls.log[cls.curr_message] = (
                astnode.get_artifact_name(), astnode, log_level, code, error_position, message)
        elif isinstance(cls.current_astnode, ASTNeuron) or isinstance(cls.current_astnode, ASTSynapse):
            cls.log[cls.curr_message] = (cls.current_astnode.get_artifact_name(), cls.current_astnode,
                                         log_level, code, error_position, message)
        cls.curr_message += 1
        if cls.no_print:
            return
        if cls.logging_level.value <= log_level.value:
            to_print = '[' + str(cls.curr_message) + ','
            to_print = (to_print + (astnode.get_name() + ', ' if astnode is not None else
                    cls.current_astnode.get_name() + ', ' if cls.current_astnode is not None else 'GLOBAL, '))
            to_print = to_print + str(log_level.name)
            to_print = to_print + (', ' + str(error_position) if error_position is not None else '') + ']: '
            to_print = to_print + str(message)
            print(to_print)
        return

    @classmethod
    def string_to_level(cls, string):
        """
        Returns the logging level corresponding to the handed over string. If no such exits, returns None.
        :param string: a single string representing the level.
        :type string: str
        :return: a single logging level.
        :rtype: LoggingLevel
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
    def set_logging_level(cls, level):
        """
        Updates the logging level to the handed over one.
        :param level: a new logging level.
        :type level: LoggingLevel
        """
        if cls.log_frozen:
            return
        cls.logging_level = level

    @classmethod
    def set_current_astnode(cls, node):
        """
        Sets the handed over astnode as the currently processed one. This enables a retrieval of messages for a
        specific astnode.
        :param node:  a single astnode instance
        :type node: astnode
        """
        if cls.log_frozen:
            return
        from pynestml.meta_model.ast_neuron import ASTNeuron
        from pynestml.meta_model.ast_synapse import ASTSynapse
        assert isinstance(node, ASTNeuron) or isinstance(node, ASTSynapse) or node is None
        cls.current_astnode = node

    @classmethod
    def get_all_messages_of_level_and_or_astnode(cls, astnode, level):
        """
        Returns all messages which have a certain logging level, or have been reported for a certain astnode, or
        both.
        :param astnode: a single astnode instance
        :type astnode: ASTNeron
        :param level: a logging level
        :type level: LoggingLevel
        :return: a list of messages with their levels.
        :rtype: list((str,Logging_Level)
        """
        if level is None and astnode is None:
            return cls.get_log()
        ret = list()
        for (artifactName, astnode_i, logLevel, code, errorPosition, message) in cls.log.values():
            if (level == logLevel if level is not None else True) and (
                    astnode if astnode is not None else True) and (
                    astnode.get_artifact_name() == artifactName if astnode is not None else True):
                ret.append((astnode, logLevel, message))
        return ret

    @classmethod
    def get_all_messages_of_level(cls, level):
        """
        Returns all messages which have a certain logging level.
        :param level: a logging level
        :type level: LoggingLevel
        :return: a list of messages with their levels.
        :rtype: list((str,Logging_Level)
        """
        if level is None:
            return cls.get_log()
        ret = list()
        for (artifactName, astnode, logLevel, code, errorPosition, message) in cls.log.values():
            if level == logLevel:
                ret.append((astnode, logLevel, message))
        return ret

    @classmethod
    def get_all_messages_of_astnode(cls, astnode):
        """
        Returns all messages which have been reported for a certain astnode.
        :param astnode: a single astnode instance
        :type astnode: ASTNeron
        :return: a list of messages with their levels.
        :rtype: list((str,Logging_Level)
        """
        if astnode is None:
            return cls.get_log()
        ret = list()
        for (artifactName, astnode_i, logLevel, code, errorPosition, message) in cls.log.values():
            if (astnode_i == astnode if astnode is not None else True) and \
                    (astnode.get_artifact_name() == artifactName if astnode is not None else True):
                ret.append((astnode, logLevel, message))
        return ret

    @classmethod
    def has_errors(cls, astnode):
        """
        Indicates whether the handed over astnode, thus the corresponding model, has errors.
        :param astnode: a single astnode instance.
        :type astnode: astnode
        :return: True if errors detected, otherwise False
        :rtype: bool
        """
        return len(cls.get_all_messages_of_level_and_or_astnode(astnode, LoggingLevel.ERROR)) > 0

    @classmethod
    def get_json_format(cls):
        """
        Returns the log in a format which can be used to be stored to a file.
        :return: a str containing the log
        :rtype: str
        """
        ret = '['
        for messageNr in cls.log.keys():
            (artifactName, astnode, logLevel, code, errorPosition, message) = cls.log[messageNr]
            ret += '{' + \
                   '"filename":"' + \
                   artifactName + \
                   '", ' + \
                   '"modelName":"' + \
                   (astnode.get_name() if astnode is not None else 'GLOBAL') + '", ' + \
                   '"severity":"' \
                   + str(logLevel.name) + '", '
            if not code is None:
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


class LoggingLevel(Enum):
    """
    Different types of logging levels, this part can be extended.
    """
    INFO = 0
    WARNING = 1
    ERROR = 2
    NO = 3
