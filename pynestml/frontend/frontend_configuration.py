# -*- coding: utf-8 -*-
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

from typing import Any, Mapping, Optional, Sequence

import argparse
import glob
import os
import re

import pynestml
from pynestml.exceptions.invalid_path_exception import InvalidPathException
from pynestml.exceptions.invalid_target_exception import InvalidTargetException
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages, MessageCode

help_input_path = 'One or more input path(s). Each path is a NESTML file, or a directory containing NESTML files. Directories will be searched recursively for files matching \'*.nestml\'.'
help_target_path = 'Path to a directory where generated code should be written to. Standard is "target".'
help_install_path = 'Path to the directory where the generated code will be installed.'
help_target = 'Name of the target platform to build code for. Default is NEST.'
help_logging = 'Indicates which messages shall be logged and printed to the screen. Standard is ERROR.'
help_module = 'Indicates the name of the module. Optional. If not indicated, the name of the directory containing the models is used'
help_log = 'Indicates whether a log file containing all messages shall be stored. Standard is NO.'
help_suffix = 'A suffix string that will be appended to the name of all generated models.'
help_dev = 'Enable development mode: extra information is rendered in the generated code, like the name of the template that generates the code.'
help_codegen_opts = 'Path to a JSON file containing additional options for the target platform code generator.'

qualifier_input_path_arg = '--input_path'
qualifier_target_path_arg = '--target_path'
qualifier_install_path_arg = '--install_path'
qualifier_target_platform_arg = '--target_platform'
qualifier_logging_level_arg = '--logging_level'
qualifier_module_name_arg = '--module_name'
qualifier_store_log_arg = '--store_log'
qualifier_suffix_arg = '--suffix'
qualifier_dev_arg = '--dev'
qualifier_codegen_opts_arg = '--codegen_opts'


