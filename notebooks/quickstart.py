#! /usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

from pymt.models import Hydrotrend


model = Hydrotrend()

cfg_file, cfg_dir = model.setup()
model.initialize(cfg_file, cfg_dir)

model.time

model.update()
model.time

model.time_units

for var in model.get_output_var_names():
    print(var)

discharge_sn = 'channel_exit_water__volume_flow_rate'
model.get_value(discharge_sn)

model.get_var_units(discharge_sn)

n_steps = int(model.end_time / model.time_step) - 1
discharge = np.empty(n_steps)
for t in range(n_steps):
    discharge[t] = model.get_value(discharge_sn)
    model.update()

model.finalize()

plt.plot(discharge, 'b')
plt.title('Mean Daily Discharge at River Mouth')
plt.xlabel('Simulation Time (d)')
plt.ylabel('Discharge ($m^3 s^{-1}$)')

plt.show()
