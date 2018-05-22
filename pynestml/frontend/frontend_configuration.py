#
# frontend_configuration.py
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
import argparse  # used for parsing of input arguments
import os

from pynestml.utils.logger import Logger

help_path = 'Path to a single file or a directory containing the source models.'
help_target = 'Path to a target directory where models should be generated to. Standard is "target".'
help_logging = 'Indicates which messages shall be logged and printed to the screen. ' \
               'Available ={INFO,WARNING/S,ERROR/S,NO}, Standard is ERRORS.'
help_dry = 'Indicates that a dry run shall be performed, i.e., without generating a target model.'
help_module = 'Indicates the name of the module. Optional. If not indicated, ' \
              'the name of the directory containing the models is used!'
help_log = 'Indicates whether a log file containing all messages shall be stored. Standard is NO.'
help_dev = 'Indicates whether the dev mode should be active, i.e., ' \
           'the whole toolchain executed even though errors in models are present.' \
           ' This option is designed for debug purpose only!'


class FrontendConfiguration(object):
    """
    This class encapsulates all settings as handed over to the frontend at start of the toolchain.
    """
    argument_parser = None
    paths_to_compilation_units = None
    provided_path = None
    logging_level = None
    dry_run = None
    target_path = None
    module_name = None
    store_log = False
    is_debug = False

    @classmethod
    def config(cls, _args=None):
        """
        Standard constructor.
        :param _args: a set of arguments as handed over to the frontend
        :type _args: list(str)
        """
        cls.argument_parser = argparse.ArgumentParser(
            description='NESTML is a domain specific language that supports the specification of neuron models in a'
                        ' precise and concise syntax, based on the syntax of Python. Model equations can either be '
                        ' given as a simple string of mathematical notation or as an algorithm written in the built-in '
                        ' procedural language. The equations are analyzed by NESTML to compute an exact solution'
                        ' if possible or use an appropriate numeric solver otherwise.'
                        ' Version 0.0.6, beta.')

        cls.argument_parser.add_argument('-path', type=str, nargs='+',
                                         help=help_path)
        cls.argument_parser.add_argument('-target', metavar='Target', type=str, nargs='?',
                                         help=help_target)
        cls.argument_parser.add_argument('-dry', action='store_true',
                                         help=help_dry)
        cls.argument_parser.add_argument('-logging_level', type=str, nargs='+',
                                         help=help_logging)
        cls.argument_parser.add_argument('-module_name', type=str, nargs='+',
                                         help=help_module)
        cls.argument_parser.add_argument('-store_log', action='store_true',
                                         help=help_log)
        cls.argument_parser.add_argument('-dev', action='store_true',
                                         help=help_dev)
        parsed_args = cls.argument_parser.parse_args(_args)
        cls.provided_path = parsed_args.path
        if cls.provided_path is None:
            # check if the mandatory path arg has been handed over, just terminate
            raise RuntimeError('Invalid source path!')
        cls.paths_to_compilation_units = list()
        if parsed_args.path is None:
            raise RuntimeError('Invalid source path!')
        elif os.path.isfile(parsed_args.path[0]):
            cls.paths_to_compilation_units.append(parsed_args.path[0])
        elif os.path.isdir(parsed_args.path[0]):
            for filename in os.listdir(parsed_args.path[0]):
                if filename.endswith(".nestml"):
                    cls.paths_to_compilation_units.append(os.path.join(parsed_args.path[0], filename))
        else:
            cls.paths_to_compilation_units = parsed_args.path[0]
            raise RuntimeError('Incorrect path provided' + parsed_args.path[0])
        # initialize the logger

        if parsed_args.logging_level is not None:
            cls.logging_level = parsed_args.logging_level
            Logger.init_logger(Logger.string_to_level(parsed_args.logging_level[0]))
        else:
            cls.logging_level = "ERROR"
            Logger.init_logger(Logger.string_to_level("ERROR"))
        # check if a dry run shall be preformed, i.e. without generating a target model
        cls.dry_run = parsed_args.dry
        # check if a target has been selected, otherwise set the buildNest as target
        if parsed_args.target is not None:
            cls.target_path = str(os.path.realpath(os.path.join('..', parsed_args.target)))
        else:
            if not os.path.isdir(os.path.realpath(os.path.join('..', 'target'))):
                os.makedirs(os.path.realpath(os.path.join('..', 'target')))
            cls.target_path = str(os.path.realpath(os.path.join('..', 'target')))
        # now adjust the name of the module, if it is a single file, then it is called just module
        if parsed_args.module_name is not None:
            cls.module_name = parsed_args.module_name[0]
        elif os.path.isfile(parsed_args.path[0]):
            cls.module_name = 'module'
        elif os.path.isdir(parsed_args.path[0]):
            cls.module_name = os.path.basename(os.path.normpath(parsed_args.path[0]))
        else:
            cls.module_name = 'module'
        cls.store_log = parsed_args.store_log
        cls.is_debug = parsed_args.dev
        return

    @classmethod
    def get_path(cls):
        """
        Returns the path to the handed over directory or file.
        :return: a single path
        :rtype: str
        """
        return cls.provided_path

    @classmethod
    def get_files(cls):
        """
        Returns a list of all files to process.
        :return: a list of paths to files as str.
        :rtype: list(str)
        """
        return cls.paths_to_compilation_units

    @classmethod
    def is_dry_run(cls):
        """
        Indicates whether it is a dry run, i.e., no model shall be generated
        :return: True if dry run, otherwise false.
        :rtype: bool
        """
        return cls.dry_run

    @classmethod
    def get_logging_level(cls):
        """
        Returns the set logging level.
        :return: the logging level
        :rtype: LoggingLevel
        """
        return cls.logging_level

    @classmethod
    def get_target_path(cls):
        """
        Returns the path to which models shall be generated to.
        :return: the target path.
        :rtype: str
        """
        return cls.target_path

    @classmethod
    def get_module_name(cls):
        """
        Returns the name of the module.
        :return: the name of the module.
        :rtype: str
        """
        return cls.module_name

    @classmethod
    def is_dev(cls):
        """
        Returns whether the dev mode have benn set as active.
        :return: True if dev mode is active, otherwise False.
        :rtype: bool
        """
        return cls.is_debug


class InvalidPathException(Exception):
    """
    This exception is thrown whenever neither a file nor a dir has been handed over. This should not happen.
    """
    pass
