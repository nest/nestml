# -*- coding: utf-8 -*-
#
# PyNestMLLexerBase.py
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
from typing import TextIO
from antlr4 import *
from antlr4.Token import CommonToken

import sys
from typing import TextIO
import re

from pynestml.generated.PyNestMLParser import PyNestMLParser


class PyNestMLLexerBase(Lexer):
    def __init__(self, input: InputStream, output: TextIO = sys.stdout):
        super().__init__(input, output)
        self._lastToken = None
        self._opened = 0
        self._indents = []
        self._tokens = []

    @property
    def tokens(self):
        return self._tokens

    @tokens.setter
    def tokens(self, tokens):
        self._tokens = tokens

    @property
    def indents(self):
        return self._indents

    @indents.setter
    def indents(self, indents):
        self._indents = indents

    @property
    def opened(self):
        return self._opened

    @opened.setter
    def opened(self, value):
        self._opened = value

    @property
    def lastToken(self):
        return self._lastToken

    @lastToken.setter
    def lastToken(self, value):
        self._lastToken = value

    def reset(self):
        super().reset()
        self.tokens = []
        self.indents = []
        self.opened = 0
        self.lastToken = None

    def emitToken(self, t):
        super().emitToken(t)
        self.tokens.append(t)

    def nextToken(self):
        if self._input.LA(1) == Token.EOF and self.indents:
            for i in range(len(self.tokens) - 1, -1, -1):
                if self.tokens[i].type == Token.EOF:
                    self.tokens.pop(i)
            self.emitToken(self.commonToken(PyNestMLParser.NEWLINE, '\n'))
            while self.indents:
                self.emitToken(self.createDedent())
                self.indents.pop()
            self.emitToken(self.commonToken(PyNestMLParser.EOF, "<EOF>"))
        next_token = super().nextToken()
        if next_token.channel == Token.DEFAULT_CHANNEL:
            self.lastToken = next_token
        return next_token if not self.tokens else self.tokens.pop(0)

    def createDedent(self):
        dedent = self.commonToken(PyNestMLParser.DEDENT, "")
        dedent.line = self.lastToken.line
        return dedent

    def commonToken(self, type, text, indent=0, channel=None):
        stop = self.getCharIndex() - 1 - indent
        start = (stop - len(text) + 1) if text else stop
        if not channel:
            channel = super().DEFAULT_TOKEN_CHANNEL
        return CommonToken(self._tokenFactorySourcePair, type, channel, start, stop)

    @staticmethod
    def getIndentationCount(spaces):
        count = 0
        for ch in spaces:
            if ch == '\t':
                count += 8 - (count % 8)
            else:
                count += 1
        return count

    def atStartOfInput(self):
        return Lexer.column.fget(self) == 0 and Lexer.line.fget(self) == 1

    def onNewLine(self):
        tempt = Lexer.text.fget(self)
        newLine = re.sub("[^\r\n\f]+", "", tempt)
        spaces = re.sub("[\r\n\f]+", "", tempt)
        la_char = ""
        try:
            la = self._input.LA(1)
            la_char = chr(la)  # Python does not compare char to ints directly
        except ValueError:  # End of file
            pass
        # Strip newlines inside open clauses except if we are near EOF. We keep NEWLINEs near EOF to
        # satisfy the final newline needed by the single_put rule used by the REPL.
        try:
            nextnext_la = self._input.LA(2)
            nextnext_la_char = chr(nextnext_la)
        except ValueError:
            nextnext_eof = True
        else:
            nextnext_eof = False
        if self.opened > 0 or nextnext_eof is False and (
                la_char == '\r' or la_char == '\n' or la_char == '\f' or la_char == '#'):
            # Emit a newline token but in the comments channel (2).
            # This newline is used as a separator between comments while parsing.
            indent = self.getIndentationCount(spaces)
            self.emitToken(self.commonToken(PyNestMLParser.NEWLINE, newLine, indent=indent, channel=2))
        else:
            indent = self.getIndentationCount(spaces)
            previous = self.indents[-1] if self.indents else 0
            self.emitToken(self.commonToken(self.NEWLINE, newLine, indent=indent))  # NEWLINE is actually the '\n' char
            if indent == previous:
                self.skip()
            elif indent > previous:
                self.indents.append(indent)
                self.emitToken(self.commonToken(PyNestMLParser.INDENT, spaces))
            else:
                while self.indents and self.indents[-1] > indent:
                    self.emitToken(self.createDedent())
                    self.indents.pop()
