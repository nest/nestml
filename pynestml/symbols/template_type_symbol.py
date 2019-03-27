#
# template_type_symbol.py
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

from pynestml.symbols.type_symbol import TypeSymbol


class TemplateTypeSymbol(TypeSymbol):
    def __init__(self, i):
        super(TemplateTypeSymbol, self).__init__(name='_template_' + str(i))
        self.i = i

    def is_numeric(self):
        return False

    def is_primitive(self):
        return True

    def print_nestml_type(self):
        return '_template_' + str(self.i)

    def is_castable_to(self, _other_type):
        if isinstance(_other_type, TemplateTypeSymbol) and _other_type.i == self.i:
            return True

        return False

    def __eq__(self, other):
        if isinstance(other, TemplateTypeSymbol) and other.i == self.i:
            return True

        return False

