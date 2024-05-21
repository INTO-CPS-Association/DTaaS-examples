from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

# Plot results with FI
df0 = read_csv('/workspace/examples/data/incubator-NuRV-monitor-validation/output/outputs.csv')
df0.fillna(0, inplace=True)
fig, ax = plt.subplots(1, sharex=False, sharey=False)
# sensor='{src}.src.sensor_data'
sensor='{src}.src.sensor_data'
estimate='{src}.src.kalman_input'
target='{es}.es.ctrl_desired_temperature'
monitor='{mon}.mon._output'
ax.title.set_text('Incubator Validation')
ax.plot(df0['time'], df0[sensor], color='tab:blue', label='temperature sensor')
ax.plot(df0['time'], df0[estimate], color='tab:orange', label='temperature estimate')
ax.plot(df0['time'], df0[monitor], color='tab:green', label='monitor output')
ax.plot(df0['time'], df0[target], '--', color='tab:red',
        label='desired temperature')
ax.grid()
ax.set_xlim([0, 100])
fig.tight_layout()
plt.rcParams['figure.figsize'] = [12, 10]
plt.legend()
#plt.show()
plt.savefig('resultIV.png')