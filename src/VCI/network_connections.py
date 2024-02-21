# Takes a network and determines which junctions are at the edge of the network, making them entry or exit junctions
# Saves a file with the junctions, their coordinates, and their type (entry, exit or entry_exit) to memory
import argparse
import os
import sumolib
from src.VCI.utils.sumo_lib_net import is_dead_end_junction, is_entry_junction, is_exit_junction

DEFAULT_SUMO_NET_FILE = "networks\\filter_by_edge.net.xml"
NETWORK_CONNECTIONS_FILENAME_SUFFIX = "_network_connections"


def get_junc_data(junction: sumolib.net.node.Node) -> tuple[str, float, float, str]:
    junc_id = junction.getID()
    x,y = junction.getCoord()
    lon, lat = net.convertXY2LonLat(x,y)
    if is_entry_junction(junction) and not is_exit_junction(junction):
        type = "entry"
    elif is_exit_junction(junction) and not is_entry_junction(junction):
        type = "exit"
    else:
        type = "entry_exit"
    return (junc_id, lon, lat, type)

def main(net: sumolib.net.Net, *args, **kwargs) -> list[tuple[str, float, float, str]]:
    '''Returns a list of tuples with the junction id, longitude, latitude and type of junction (entry, exit or entry_exit)'''
    # Get junctions of type dead_end
    all_junctions: set[sumolib.net.node.Node] = {node for node in net.getNodes()}

    
    connection_junctions = set(filter(is_dead_end_junction, all_junctions))
    
    system_connections = []
    for junction in connection_junctions:
        system_connection = get_junc_data(junction)
        system_connections.append(system_connection)
    
    return system_connections



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
    connections = main(net=net)

    header = ["id", "lon", "lat", "type"]
    df = pd.DataFrame(connections, columns=header)
    df.to_csv(output, index=False)



    