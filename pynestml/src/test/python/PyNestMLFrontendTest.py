#
# PyNestMLFrontendTest.py
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
import unittest
import os
from pynestml.src.main.python.org.frontend.PyNestMLFrontend import main


class PyNestMLFrontendTest(unittest.TestCase):
    """
    Tests if the frontend works as intended and is able to process handed over arguments.
    """

    def test(self):
        path = str(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                 os.path.join('..', '..', '..', '..', 'models'))))
        params = list()
        params.append('-path')
        params.append(path)
        #params.append('-dry')
        params.append('-logging_level')
        params.append('ALL')
        params.append('-target')
        params.append('buildNest')
        main(params)


if __name__ == '__main__':
    unittest.main()
