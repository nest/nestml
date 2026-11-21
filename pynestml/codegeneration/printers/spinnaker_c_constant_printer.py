# -*- coding: utf-8 -*-
#
# spinnaker_c_constant_printer.py
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

from typing import Union

from pynestml.codegeneration.printers.constant_printer import ConstantPrinter


class SpinnakerCConstantPrinter(ConstantPrinter):
    r"""
    Constant printer for SpiNNaker C code, in which ``REAL`` is the S16.15 fixed-point type ``accum``.

    In C, an unsuffixed floating-point literal such as ``0.`` is a ``double``. Combining it with an ``accum`` operand promotes the whole (sub)expression to ``double``. The ARM968 has no FPU, so this results in calls to software floating-point routines (``__gnu_fractsadf``, ``__aeabi_dcmpgt``, ``__aeabi_dsub``, ``__gnu_fractdfsa``, ...) instead of plain integer instructions.

    This printer therefore prints floating-point constants as ``accum`` literals (with a ``k`` suffix, like sPyNNaker's ``REAL_CONST(x)``), but only if they are exactly representable in S16.15 format (e.g. ``0``, ``1``, ``0.5``, ``1000``). Other constants (e.g. ``0.001``, which would be rounded by up to half an LSB = 2**-16, or ``1E6``, which is out of range) are printed as ``double`` as before, so that numerical results do not change.
    """

    ACCUM_FRACTIONAL_BITS = 15
    ACCUM_MIN = -2.**16
    ACCUM_MAX = 2.**16 - 2.**-ACCUM_FRACTIONAL_BITS

    @classmethod
    def is_exactly_representable_as_accum(cls, value: float) -> bool:
        return cls.ACCUM_MIN <= value <= cls.ACCUM_MAX and (value * 2.**cls.ACCUM_FRACTIONAL_BITS).is_integer()

    def print_constant(self, node: Union[str, float, int]) -> str:
        if isinstance(node, float) and self.is_exactly_representable_as_accum(node):
            # ``repr()`` gives the shortest decimal string that round-trips to the same double; as any S16.15 value is exactly representable as a double, this is the exact value (as opposed to the base class' fixed number of significant digits, which might round to a neighbouring accum value)
            printed = repr(node)
            assert "inf" not in printed and "nan" not in printed
            if not any(c in printed for c in ".eE"):
                printed += "."
            return printed + "k"

        return super().print_constant(node)
