# -*- coding: utf-8 -*-
#
# replace_import.py
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
import re

lexer_file = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "generated", "PyNestMLLexer.py")))
import_str = "from pynestml.generated.PyNestMLLexerBase import PyNestMLLexerBase"
with open(lexer_file) as f:
    content = f.read()
    content = re.sub(r"if __name__.*\n[ ]+.*\nelse:\n[ ]+.*PyNestMLLexerBase", import_str, content)
    f.close()

with open(lexer_file, "w") as f:
    f.write(content)
