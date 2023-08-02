import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

font = {'font.family' : 'monospace',
        'font.weight' : 'bold',
        'axes.titlesize'   : 18,
        'axes.labelsize'   : 14,
        'legend.fontsize' : 10,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
       }

plt.rcParams.update(font)
df_cosim = pd.read_csv("/workspace/data/flex-cell/output/outputs.csv")
df_kuka = pd.read_csv("/workspace/data/flex-cell/output/physical_twin/kukalbriiwa7_actual.csv")
df_ur5e = pd.read_csv("/workspace/data/flex-cell/output/physical_twin/ur5e_actual.csv",sep=" ")


fig, axes = plt.subplots(2,2, figsize=(16,12))
plt.grid()
plt.subplot(2,2,1)
df_cosim.plot(x = "time",y = ["{ur5e}.ur5e.actual_q0","{ur5e}.ur5e.actual_q1",
                                    "{ur5e}.ur5e.actual_q2","{ur5e}.ur5e.actual_q3",
                                   "{ur5e}.ur5e.actual_q4","{ur5e}.ur5e.actual_q5"],
             figsize=(14,10),
             title = "Co-sim UR5e joints",
             ax=axes[0,0])
plt.xlabel('time [s]')
plt.ylabel('radians')
plt.grid()
plt.tight_layout()

plt.subplot(2,2,2)
df_cosim.plot(x = "time",y = ["{kuka}.kuka.actual_q0","{kuka}.kuka.actual_q1",
                                    "{kuka}.kuka.actual_q2","{kuka}.kuka.actual_q3",
                                   "{kuka}.kuka.actual_q4","{kuka}.kuka.actual_q5","{kuka}.kuka.actual_q6"],
             figsize=(14,10),
             title = "Co-sim Kuka lbr iiwa 7 joints",
             ax=axes[0,1])
plt.xlabel('time [s]')
plt.ylabel('radians')
plt.grid()
plt.tight_layout()

plt.subplot(2,2,3)
df_ur5e.plot(x = "timestamp",y = ["actual_q_0","actual_q_1",
                                    "actual_q_2","actual_q_3",
                                   "actual_q_4","actual_q_5"],
             figsize=(14,10),
             title = "Real UR5e joints",
             ax=axes[1,0])
plt.xlabel('timestamp')
plt.ylabel('radians')
plt.grid()
plt.tight_layout()

plt.subplot(2,2,4)
df_kuka.plot(x = "timestamp",y = ["actual_q_0","actual_q_1",
                                    "actual_q_2","actual_q_3",
                                   "actual_q_4","actual_q_5","actual_q_6"],
             figsize=(14,10),
             title = "Real Kuka lbr iiwa 7 joints",
             ax=axes[1,1])
plt.xlabel('timestamp')
plt.ylabel('radians')
plt.grid()
plt.tight_layout()
fig.savefig('/workspace/data/flex-cell/output/experiment_plot.pdf', dpi=300)
fig.savefig('/workspace/data/flex-cell/output/experiment_plot.png', dpi=300)