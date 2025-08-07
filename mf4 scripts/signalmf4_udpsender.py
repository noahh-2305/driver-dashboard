import socket
from asammdf import MDF
import time
import json

#"signal_based_output_group3.mf4"
mdf = MDF("signal_based_output_group6.mf4")
print(mdf.channels_db.keys())

OilTemp_data = mdf.get("EngOilTemp_Cval")  
#add more of these as needed for each signal you want to send...


oiltempvalues = OilTemp_data.samples
#same thing here...


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = ('127.0.0.1', 6000)

# if you want to use multiple values you will zip all the values together in a tuple and then access them like that
for value1 in oiltempvalues:
    packet_dict = {
            'EngOilTemp_Cval': float(value1),
        }
    message = json.dumps(packet_dict).encode()
    print(f"Sending {packet_dict} to Local Host")
    sock.sendto(message, address)