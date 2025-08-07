from asammdf import MDF, Signal
import cantools
import cantools.database

from collections import defaultdict
import numpy as np

mdf = MDF("ZZ5420_Data2_F019_2025-07-24_23-39-58.mf4")
db = cantools.database.load_file("CHASSIS_667kB_dbc_2024_20a.dbc")
#Using asammdf to take in the frame-based mf4 file and then cantools to take in the dbc file.

#.get helps us extract Signal objects from the loaded MDF file, such as CAN ID, CAN data length code, data bytes, and timestamps
ids = mdf.get('CAN_DataFrame.ID', group=3).samples.astype(int) # group=1 is specifying to use CAN group 1
dlcs = mdf.get('CAN_DataFrame.DLC', group=3).samples.astype(int)
data_bytes = mdf.get('CAN_DataFrame.DataBytes', group=3).samples
timestamps = mdf.get('t', group=3).samples


#--------- build a frame list to put together CAN IDs, timestamps, data length codes, and data bytes ------
frames = []
for i in range(len(timestamps)): 
    can_id = ids[i]
    dlc = dlcs[i]
    data = bytes(data_bytes[i][:dlc])
    frames.append((timestamps[i], can_id, data))
#----------------------------------------------------------------------------------------------------------
    
#------------  decoding using the dbc file -----------------
decoded_signals = []
for ts, can_id, data in frames:
    try:
        msg = db.get_message_by_frame_id(can_id) # try and get the message definition from dbc
        signals = msg.decode(data) # decode byte data into the signal's values
        decoded_signals.append((ts, signals)) # stored as (timestamp, {signal_name: value, ...})
    except Exception:# Frame not in DBC or decode error, skip as needed
        pass
#-----------------------------------------------------------

#------------ Group each value into a time series for its signal --------------
signal_times = defaultdict(list) # no key error will be raised, default to empty list
signal_values = defaultdict(list)

for ts, sig_dict in decoded_signals:
    for sig_name, val in sig_dict.items():
        signal_times[sig_name].append(ts)
        signal_values[sig_name].append(val)
#------------------------------------------------------------------------------

#------------ Convert into asammdf Signal objects --------------
signals = [] 
for sig_name in signal_times:
    times = np.array(signal_times[sig_name])
    values = np.array(signal_values[sig_name])
    
    # Sort time stamps to be in order
    sort_idx = np.argsort(times)
    times = times[sort_idx]
    values = values[sort_idx]

    sig = Signal(
        samples=values,
        timestamps=times,
        name=sig_name,
        unit=''  
    )
    if sig.samples.dtype == object:
    # Extract float values from NamedSignalValue objects, this is for any can signal that isn't a float already, need to figure that out in the future
        sig.samples = np.array([v.value if hasattr(v, 'value') else v for v in sig.samples], dtype=np.float64)

    signals.append(sig)
#---------------------------------------------------------------


new_mdf = MDF()
new_mdf.append(signals)
new_mdf.save('signal_based_output_group3.mf4')# generate a signal-based output file