class FrontendConfiguration:
    """
    This class encapsulates all settings as handed over to the frontend at start of the toolchain.
    """

    # static properties
    DEFAULT_TARGET_PATH_: str = "target"

    # member variables
    argument_parser = None
    paths_to_compilation_units = None
    provided_input_path = None
    logging_level = None
    target = None
    install_path = None
    target_path = None
    target_platform = ""
    module_name = None
    store_log = False
    suffix = ""
    is_dev = False
    codegen_opts = {}  # type: Mapping[str, Any]
    codegen_opts_fn = ""

    @classmethod
    def parse_config(cls, args):
        """
        Standard constructor. This method parses the
        :param args: a set of arguments as handed over to the frontend
        :type args: list(str)
        """
        from pynestml.frontend.pynestml_frontend import get_known_targets

        cls.argument_parser = argparse.ArgumentParser(
            description='''NESTML is a domain specific language that supports the specification of neuron
models in a precise and concise syntax, based on the syntax of Python. Model
equations can either be given as a simple string of mathematical notation or
as an algorithm written in the built-in procedural language. The equations are
analyzed by NESTML to compute an exact solution if possible or use an
appropriate numeric solver otherwise.

 Version ''' + str(pynestml.__version__), formatter_class=argparse.RawDescriptionHelpFormatter)

        cls.argument_parser.add_argument(qualifier_input_path_arg, metavar='PATH', nargs='+',
                                         type=str, help=help_input_path, required=True)
        cls.argument_parser.add_argument(qualifier_target_path_arg, metavar='PATH', type=str, help=help_target_path)
        cls.argument_parser.add_argument(qualifier_install_path_arg, metavar='PATH', type=str, help=help_install_path)
        cls.argument_parser.add_argument(qualifier_target_platform_arg, choices=get_known_targets(), type=str.upper, help=help_target, default='NEST')
        cls.argument_parser.add_argument(qualifier_logging_level_arg, metavar='{DEBUG, INFO, WARNING, ERROR, NONE}', choices=[
                                         'DEBUG', 'INFO', 'WARNING', 'WARNINGS', 'ERROR', 'ERRORS', 'NONE', 'NO'], type=str, help=help_logging, default='ERROR')
        cls.argument_parser.add_argument(qualifier_module_name_arg, metavar='NAME', type=str, help=help_module)
        cls.argument_parser.add_argument(qualifier_store_log_arg, action='store_true', help=help_log)
        cls.argument_parser.add_argument(qualifier_suffix_arg, metavar='SUFFIX', type=str, help=help_suffix, default='')
        cls.argument_parser.add_argument(qualifier_dev_arg, action='store_true', help=help_dev)
        cls.argument_parser.add_argument(qualifier_codegen_opts_arg, metavar='PATH', type=str, help=help_codegen_opts, default='', dest='codegen_opts_fn')
        parsed_args = cls.argument_parser.parse_args(args)

        # initialize the logger
        cls.logging_level = Logger.level_to_string(Logger.string_to_level(parsed_args.logging_level))
        Logger.init_logger(Logger.string_to_level(parsed_args.logging_level))

        cls.handle_input_path(parsed_args.input_path)
        cls.handle_target_platform(parsed_args.target_platform)
        cls.handle_target_path(parsed_args.target_path)
        cls.handle_install_path(parsed_args.install_path)
        cls.handle_module_name(parsed_args.module_name)
        cls.handle_codegen_opts_fn(parsed_args.codegen_opts_fn)

        cls.store_log = parsed_args.store_log
        cls.suffix = parsed_args.suffix
        cls.is_dev = parsed_args.dev

    @classmethod
    def get_provided_input_path(cls) -> Sequence[str]:
        """
        Returns the list of file and directory names as supplied by the user.
        :return: a list of file and directory names
        """
        return cls.provided_input_path

    @classmethod
    def get_files(cls):
        """
        Returns a list of all files to process.
        :return: a list of paths to files as str.
        :rtype: list(str)
        """
        return cls.paths_to_compilation_units

    @classmethod
    def get_target_platform(cls):
        """
        Get the name of the target platform.
        :return: None or "" in case no code needs to be generated
        :rtype: str
        """
        return cls.target_platform

    @classmethod
    def get_logging_level(cls):
        """
        Returns the set logging level.
        :return: the logging level
        :rtype: LoggingLevel
        """
        return cls.logging_level

    @classmethod
    def get_target_path(cls) -> str:
        """
        Returns the path to which models shall be generated to.
        :return: the target path.
        """
        return cls.target_path

    @classmethod
    def get_install_path(cls) -> str:
        """
        Path to the directory where the generated code will be installed.
        :return: the install path.
        """
        return cls.install_path

    @classmethod
    def get_module_name(cls):
        """
        Returns the name of the module.
        :return: the name of the module.
        :rtype: str
        """
        return cls.module_name

    @classmethod
    def get_is_dev(cls):
        """
        Returns whether the development mode has been enabled.
        :return: True if development mode is enabled, otherwise False.
        :rtype: bool
        """
        return cls.is_dev

    @classmethod
    def get_codegen_opts(cls):
        """Get the code generator options dictionary"""
        return cls.codegen_opts

    @classmethod
    def set_codegen_opts(cls, codegen_opts):
        """Set the code generator options dictionary"""
        cls.codegen_opts = codegen_opts

    @classmethod
    def handle_codegen_opts_fn(cls, codegen_opts_fn):
        """If a filename of a JSON file containing code generator options is passed on the command line, read it into a Python dictionary"""
        if codegen_opts_fn and not os.path.isfile(codegen_opts_fn):
            raise Exception('The specified code generator options file ("' + codegen_opts_fn + '") cannot be found')
        cls.codegen_opts_fn = codegen_opts_fn
        cls.codegen_opts = {}
        if cls.codegen_opts_fn:
            # load optional code generator options from JSON
            import json
            if FrontendConfiguration.codegen_opts_fn:
                with open(FrontendConfiguration.codegen_opts_fn) as json_file:
                    cls.codegen_opts = json.load(json_file)
            Logger.log_message(message='Loaded code generator options from file: ' + FrontendConfiguration.codegen_opts_fn,
                               log_level=LoggingLevel.INFO)
            if not cls.codegen_opts:
                raise Exception('Errors occurred while processing code generator options file')

    @classmethod
    def handle_module_name(cls, module_name):
        """parse or compose the module name"""
        if module_name is not None:
            if not module_name.endswith('module'):
                raise Exception('Invalid module name specified ("' + module_name
                                + '"): the module name should end with the word "module"')
            if not re.match(r'[a-zA-Z_][a-zA-Z0-9_]*\Z', module_name):
                raise Exception('The specified module name ("' + module_name
                                + '") cannot be parsed as a C variable name')
            cls.module_name = module_name
        else:
            cls.module_name = 'nestmlmodule'
            Logger.log_message(code=MessageCode.MODULE_NAME_INFO, message='No module name specified; the generated module will be named "'
                               + cls.module_name + '"', log_level=LoggingLevel.INFO)

    @classmethod
    def handle_target_platform(cls, target_platform: Optional[str]):
        if target_platform is None or target_platform.upper() == 'NONE':
            target_platform = ''     # make sure `target_platform` is always a string

        from pynestml.frontend.pynestml_frontend import get_known_targets

        if target_platform.upper() not in get_known_targets():
            code, message = Messages.get_unknown_target_platform(target_platform)
            Logger.log_message(None, code, message, None, LoggingLevel.ERROR)
            raise InvalidTargetException()

        cls.target_platform = target_platform

    @classmethod
    def handle_target_path(cls, path: Optional[str]) -> None:
        r"""Process the target path parameter.

        Create the target path directory if it is specified as a string, but does not exist. Its parent directory has to exist already.

        If the path is None, it will default to ``FrontendConfiguration.DEFAULT_TARGET_PATH_`` in the current working directory.
        """

        if path is None:
            cls.target_path = os.path.abspath(cls.DEFAULT_TARGET_PATH_)
        elif os.path.isabs(path):
            cls.target_path = path
        else:
            cls.target_path = os.path.abspath(path)

        # create the target_path directory if it does not yet exist
        if not os.path.isdir(cls.target_path):
            parent_dir = os.path.abspath(os.path.join(cls.target_path, os.path.pardir))
            if os.path.isdir(parent_dir):
                code, msg = Messages.get_creating_target_path(cls.target_path)
                Logger.log_message(code=code, message=msg, log_level=LoggingLevel.INFO)
                os.makedirs(cls.target_path)
                return

            # target_path nor parent_dir exist
            raise InvalidPathException("Target path \"" + str(cls.target_path) + "\" not found.")

        code, msg = Messages.get_target_path_info(cls.target_path)
        Logger.log_message(code=code, message=msg, log_level=LoggingLevel.INFO)

    @classmethod
    def handle_install_path(cls, path: Optional[str]) -> None:
        r"""Process the installation path parameter.

        Create the installation path directory if it is specified as a string, but does not exist. Its parent directory has to exist already. The path will not be created if ``path`` is None."""
        if path is None:
            return

        if os.path.isabs(path):
            cls.install_path = path
        else:
            cls.install_path = os.path.abspath(path)

        # create the install_path directory if it does not yet exist
        if not os.path.isdir(cls.install_path):
            parent_dir = os.path.abspath(os.path.join(cls.install_path, os.path.pardir))
            if os.path.isdir(parent_dir):
                code, msg = Messages.get_creating_install_path(path)
                Logger.log_message(code=code, message=msg, log_level=LoggingLevel.INFO)
                os.makedirs(cls.install_path)
                return

            # install_path nor parent_dir exist
            raise InvalidPathException("Installation path \"" + str(cls.install_path) + "\" not found.")

        code, msg = Messages.get_install_path_info(cls.install_path)
        Logger.log_message(code=code, message=msg, log_level=LoggingLevel.INFO)

    @classmethod
    def handle_input_path(cls, path) -> None:
        """
        Sets cls.paths_to_compilation_units with a list of absolute paths to NESTML files.

        Use glob to search directories recursively.
        """
        cls.provided_input_path = path

        if not path or path == ['']:
            # mandatory path arg has not been handed over
            code, message = Messages.get_input_path_not_found(path="")
            Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR)
            raise InvalidPathException(message)

        if type(path) is str:
            path = [path]

        cls.paths_to_compilation_units = list()
        for _path in path:
            if not os.path.isabs(_path):
                # turn relative to absolute path
                pynestml_dir = os.getcwd()
                _path = os.path.join(pynestml_dir, _path)

            if os.path.isfile(_path):
                cls.paths_to_compilation_units.append(_path)
            elif os.path.isdir(_path):
                for fn in glob.glob(os.path.join(_path, "**", "*.nestml"), recursive=True):
                    cls.paths_to_compilation_units.append(os.path.join(_path, fn))
            else:
                # input_path should be either a file or a directory
                code, message = Messages.get_input_path_not_found(path=_path)
                Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR)
                raise InvalidPathException(message)

        if not cls.paths_to_compilation_units:
            code, message = Messages.get_no_files_in_input_path(" ".join(path))
            Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR)
            raise InvalidPathException(message)

        Logger.log_message(message="List of files that will be processed:", log_level=LoggingLevel.INFO)
        for fn in cls.paths_to_compilation_units:
            Logger.log_message(message=fn, log_level=LoggingLevel.INFO)
