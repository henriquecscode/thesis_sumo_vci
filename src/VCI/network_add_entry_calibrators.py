# Takes a network and a set of edges
# Outputs an additional file with calibrators at the start of each lane
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
DEFAULT_NETWORK_CONNECTION_EDGES_FILE = "networks\\filter_by_edge_network_connection_edges.txt"
DEFAULT_SUMO_ADDITIONALS_FILE = "networks\\filter_by_edge.add.xml"
NETWORK_ADDITIONALS_FILENAME_SUFFIX = "_entry_calibrators"
def main(root: ET.Element, net: sumolib.net.Net, edges: set[sumolib.net.edge.Edge], *args, **kwargs) -> ET.Element:
    for edge in edges:
        for lane in edge.getLanes():
            calibrator = get_lanes_lane_calibrator_element(lane, edge)
            root.append(calibrator)
        
    return root

def get_lanes_lane_calibrator_element(lane:sumolib.net.lane.Lane, parent_edge: sumolib.net.edge.Edge, *args, **kwargs) -> ET.Element:
    lane_id = lane.getID()
    calibrator_id = f"ca_{lane_id}"
    calibrator = ET.Element("calibrator")
    calibrator.set("id", calibrator_id)
    calibrator.set("lane", lane_id)
    calibrator_pos = str(0.0)
    calibrator.set("pos", calibrator_pos)
    calibrator.set("output", calibrator_id)
    return calibrator

def parse_arguments():
    parser = argparse.ArgumentParser(description='Description of your script')

    # Add command line arguments
    parser.add_argument('--sumo-net-file', '-s', type=str, help='Path to the SUMO network file')
    parser.add_argument('--network-connection-edges-file', type=str, help='Path to the network connection edges file')
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

    if args.network_connection_edges_file is None:
        network_connection_edges_file = DEFAULT_NETWORK_CONNECTION_EDGES_FILE
    else:
        network_connection_edges_file = args.network_connection_edges_file

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
    df = pd.read_csv(network_connection_edges_file)
    only_entries = df[df['type'] == 'entry']
    edges_ids = only_entries['id'].astype('str').tolist()

    edges = {net.getEdge(edge_id) for edge_id in edges_ids}
    
    root = main(root, net, edges, args)

    # Save to mem
    write_root(root, output)