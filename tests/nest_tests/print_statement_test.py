# -*- coding: utf-8 -*-
#
# print_statement_test.py
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
import subprocess
import unittest


class PrintStatementTest(unittest.TestCase):
    """
    Test to validate the output of NEST cout statements converted from the corresponding NESTML print() functions.
    """

    def test_print_statement(self):
        input_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            'resources', 'print_variable_script.py'))))
        self.output_path = "output.txt"

        with open(self.output_path, 'w') as outfile:
            subprocess.run(['python', input_path], stdout=outfile)

        with open(self.output_path, 'r') as reader:
            lines = list(reader.readlines())
            reader.close()

        matches = [s for s in lines if "print:" in s]
        self.assertEqual(matches[0], "print: This is a simple print statement\n")
        self.assertEqual(matches[1], "print: Membrane voltage: -0.05 V, threshold: -7e-08 MA Ohm, and V_abs: -50 mV\n")

    def tearDown(self) -> None:
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
