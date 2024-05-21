from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

# Plot results with FI
df0 = read_csv('/workspace/examples/data/mass-spring-damper-monitor/output/outputs.csv')
df0.fillna(0, inplace=True)
fig, ax = plt.subplots(1, sharex=False, sharey=False)
name1='{msd1}.msd1i.x1'
name2='{msd2}.msd2i.x2'
monitor='{m2}.monitor._output'
ax.title.set_text('Mass spring dumper with monitor')
ax.plot(df0['time'], df0[name1] - df0[name2], color='tab:blue',
        label='msd1i.x1 - msd2i.x2')
ax.plot(df0['time'], df0[monitor], color='tab:green', label='monitor output')
ax.plot(df0['time'], [1] * len(df0['time']), '--', color='tab:red',
        label='monitor threshold')
# plt.yticks(np.arange(0.0, 9.2, 1.0))
# ax.set_xlim([0, 40])
ax.grid()
fig.tight_layout()
plt.legend()
plt.rcParams['figure.figsize'] = [12, 10]
#plt.show()
plt.savefig('resultWT_mon.png')