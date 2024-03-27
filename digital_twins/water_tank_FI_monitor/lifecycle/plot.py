from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

# Plot results with FI
df0 = read_csv('/workspace/examples/data/water_tank_FI_monitor/output/outputs.csv')
df0.fillna(0, inplace=True)
fig, ax = plt.subplots(1, sharex=False, sharey=False)
name1='{x2}.tank.level'
name4='{x2}.tank.valvecontrol'
ax.title.set_text('tank level - FI')
ax.plot(df0['time'], df0[name1])
ax.plot(df0['time'], df0[name4])
plt.yticks(np.arange(0.0, 9.2, 1.0))
ax.set_xlim([0, 40])
ax.grid()
fig.tight_layout()
plt.rcParams['figure.figsize'] = [12, 10]
#plt.show()
plt.savefig('resultFI.png')