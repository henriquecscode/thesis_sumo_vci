import sumolib
import os

def get_net_file(sumo_net_file: str) -> sumolib.net.Net:
    if not os.path.exists(sumo_net_file):
        raise FileNotFoundError(f"File {sumo_net_file} does not exist")
    net = sumolib.net.readNet(sumo_net_file)
    return net

def is_dead_end_junction(junction: sumolib.net.node.Node) -> bool:
    return junction.getType() == 'dead_end'

def is_entry_junction(junction: sumolib.net.node.Node) -> bool:
    return len(junction.getIncoming()) == 0

def is_exit_junction(junction: sumolib.net.node.Node) -> bool:
    return len(junction.getOutgoing()) == 0