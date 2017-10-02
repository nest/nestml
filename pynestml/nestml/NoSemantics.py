#
# NoSemantics.py
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

"""
Placeholder for expression productions that are not implemented
"""
from pynestml.nestml.ErrorStrings import ErrorStrings
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.Either import Either
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class NoSemantics(NESTMLVisitor):
    def visitExpression(self, _expr=None):
        errorMsg = ErrorStrings.messageNoSemantics(self, _expr.printAST, _expr.getSourcePosition())
        _expr.setTypeEither(Either.error(errorMsg))
        # just warn though
        Logger.logMessage(errorMsg, LOGGING_LEVEL.WARNING)
        return
