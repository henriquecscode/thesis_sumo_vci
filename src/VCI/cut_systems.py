# This script takes the lanes with detectors and cuts them  from the network for the process of isolating the weakly connected components 
# These weakly connected components are the ones that are going to be subject to flow equations

import argparse
import os
import sumolib
import lxml.etree as ET
from src.VCI.utils.sumo_lib_net import get_net_file
from src.VCI.utils.path_utils import true_basename
from src.VCI.utils.datetime_utils import get_current_time_file_format
from src.VCI.utils.run import run_system

DEFAULT_SUMO_NET_FILE = "networks/filter_by_edge.net.xml"
DEFAULT_SYSTEMS_CUT_FILE = "network_configs/cut_edges.txt"
DEFAULT_CONFIG_FILE = "network_configs/raw.cfg"
SYSTEMS_FILENAME_SUFFIX = "_cut_systems"

def mydeb(id):
    if id in ["95984918", "390157775", "1093951608", "497924851", "915252791"]:
        pass
# Expands the set of edges to include the edges that are continuous to the ones in the set
# That means, there is a determinism in the flow of traffic
def get_continuous_edges(net: sumolib.net.Net, all_edges_ids: set[str], to_get_continuous_edges_ids: set[str], *args, **kwargs) -> set[str]:
    all_edges_ids = all_edges_ids.union(to_get_continuous_edges_ids)
    if len(to_get_continuous_edges_ids) == 0:
        return all_edges_ids
    found_continuous_edges = set()
    for edge_id in to_get_continuous_edges_ids:
        mydeb(edge_id)
        edge: sumolib.net.edge.Edge = net.getEdge(edge_id)

        from_node: sumolib.net.node.Node = edge.getFromNode()
        to_node: sumolib.net.node.Node = edge.getToNode()

        to_node_incoming_edges = to_node.getIncoming()
        to_node_outgoing_edges = to_node.getOutgoing()
        from_node_incoming_edges = from_node.getIncoming()
        from_node_outgoing_edges = from_node.getOutgoing()

        if len(to_node_incoming_edges) <= 1 and len(to_node_outgoing_edges) <= 1:
            other_edge = to_node_outgoing_edges[0]
            other_edge_id = other_edge.getID()
            mydeb(other_edge_id)
            if other_edge_id not in all_edges_ids:
                found_continuous_edges.add(other_edge_id)
        if len(from_node_incoming_edges) <= 1 and len(from_node_outgoing_edges) <= 1:
            other_edge = from_node_incoming_edges[0]
            other_edge_id = other_edge.getID()
            mydeb(other_edge_id)
            if other_edge_id not in all_edges_ids:
                found_continuous_edges.add(other_edge_id)

    all_edges_ids = get_continuous_edges(net, all_edges_ids, found_continuous_edges)
    return all_edges_ids

def main(sumo_net_file: str, config_file: str, cut_edges_file: str, output_file: str, *args, **kwargs):
    
    # Need to do the output file relative to the config file
    # output_file = os.path.relpath(output_file, os.path.dirname(config_file))
    net = get_net_file(sumo_net_file)
    with open (cut_edges_file, "r") as file:
        cut_edges = file.read().splitlines()

    command = f"netconvert -c {config_file} --remove-edges.input-file {cut_edges_file} --sumo-net-file {sumo_net_file} --output-file {output_file}"
    run_system(command)

    cut_edges_ids = set(cut_edges)
    continuous_cut_edges = get_continuous_edges(net, set(), cut_edges_ids)
    if cut_edges_ids != continuous_cut_edges:
        # Create a new file for the updated cut edges
        cut_edges_file_dir = os.path.dirname(cut_edges_file)
        cut_edges_file_truebasename, cut_edges_file_extension = true_basename(cut_edges_file)
        if "time" in kwargs:
            time = kwargs["time"]
        else:
            time = get_current_time_file_format()
        continuous_cut_edges_file = f"{cut_edges_file_truebasename}_continuous_{time}{cut_edges_file_extension}"
        continuous_cut_edges_file_path = os.path.join(cut_edges_file_dir, continuous_cut_edges_file)
    
        with open(continuous_cut_edges_file_path, "w") as f:
            f.write("\n".join(continuous_cut_edges))
    else:
        continuous_cut_edges_file_path = cut_edges_file

    command = f"netconvert -c {config_file} --remove-edges.input-file {continuous_cut_edges_file_path} --sumo-net-file {sumo_net_file} --output-file {kwargs["o2"]}"
    run_system(command)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Description of your script')

    # Add command line arguments
    parser.add_argument('--sumo-net-file', type=str, help='Path to the SUMO network file')
    parser.add_argument("--config-file", "--c", type=str,
                        help="Path to the netconvert configuration file")
    parser.add_argument('--cut-edges-file', type=str, help='Path to the file with the edges that are going to be cut')
    parser.add_argument('--output', type=str, help='Path to the output file')

    #parser.add_argument('arg1', type=str, help='Description of arg1')
    #parser.add_argument('--arg2', type=int, default=10, help='Description of arg2 (default: 10)')

    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()

    if args.sumo_net_file is None:
        sumo_net_file = DEFAULT_SUMO_NET_FILE
    else:
        sumo_net_file = args.sumo_net_file

    if args.config_file is None:
        config_file = DEFAULT_CONFIG_FILE
    else:
        config_file = args.config_file
    if args.cut_edges_file is None:
        cut_edges_file = DEFAULT_SYSTEMS_CUT_FILE
    else:
        cut_edges_file = args.cut_edges_file

    if args.output is None:
        sumo_net_file_path = os.path.dirname(sumo_net_file)
        sumo_net_file_truebasename, sumo_net_file_extension = true_basename(sumo_net_file)
        output_time = get_current_time_file_format()
        output_file = os.path.join(sumo_net_file_path, f"{sumo_net_file_truebasename}{SYSTEMS_FILENAME_SUFFIX}_{output_time}.net.xml")
        output_file_2 = os.path.join(sumo_net_file_path, f"{sumo_net_file_truebasename}{SYSTEMS_FILENAME_SUFFIX}_continuous_{output_time}.net.xml")
    else:
        output_file = args.output
    # Call the main function with parsed arguments

    main(sumo_net_file, config_file, cut_edges_file, output_file, **{"time": output_time, "o2": output_file_2})