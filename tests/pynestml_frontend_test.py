# -*- coding: utf-8 -*-
#
# pynestml_frontend_test.py
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
import os
import pytest
import sys
import tempfile
import unittest

from pynestml.frontend.pynestml_frontend import main
from pynestml.frontend.frontend_configuration import FrontendConfiguration

try:
    # python 3.4+ should use builtin unittest.mock not mock package
    from unittest.mock import patch
except ImportError:
    from mock import patch


class PyNestMLFrontendTest(unittest.TestCase):
    """
    Tests if the frontend works as intended and is able to process handed over arguments.
    """

    def test_codegeneration_for_single_model(self):
        path = str(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                 os.path.join('..', 'models', 'iaf_psc_exp.nestml'))))
        params = list()
        params.append('nestml')
        params.append('--input_path')
        params.append(path)
        params.append('--logging_level')
        params.append('INFO')
        params.append('--target_path')
        params.append('target/models')
        params.append('--store_log')
        params.append('--dev')
        exit_code = None
        with patch.object(sys, 'argv', params):
            exit_code = main()
        self.assertTrue(exit_code == 0)

    def test_module_name_parsing_right_module_name_specified(self):
        path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join('..', 'models'))))

        params = list()
        params.append('--input_path')
        params.append(path)
        params.append('--module_name')
        params.append('xyzzymodule')
        FrontendConfiguration.parse_config(params)

        assert FrontendConfiguration.module_name == 'xyzzymodule'

    def test_module_name_parsing_wrong_module_name_specified(self):
        with pytest.raises(Exception):
            path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join('..', 'models'))))

            params = list()
            params.append('--input_path')
            params.append(path)
            params.append('--module_name')
            params.append('xyzzy')
            FrontendConfiguration.parse_config(params)

    def test_input_path_handling_empty_dir(self):
        with pytest.raises(Exception):
            path = tempfile.mkdtemp(prefix='nestml-')

            params = list()
            params.append('--input_path')
            params.append(path)
            params.append('--logging_level')
            params.append('INFO')
            FrontendConfiguration.parse_config(params)

    def test_input_path_handling_dir_one_file(self):
        path = tempfile.mkdtemp(prefix='nestml-')
        fd, fpath = tempfile.mkstemp(dir=path, suffix='.nestml')
        with open(fpath, 'w') as f:
            f.write('neuron foo:\nend\n')
            os.close(fd)

        params = list()
        params.append('--input_path')
        params.append(path)
        params.append('--logging_level')
        params.append('INFO')
        FrontendConfiguration.parse_config(params)

        assert len(FrontendConfiguration.paths_to_compilation_units) == 1

    def test_input_path_handling_dir_two_files(self):
        path = tempfile.mkdtemp(prefix='nestml-')
        fd, fpath = tempfile.mkstemp(dir=path, suffix='.nestml')
        with open(fpath, 'w') as f:
            f.write('neuron foo:\nend\n')
            os.close(fd)
        fd, fpath = tempfile.mkstemp(dir=path, suffix='.nestml')
        with open(fpath, 'w') as f:
            f.write('neuron bar:\nend\n')
            os.close(fd)

        params = list()
        params.append('--input_path')
        params.append(path)
        params.append('--logging_level')
        params.append('INFO')
        FrontendConfiguration.parse_config(params)

        assert len(FrontendConfiguration.paths_to_compilation_units) == 2

    def tearDown(self):
        # clean up
        import shutil
        if FrontendConfiguration.target_path:
            try:
                shutil.rmtree(FrontendConfiguration.target_path)
            except Exception:
                pass


if __name__ == '__main__':
    unittest.main()
