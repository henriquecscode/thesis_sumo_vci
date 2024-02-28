# Takes a network and determines which edges are at entries or exits of the network
# Saves a file with the edges, the coordinates of the respective entry/exit, and their type (entry, exit) to memory
import argparse
import os
import sumolib
from src.VCI.utils.sumo_lib_net import is_dead_end_junction, is_entry_junction, is_exit_junction

DEFAULT_SUMO_NET_FILE = "networks\\filter_by_edge.net.xml"
NETWORK_CONNECTION_EDGES_FILENAME_SUFFIX = "_network_connection_edges"


def get_junc_connection_edges(junction: sumolib.net.node.Node) -> list[tuple[str, float, float, str]]:
    x,y = junction.getCoord()
    lon, lat = net.convertXY2LonLat(x,y)

    incoming_edges = junction.getIncoming()
    outgoing_edges = junction.getOutgoing()
    
    connection_edges = []
    for edge in incoming_edges:
        edge_id = edge.getID()
        edge_data = (edge_id, lon, lat, "exit")
        connection_edges.append(edge_data)
    for edge in outgoing_edges:
        edge_id = edge.getID()
        edge_data = (edge_id, lon, lat, "entry")
        connection_edges.append(edge_data)
    return connection_edges

def main(net: sumolib.net.Net, *args, **kwargs) -> list[tuple[str, float, float, str]]:
    '''Returns a list of tuples with the edge id, longitude, latitude of dead end junction and type of edge (entry, exit)'''
    # Get junctions of type dead_end
    all_junctions: set[sumolib.net.node.Node] = {node for node in net.getNodes()}

    
    connection_junctions = set(filter(is_dead_end_junction, all_junctions))
    
    system_connection_edges = []
    for junction in connection_junctions:
        new_connection_edges = get_junc_connection_edges(junction)
        system_connection_edges.extend(new_connection_edges)
    
    return system_connection_edges


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
        output = os.path.join(sumo_net_file_path, f"{sumo_net_file_truebasename}{NETWORK_CONNECTION_EDGES_FILENAME_SUFFIX}_{output_time}.txt")
    else:
        output = args.output

    # Call the main function with parsed arguments
        
    net = get_net_file(sumo_net_file)
    connections = main(net=net)

    header = ["id", "lon", "lat", "type"]
    df = pd.DataFrame(connections, columns=header)
    df.to_csv(output, index=False)



    