import argparse
import random
import time

from pythonosc import udp_client

def initialize():
    port = 7400
    ip_address = "10.132.242.3"

    client = udp_client.SimpleUDPClient(ip_address, port)
    return client

def send_data_to_server(client, point_array):
# new_entry = {
#                             "triggered": triggered,
#                             "position": position.tolist(),
#                             "acceleration" : acceleration,
#                             "dimensions": dimensions.tolist(),
#                             "head_position": head_pos.tolist(),                    
#                             }

    position_x, position_z = point_array.get("position_unit_space")
    em1 = float(point_array.get("head_position"))
    em2 = point_array.get("acceleration")
    em2 = float(em2)
    print(position_x, position_z, em1, em2)

    client.send_message("/position_x", position_x)
    client.send_message("/position_z", position_z)
    client.send_message("/em1", em1)
    client.send_message("/em2", em2)