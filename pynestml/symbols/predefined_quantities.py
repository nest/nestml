# -*- coding: utf-8 -*-
#
# predefined_quantities.py
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

from typing import Dict, Iterable, List, Optional, Tuple, Union

import re

from astropy import units as u

from pynestml.utils.messages import MessageCode, Messages


class InvalidQuantityException(Exception):
    r"""
    Raised when a physical quantity expression (such as ``"conductance / time"``) cannot be interpreted.

    :param code: the message code describing the problem
    :param message: a human-readable description of the problem
    """

    def __init__(self, code: MessageCode, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class PredefinedQuantities:
    r"""
    The physical quantities that can be used to declare the type of a variable, for instance ``V_m "voltage" = -70 mV``.

    A quantity only fixes the physical dimension of a variable, not its unit: ``"voltage"`` is equally well satisfied by ``-70 mV`` as by ``-0.07 V``. Internally, each quantity is represented by its coherent SI unit (``V`` for ``"voltage"``); as types only compare dimensions, the choice of unit here does not imply any particular magnitude.

    Quantities can be combined into expressions using ``*``, ``/`` and ``**``, mirroring the syntax of physical units, for instance ``"conductance / time"``, ``"1 / time"``, ``"time**-(1/2)"`` or ``"(amount of substance)**2"``. Quantity names can consist of several words separated by spaces.
    """

    # canonical quantity names and their aliases, each mapped to the coherent SI unit that represents its dimension
    _QUANTITIES: List[Tuple[Tuple[str, ...], u.UnitBase]] = [
        # SI base quantities
        (("time",), u.s),
        (("length",), u.m),
        (("mass",), u.kg),
        (("current", "electrical current", "electric current"), u.A),
        (("temperature",), u.K),
        (("amount of substance",), u.mol),
        (("luminous intensity",), u.cd),
        # derived quantities
        (("frequency",), u.Hz),
        (("voltage", "electrical potential", "electric potential"), u.V),
        (("charge", "electrical charge", "electric charge"), u.C),
        (("resistance", "electrical resistance"), u.Ohm),
        (("conductance", "electrical conductance"), u.S),
        (("capacitance", "electrical capacitance"), u.F),
        (("inductance",), u.H),
        (("magnetic flux",), u.Wb),
        (("magnetic flux density",), u.T),
        (("force",), u.N),
        (("energy",), u.J),
        (("power",), u.W),
        (("pressure",), u.Pa),
        (("area",), u.m**2),
        (("volume",), u.m**3),
        (("velocity", "speed"), u.m / u.s),
        (("acceleration",), u.m / u.s**2),
        (("concentration", "molar concentration"), u.mol / u.m**3),
    ]

    name2unit: Dict[str, u.UnitBase] = {}

    @classmethod
    def register_quantities(cls) -> None:
        cls.name2unit = {}
        for names, unit in cls._QUANTITIES:
            for name in names:
                cls.name2unit[name] = unit

    @classmethod
    def get_quantity_names(cls) -> Iterable[str]:
        if not cls.name2unit:
            cls.register_quantities()

        return cls.name2unit.keys()

    @classmethod
    def is_quantity(cls, name: str) -> bool:
        return cls._normalise_name(name) in cls.get_quantity_names()

    @classmethod
    def get_unit(cls, name: str) -> Optional[u.UnitBase]:
        r"""
        Returns the coherent SI unit representing the dimension of the quantity with the given name, or None if the name is not a known quantity.
        """
        if not cls.is_quantity(name):
            return None

        return cls.name2unit[cls._normalise_name(name)]

    @classmethod
    def parse(cls, quantity_str: str) -> u.UnitBase:
        r"""
        Interpret a quantity expression, such as ``"conductance / time"``, and return the coherent SI unit that represents its dimension (in this example, S/s).

        :param quantity_str: the quantity expression (without the enclosing double quotes)
        :raises InvalidQuantityException: if the expression cannot be interpreted
        """
        return _QuantityExpressionParser(quantity_str).parse()

    @staticmethod
    def _normalise_name(name: str) -> str:
        return " ".join(name.split())


class _QuantityExpressionParser:
    r"""
    Recursive-descent parser for quantity expressions. The grammar mirrors that of unit types (``unitType`` in the parser grammar):

    .. code::

       expr     : term (("*" | "/") term)*
       term     : factor ("**" exponent)?
       factor   : "(" expr ")" | NAME | NUMBER
       exponent : ("+" | "-")? (NUMBER | "(" NUMBER "/" NUMBER ")")

    where NAME is a quantity name, possibly consisting of several words separated by whitespace. The only number that is allowed as a factor is 1, as in ``"1 / time"``.
    """

    _TOKEN_REGEX = re.compile(r"\s*(?:(?P<number>(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)"
                              r"|(?P<name>[A-Za-z_]\w*(?:\s+[A-Za-z_]\w*)*)"
                              r"|(?P<op>\*\*|[*/()+-]))")

    def __init__(self, quantity_str: str):
        self.quantity_str = quantity_str
        self.tokens = self._tokenize(quantity_str)
        self.pos = 0

    def _error(self, reason: str) -> InvalidQuantityException:
        code, message = Messages.get_invalid_quantity(self.quantity_str, reason)
        return InvalidQuantityException(code, message)

    def _tokenize(self, s: str) -> List[Tuple[str, str]]:
        tokens = []
        pos = 0
        s = s.rstrip()
        while pos < len(s):
            match = self._TOKEN_REGEX.match(s, pos)
            if match is None or match.end() == pos:
                raise self._error("unexpected character \"" + s[pos:].lstrip()[0] + "\"")

            kind = match.lastgroup
            tokens.append((kind, match.group(kind)))
            pos = match.end()

        if not tokens:
            raise self._error("empty quantity")

        return tokens

    def _peek(self) -> Optional[Tuple[str, str]]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]

        return None

    def _peek_op(self, *ops: str) -> bool:
        token = self._peek()
        return token is not None and token[0] == "op" and token[1] in ops

    def _next(self) -> Tuple[str, str]:
        token = self._peek()
        if token is None:
            raise self._error("unexpected end of expression")

        self.pos += 1
        return token

    def _expect_op(self, op: str) -> None:
        kind, value = self._next()
        if kind != "op" or value != op:
            raise self._error("expected \"" + op + "\" but found \"" + value + "\"")

    def parse(self) -> u.UnitBase:
        unit = self._parse_expr()
        if self._peek() is not None:
            raise self._error("unexpected \"" + self._peek()[1] + "\"")

        return unit

    def _parse_expr(self) -> u.UnitBase:
        unit = self._parse_term()
        while self._peek_op("*", "/"):
            _, op = self._next()
            rhs = self._parse_term()
            unit = unit * rhs if op == "*" else unit / rhs

        return unit

    def _parse_term(self) -> u.UnitBase:
        unit = self._parse_factor()
        if self._peek_op("**"):
            self._next()
            unit = unit ** self._parse_exponent()

        return unit

    def _parse_factor(self) -> Union[u.UnitBase, int]:
        kind, value = self._next()
        if kind == "op" and value == "(":
            unit = self._parse_expr()
            self._expect_op(")")
            return unit

        if kind == "name":
            unit = PredefinedQuantities.get_unit(value)
            if unit is None:
                code, message = Messages.get_unknown_quantity(PredefinedQuantities._normalise_name(value), self.quantity_str)
                raise InvalidQuantityException(code, message)

            return unit

        if kind == "number":
            if float(value) != 1:
                code, message = Messages.get_wrong_numerator(self.quantity_str)
                raise InvalidQuantityException(code, message)

            return u.dimensionless_unscaled

        raise self._error("unexpected \"" + value + "\"")

    def _parse_exponent(self) -> float:
        sign = 1
        if self._peek_op("+", "-"):
            _, op = self._next()
            sign = -1 if op == "-" else 1

        if self._peek_op("("):
            self._next()
            num = self._expect_number()
            self._expect_op("/")
            den = self._expect_number()
            self._expect_op(")")
            return sign * num / den

        return sign * self._expect_number()

    def _expect_number(self) -> float:
        kind, value = self._next()
        if kind != "number":
            raise self._error("expected a number but found \"" + value + "\"")

        return float(value)
