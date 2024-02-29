# Takes a network and a set of edges
# Outputs an additional file with rerouters at those edges
import argparse
import os
import sumolib
import lxml.etree as ET
from src.VCI.utils.sumo_lib_net import get_net_file
from src.VCI.utils.path_utils import true_basename
from src.VCI.utils.datetime_utils import get_current_time_file_format
import pandas as pd
from src.VCI.utils.sumo_lib_net import create_additionals_root
from src.VCI.utils.xml_utils import write_root

DEFAULT_SUMO_NET_FILE = "networks\\filter_by_edge.net.xml"
DEFAULT_NETWORK_CHOICE_EDGES_FILE = "networks\\filter_by_edge_network_choice_edges.txt"
DEFAULT_SUMO_ADDITIONALS_FILE = "networks\\filter_by_edge.add.xml"
NETWORK_ADDITIONALS_FILENAME_SUFFIX = "_choice_edges_rerouters"
def main(root: ET.Element, net: sumolib.net.Net, edges: set[sumolib.net.edge.Edge], *args, **kwargs) -> ET.Element:
    for edge in edges:
        rerouter = get_edge_rerouter_element(edge)
        root.append(rerouter)
        
    return root

def get_edge_rerouter_element(edge:sumolib.net.edge.Edge, *args, **kwargs) -> ET.Element:
    edge_id = edge.getID()
    rerouter_id = f"rr_{edge_id}"
    edge_pos = edge.getShape()[0]
    x,y = edge_pos
    rerouter_pos = f"{x},{y}"
    rerouter = ET.Element("rerouter")
    rerouter.set("id", rerouter_id)
    rerouter.set("edges", edge_id)
    rerouter.set("pos", rerouter_pos)
    return rerouter

def parse_arguments():
    parser = argparse.ArgumentParser(description='Description of your script')

    # Add command line arguments
    parser.add_argument('--sumo-net-file', '-s', type=str, help='Path to the SUMO network file')
    parser.add_argument('--network-choice-edges-file', type=str, help='Path to the network choice edges file')
    parser.add_argument("--output", "-o", type=str, help="Path to the output file")
    parser.add_argument('--network-additionals-file', type=str, help='Path to the network additionals file')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite the input network additionals file. Ignore Output argument')
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    
    args = parse_arguments()


    if args.sumo_net_file is None:
        sumo_net_file = DEFAULT_SUMO_NET_FILE
    else:
        sumo_net_file = args.sumo_net_file

    if args.network_choice_edges_file is None:
        network_choice_edges_file = DEFAULT_NETWORK_CHOICE_EDGES_FILE
    else:
        network_choice_edges_file = args.network_choice_edges_file

    if args.network_additionals_file is None:
        network_additionals_file = DEFAULT_SUMO_ADDITIONALS_FILE
        root = create_additionals_root()

    else:
        network_additionals_file = args.network_additionals_file
        parser = ET.XMLParser(remove_blank_text=True)
        root = ET.parse(args.network_additionals_file, parser).getroot()


    if args.overwrite and args.network_additionals_file is not None:
            output_file = network_additionals_file
    else:
        if args.output is None:
            sumo_net_file_path = os.path.dirname(sumo_net_file)
            sumo_net_file_truebasename, sumo_net_file_extension = true_basename(sumo_net_file)
            output_time = get_current_time_file_format()
            output = os.path.join(sumo_net_file_path, f"{sumo_net_file_truebasename}{NETWORK_ADDITIONALS_FILENAME_SUFFIX}_{output_time}.add.xml")
        else:
            output = args.output

    # Call the main function with parsed arguments
    net = get_net_file(sumo_net_file)
    with open (network_choice_edges_file, "r") as f:
        edges_ids = f.read().splitlines()

    edges = {net.getEdge(edge_id) for edge_id in edges_ids}
    
    root = main(root, net, edges, args)

    # Save to mem
    write_root(root, output)