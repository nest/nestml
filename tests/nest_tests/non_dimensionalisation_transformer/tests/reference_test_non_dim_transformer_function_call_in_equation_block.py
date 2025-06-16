# -*- coding: utf-8 -*-
#
# test_non_dimensionalisation_transformer.py
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


import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Adjusted parameters for practical simulation (using SI units: V, A, F, s)
params = {
    'V_m_init': -65e-3,      # Initial membrane potential (V)
    'C_exp_0': 150e-12,      # Capacitance (F)
    'tau_m': 2e-3,           # Time constant (s)
    'alpha_exp': 2 / (3e6),  # Exponential factor (per V)
    'I_foo': 200e-12         # Constant current: 200 pA
}

# Initial state
V_m0 = -70e-3  # Initial membrane potential (V)

# Compute the constant denominator term
denom = params['I_foo'] * (1 + np.exp(params['alpha_exp'] * params['V_m_init']))
# Compute the coefficient k for the ODE: dV_m/dt = k * V_m
k = params['C_exp_0'] / (params['tau_m'] * denom)

# ODE function
def neuron_ode(t, V_m):
    return k * V_m

# Time span for simulation (0 to 20 ms)
t_span = (0, 0.02)  # 20 ms in seconds
t_eval = np.linspace(t_span[0], t_span[1], 500)

# Solve the ODE
sol = solve_ivp(neuron_ode, t_span, [V_m0], t_eval=t_eval)

# Convert results to mV and ms for plotting
V_m_mV = sol.y[0] * 1e3  # Convert V to mV
time_ms = sol.t * 1e3     # Convert s to ms

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(time_ms, V_m_mV, 'b-', linewidth=2)
plt.title('Reference for Non-Dimensionalisation-Transformer test_exp_in_equationblock')
plt.xlabel('Time (ms)')
plt.ylabel('Membrane Potential (mV)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()
print('test')