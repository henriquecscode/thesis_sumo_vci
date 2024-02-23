import sumolib
import os
import lxml.etree as ET
from collections.abc import Iterable

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

def create_additionals_root() -> ET.ElementTree:
    # <additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">

    NSMAP = {
        None: "http://sumo.dlr.de/xsd/additional_file.xsd",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance"
    }
    tree = ET.ElementTree(ET.Element("additional", nsmap=NSMAP))
    root = tree.getroot()
    return root


# Takes a iterable of ids and returns a string with the ids separated by commas (as required for configs)
def get_edges_list_str(edges_ids: Iterable[str]) -> str:
    if len(edges_ids) == 0:
        return "\"\""
    return ",".join(edges_ids)