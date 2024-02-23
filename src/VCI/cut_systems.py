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

# Expands the set of edges to include the edges that are continuous to the ones in the set
# That means, there is a determinism in the flow of traffic
    
def get_continuous_edges(net: sumolib.net.Net, all_edges_ids: set[str], to_get_continuous_edges_ids: set[str], *args, **kwargs) -> set[str]:
    all_edges_ids = all_edges_ids.union(to_get_continuous_edges_ids)
    if len(to_get_continuous_edges_ids) == 0:
        return all_edges_ids
    found_continuous_edges = set()
    for edge_id in to_get_continuous_edges_ids:
        edge: sumolib.net.edge.Edge = net.getEdge(edge_id)

        from_node: sumolib.net.node.Node = edge.getFromNode()
        to_node: sumolib.net.node.Node = edge.getToNode()

        to_node_incoming_edges = to_node.getIncoming()
        to_node_outgoing_edges = to_node.getOutgoing()
        from_node_incoming_edges = from_node.getIncoming()
        from_node_outgoing_edges = from_node.getOutgoing()

        # This conditions are not enough. In case of a junction that has one incoming and one outgoing edge that are not connected this shouldn't work!!
        # For example, a dead end (entry/exit to the system) with both an entry and an exit edge
        # Need to go in deep to know what are the connections of the junctions (and with that can even expand to complex junctions with limited directions)
        if len(to_node_incoming_edges) <= 1 and len(to_node_outgoing_edges) == 1:
            # If len(to_node_outgoing_edges) == 0, then it is a sink, and we don't need to add it to the set of continuous edges
            if to_node.getType() != "dead_end":
                other_edge = to_node_outgoing_edges[0]
                other_edge_id = other_edge.getID()
                if other_edge_id not in all_edges_ids:
                    found_continuous_edges.add(other_edge_id)
        if len(from_node_incoming_edges) == 1 and len(from_node_outgoing_edges) <= 1:
            # If len(from_node_outgoing_edges) == 0, then it is a source, and we don't need to add it to the set of continuous edges
            if from_node.getType() != "dead_end":
                other_edge = from_node_incoming_edges[0]
                other_edge_id = other_edge.getID()
                if other_edge_id not in all_edges_ids:
                    found_continuous_edges.add(other_edge_id)

    all_edges_ids = get_continuous_edges(net, all_edges_ids, found_continuous_edges)
    return all_edges_ids


# Not 100% efficient since, for each edge added, we could just apply recursively on the other end of said edge, instead of on both, by using recursion on the whole set of edges
# The fact that we are speeding up recursion would also be done. The edge's other end, would now count. Aka, we perform recursion at a edge level, instead of at a network level.
# The same could apply to the continuous edges function
def get_deducible_edges(net: sumolib.net.Net, all_edges_ids: set[str], to_get_deducible_edges_ids: set[str], *args, **kwargs) -> set[str]:
    all_edges_ids = all_edges_ids.union(to_get_deducible_edges_ids)
    if len(to_get_deducible_edges_ids) == 0:
        return all_edges_ids
    found_deducible_edges = set()
    for edge_id in to_get_deducible_edges_ids:
        edge: sumolib.net.edge.Edge = net.getEdge(edge_id)

        from_node: sumolib.net.node.Node = edge.getFromNode()
        to_node: sumolib.net.node.Node = edge.getToNode()

        to_node_incoming_edges = to_node.getIncoming()
        to_node_outgoing_edges = to_node.getOutgoing()
        from_node_incoming_edges = from_node.getIncoming()
        from_node_outgoing_edges = from_node.getOutgoing()

        to_node_incoming_edges_ids = set([edge.getID() for edge in to_node_incoming_edges])
        to_node_outgoing_edges_ids = set([edge.getID() for edge in to_node_outgoing_edges])
        to_node_edges_ids = to_node_incoming_edges_ids.union(to_node_outgoing_edges_ids)
        
        unknown_to_node_edges_ids = to_node_edges_ids.difference(all_edges_ids)
        if len(unknown_to_node_edges_ids) == 1:
            now_known_edge_id = unknown_to_node_edges_ids.pop()
            found_deducible_edges.add(now_known_edge_id)
            all_edges_ids.add(now_known_edge_id) # Speed up recursion by adding the edge to the set of known edges right away

        from_node_incoming_edges_ids = set([edge.getID() for edge in from_node_incoming_edges])
        from_node_outgoing_edges_ids = set([edge.getID() for edge in from_node_outgoing_edges])
        from_node_edges_ids = from_node_incoming_edges_ids.union(from_node_outgoing_edges_ids)
        
        unknown_from_node_edges_ids = from_node_edges_ids.difference(all_edges_ids)
        if len(unknown_from_node_edges_ids) == 1:
            now_known_edge_id = unknown_from_node_edges_ids.pop()
            found_deducible_edges.add(now_known_edge_id)
            all_edges_ids.add(now_known_edge_id) # Speed up recursion by adding the edge to the set of known edges right away

    all_edges_ids = get_deducible_edges(net, all_edges_ids, found_deducible_edges)
    return all_edges_ids    

def main(sumo_net_file: str, config_file: str, cut_edges_file: str, output_file: str, *args, **kwargs):
    
    net = get_net_file(sumo_net_file)
    with open (cut_edges_file, "r") as file:
        cut_edges = file.read().splitlines()

    # Create a new file for the cut edges
    command = f"netconvert -c {config_file} --remove-edges.input-file {cut_edges_file} --sumo-net-file {sumo_net_file} --output-file {output_file}"
    run_system(command)

    #  Create a new file for the continuous edges
    cut_edges_ids = set(cut_edges)
    continuous_cut_edges = get_continuous_edges(net, set(), cut_edges_ids)
    if True or cut_edges_ids != continuous_cut_edges:
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
    


    # Create a new file for the deducible edges
    continuous_cut_edges_ids = continuous_cut_edges
    deducible_cut_edges = get_deducible_edges(net, set(), continuous_cut_edges_ids)

    if True or continuous_cut_edges_ids != deducible_cut_edges:
        # Create a new file for the updated cut edges
        cut_edges_file_dir = os.path.dirname(continuous_cut_edges_file_path)
        cut_edges_file_truebasename, cut_edges_file_extension = true_basename(cut_edges_file)
        if "time" in kwargs:
            time = kwargs["time"]
        else:
            time = get_current_time_file_format()
        deducible_cut_edges_file = f"{cut_edges_file_truebasename}_deducible_{time}{cut_edges_file_extension}"
        deducible_cut_edges_file_path = os.path.join(cut_edges_file_dir, deducible_cut_edges_file)
    
        with open(deducible_cut_edges_file_path, "w") as f:
            f.write("\n".join(deducible_cut_edges))
    else:
        deducible_cut_edges_file_path = continuous_cut_edges_file_path

    command = f"netconvert -c {config_file} --remove-edges.input-file {deducible_cut_edges_file_path} --sumo-net-file {sumo_net_file} --output-file {kwargs["o3"]}"
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
        output_file_3 = os.path.join(sumo_net_file_path, f"{sumo_net_file_truebasename}{SYSTEMS_FILENAME_SUFFIX}_deducible_{output_time}.net.xml")

    else:
        
        output_file = args.output
    # Call the main function with parsed arguments

    main(sumo_net_file, config_file, cut_edges_file, output_file, **{"time": output_time, "o2": output_file_2, "o3": output_file_3})