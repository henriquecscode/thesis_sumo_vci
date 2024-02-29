# Takes a network and determines the edges at the end of which, a vehicle has a choice on the next edge to take
# Saves a file with the edges ids to memory
import argparse
import os
import sumolib
from src.VCI.utils.sumo_lib_net import is_dead_end_junction, is_entry_junction, is_exit_junction

DEFAULT_SUMO_NET_FILE = "networks\\filter_by_edge.net.xml"
NETWORK_CONNECTIONS_FILENAME_SUFFIX = "_network_choice_edges"


def main(net: sumolib.net.Net, *args, **kwargs) -> set[sumolib.net.edge.Edge]:
    '''Returns a list of edges at the end of which, a vehicle has a choice on the next edge to take'''
    # Get junctions of type dead_end
    all_junctions: set[sumolib.net.node.Node] = {node for node in net.getNodes()}

    junctions_with_more_than_one_outgoing_edges = set(filter(lambda junc: len(junc.getOutgoing()) > 1, all_junctions))
    junctions_incoming_edges = set(edge for node in junctions_with_more_than_one_outgoing_edges for edge in node.getIncoming() )
    
    return junctions_incoming_edges



def parse_arguments():
    parser = argparse.ArgumentParser(description='Gets the entries and exits of the road network and saves to a file')

    # Add command line arguments
    parser.add_argument("--sumo-net-file", "-s", type=str, help="Path to the SUMO network file")
    parser.add_argument("--output", "-o", type=str, help="Path to the output file")

    return parser.parse_args()

if __name__ == "__main__":
    from src.VCI.utils.sumo_lib_net import get_net_file
    from src.VCI.utils.path_utils import true_basename
    from src.VCI.utils.datetime_utils import get_current_time_file_format
    import pandas as pd

    # Parse command line arguments
    args = parse_arguments()

    if args.sumo_net_file is None:
        sumo_net_file = DEFAULT_SUMO_NET_FILE
    else:
        sumo_net_file = args.sumo_net_file

    if args.output is None:
        sumo_net_file_path = os.path.dirname(sumo_net_file)
        sumo_net_file_truebasename, sumo_net_file_extension = true_basename(sumo_net_file)
        output_time = get_current_time_file_format()
        output = os.path.join(sumo_net_file_path, f"{sumo_net_file_truebasename}{NETWORK_CONNECTIONS_FILENAME_SUFFIX}_{output_time}.txt")
    else:
        output = args.output

    # Call the main function with parsed arguments
        
    net = get_net_file(sumo_net_file)
    edges = main(net=net)

    with open(output, "w") as f:
        for edge in edges:
            f.write(f"{edge.getID()}\n")



    