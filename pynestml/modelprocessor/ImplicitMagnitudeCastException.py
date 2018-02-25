#
# ImplicitMagnitudeCastException.py
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


class ImplicitMagnitudeCastException(Exception):
    code = None
    message = None
    conversion_factor = None

    def __init__(self, _code, _message, _conversion_factor):
        self.code = _code
        self.message = _message
        self.conversion_factor = _conversion_factor
