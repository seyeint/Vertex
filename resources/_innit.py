import os
import pickle
import random
import pandas as pd

path_win = "fill"
path_mac = "fill"

if os.name == 'nt':
    path = path_win
else:
    path = path_mac

initial_date = 1568246400  # Thursday, 12 September 2019 00:00:00
final_date = 1688947200  # Monday, 10 July 2023 00:00:00
cycle = 3  # Number of days per trading session
trade_ranges = [initial_date]

while initial_date + 86400*cycle < final_date:
    initial_date += 86400*cycle
    trade_ranges.append(initial_date)

"""Quick check."""
random.shuffle(trade_ranges)
print((final_date-1568246400)/(86400*3), len(trade_ranges)-1, trade_ranges[-4:])


with open(path+"trading_cycles_3d", "wb") as file:
    pickle.dump(trade_ranges, file)

progress = []
with open(path+"progress_cycles_3d", "wb") as file:
    pickle.dump(progress, file)

results = pd.DataFrame(columns=['date', 'direction', 'entry', 'tp', 'sl', 'lc', 'win'])
results.to_csv(path+"results.csv")

