"""
/*
 *  PredefinedFunctions.py
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
 @author kperun
"""


class PredefinedFunctions:
    """
    This class is used to represent all predefined functions of NESTML.
    """
    __TIME_RESOLUTION = 'resolution'
    __TIME_STEPS = 'steps'
    __EMIT_SPIKE = 'emit_spike'
    __PRINT = 'print'
    __PRINTLN = 'println'
    __POW = 'pow'
    __EXP = 'exp'
    __LOG = 'log'
    __LOGGER_INFO = 'info'
    __LOGGER_WARNING = 'warning'
    __RANDOM = 'random'
    __RANDOM_INT = 'randomInt'
    __EXPM1 = 'expm1'
    __DELTA = 'delta'
    __MAX = 'max'
    __BOUNDED_MAX = 'bounded_max'
    __MIN = 'min'
    __BOUNDED_MIN = 'bounded_min'
    __INTEGRATE_ODES = 'integrate_odes'
    __CURR_SUM = 'curr_sum'
    __COND_SUM = 'cond_sum'
