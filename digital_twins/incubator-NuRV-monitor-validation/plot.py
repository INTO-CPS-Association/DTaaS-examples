import pandas as pd
import matplotlib.pyplot as plt
import os

print("Creating data plots")

# Read the CSV file
CSV_PATH = '/workspace/examples/data/incubator-NuRV-monitor-validation/output/outputs.csv'
FIGS_PATH = '/workspace/examples/data/incubator-NuRV-monitor-validation/figs'

# Create the directory if it doesn't exist
if not os.path.exists(FIGS_PATH):
    os.makedirs(FIGS_PATH)

df = pd.read_csv(CSV_PATH)

time = df['time']
df = df.drop(columns=['time'])

for column_name in df.columns:
    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(time, df[column_name], linestyle='-', color='b')
    plt.title(column_name)
    plt.xlabel('Time')
    plt.ylabel(column_name)
    plt.grid(True)
    plt.savefig(f"{FIGS_PATH}/{column_name}.png", dpi=300, bbox_inches='tight')
    plt.close()

print(f"Data plots can be found in: {FIGS_PATH}")