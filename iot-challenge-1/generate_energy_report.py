#! /usr/bin/env python3

from pathlib import Path
import argparse
import csv
import math
import pandas as pd

# configurable parametres
parser = argparse.ArgumentParser(description='Generate energy report from timing log and power measurements.')
parser.add_argument('--deep_sleep_s', type=float, default=5.2, required=False, help='Deep sleep time in seconds (default: 5.2)')
parser.add_argument('--max_tx_power', action='store_true', default=False, required=False, help='Use maximum transmission power (19.5 dBm) instead of 2 dBm')
args = parser.parse_args()
max_tx_power = args.max_tx_power
deep_sleep_us = args.deep_sleep_s * 1e6

# initialization
timing_avgs_us = {"Idle": 0.0, "Sensing": 0.0, "WiFi": 0.0, "TX2dBm" if not max_tx_power else "TX19.5dBm": 0.0, "Deep sleep": deep_sleep_us}
battery_energy_mJ = 17147 * 1e3

# power estimation
sensor_read_df = pd.read_csv(Path('./samples/sensor_read.csv'), parse_dates=["Timestamp"], index_col="Timestamp")
tx_power_df = pd.read_csv(Path('./samples/sender.csv'), parse_dates=["Timestamp"], index_col="Timestamp")
deep_sleep_df = pd.read_csv(Path('./samples/deep_sleep.csv'), parse_dates=["Timestamp"], index_col="Timestamp")

power_avgs_mW = {
    "Idle": pd.concat([sensor_read_df[sensor_read_df < 300], deep_sleep_df[(deep_sleep_df > 100) & (deep_sleep_df < 300)]], ignore_index=True).mean().item(),
    "Sensing": sensor_read_df[sensor_read_df > 300].mean().item(),
    "WiFi": pd.concat([tx_power_df[tx_power_df < 610], deep_sleep_df[(deep_sleep_df > 600) & (deep_sleep_df < 610)]], ignore_index=True).mean().item(),
    "TX2dBm" if not max_tx_power else "TX19.5dBm": tx_power_df[(tx_power_df > 610) & (tx_power_df < 630)].mean().item() if not max_tx_power else tx_power_df[tx_power_df > 630].mean().item(),
    "Deep sleep": deep_sleep_df[deep_sleep_df < 150].mean().item()
}

# timing estimation
count = 0
with open('timing_log.csv', mode='r') as file:
    dict_reader = csv.DictReader(file)
    for row in dict_reader:
        idle_time_us = (int(row["Sensing_start"]) - int(row["Idle1_start"])) + (int(row["WiFi_start"]) - int(row["Idle2_start"])) + (int(row["Deep_sleep_start"]) - int(row["Idle3_start"]))
        sensing_time_us = (int(row["Idle2_start"]) - int(row["Sensing_start"]))
        wifi_time_us = (int(row["TX_start"]) - int(row["WiFi_start"]))
        tx_time_us = (int(row["Idle3_start"]) - int(row["TX_start"]))
        timing_avgs_us["Idle"] = (timing_avgs_us["Idle"] * count + idle_time_us) / (count + 1)
        timing_avgs_us["Sensing"] = (timing_avgs_us["Sensing"] * count + sensing_time_us) / (count + 1)
        timing_avgs_us["WiFi"] = (timing_avgs_us["WiFi"] * count + wifi_time_us) / (count + 1)
        timing_avgs_us["TX2dBm" if not max_tx_power else "TX19.5dBm"] = (timing_avgs_us["TX2dBm" if not max_tx_power else "TX19.5dBm"] * count + tx_time_us) / (count + 1)
        count += 1
cycle_time_avg_us = sum(timing_avgs_us.values())

# overall analysis
cycle_power_avg_mW = sum(power_avgs_mW[i] * timing_avgs_us[i] for i in timing_avgs_us) / sum(timing_avgs_us.values())
energy_avgs_mJ = {i: timing_avgs_us[i] * power_avgs_mW[i] / 1e6 for i in timing_avgs_us}
cycle_energy_avg_mJ = sum(energy_avgs_mJ.values())
cycles_per_battery = math.floor(battery_energy_mJ / cycle_energy_avg_mJ)
battery_life_s = cycles_per_battery * cycle_time_avg_us / 1e6
battery_life_d = cycles_per_battery * cycle_time_avg_us / (1e6 * 60 * 60 * 24)

print(f'TIMING:')
for time in timing_avgs_us:
    print(f'{time} = {timing_avgs_us[time]:.3f} us')
print(f'CYCLE = {cycle_time_avg_us:.3f} us')

print()

print (f'POWER CONSUMPTION:')
for power in power_avgs_mW:
    print(f'{power} = {power_avgs_mW[power]:.3f} mW')
print(f'CYCLE = {cycle_power_avg_mW:.3f} mW')

print()

print(f'ENERGY CONSUMPTION:')
for energy in energy_avgs_mJ:
    print(f'{energy} = {energy_avgs_mJ[energy]:.3f} mJ')
print(f'CYCLE = {cycle_energy_avg_mJ:.3f} mJ')

print()

print(f'BATTERY LIFE ESTIMATION:')
print(f'Battery energy = {battery_energy_mJ / 1e3:.3f} J')
print(f'Cycles per battery = {cycles_per_battery}')
print(f'Battery life = {battery_life_s:.3f} s ({battery_life_d:.3f} days)')