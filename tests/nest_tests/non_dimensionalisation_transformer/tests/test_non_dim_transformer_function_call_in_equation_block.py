# -*- coding: utf-8 -*-
#
# test_non_dim_transformer_function_call_in_equation_block.py
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

# parameters (SI)
params = {
    "tau_m": 12.85e-3,  # membrane time constant (s)
    "alpha_exp": 2 / 70e6,  # exponential factor (1/V)
    "V_rest": -65e-3,  # resting potential (V)
}

V_m0 = -70e-3  # start 5mV below rest

tau_eff = params["tau_m"] * (1 + np.exp(params["alpha_exp"] * params["V_rest"]))


# ODE
def neuron_ode(t, v):
    return -v / tau_eff


# simulation: 0–50ms
t_span = (0.0, 0.05)  # s
t_eval = np.linspace(*t_span, 1001)

# sol = solve_ivp(neuron_ode, t_span, [V_m0],
#                 t_eval=t_eval, rtol=1e-9, atol=1e-12)
sol = solve_ivp(neuron_ode, t_span, [V_m0], t_eval=t_eval, rtol=1e-6, atol=1e-6)

# checkpoints
check_times_ms = np.array([25, 50])  # ms
check_idx = [np.argmin(np.abs(t_eval * 1e3 - ct)) for ct in check_times_ms]
check_vm_mV = sol.y[0, check_idx] * 1e3  # mV

# plot
plt.figure(figsize=(8, 5))

# membrane‑potential trace
plt.plot(t_eval * 1e3, sol.y[0] * 1e3, label="numeric (solve_ivp)")

# Xs at checkpoints
plt.plot(
    check_times_ms,
    check_vm_mV,
    "x",
    markersize=9,
    markeredgewidth=2,
    label="checkpoints",
)

# annotate Xs with their values
for t, v in zip(check_times_ms, check_vm_mV):
    offset = 2 if v > 0 else -2
    plt.text(
        t,
        v + offset,
        f"{v:+.2f}mV",
        ha="center",
        va="bottom" if v > 0 else "top",
        fontsize=9,
    )

plt.xlabel("Time (ms)")
plt.ylabel("Membrane potential (mV)")
plt.title("50ms leak‑decay reference")
plt.grid(alpha=0.6, linestyle="--")
plt.legend()
plt.tight_layout()
plt.savefig("reference_test_non_dim_transformer_function_call_in_equation_block.png")
print("test")
