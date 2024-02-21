# Takes a network and a set of entry or exit junctions
# Outputs an additional file with calibrators for each lane in the entry or exit edges
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
DEFAULT_NETWORK_CONNECTIONS_FILE = "networks\\filter_by_edge_system_connections.txt"
DEFAULT_SUMO_ADDITIONALS_FILE = "networks\\filter_by_edge.add.xml"
NETWORK_ADDITIONALS_FILENAME_SUFFIX = "_calibrators"
CALIBRATOR_LENGTH = 2.0
def main(root: ET.Element, net: sumolib.net.Net, junctions: set[sumolib.net.node.Node], *args, **kwargs) -> ET.Element:
    for junction in junctions:
        incoming = junction.getIncoming()
        incoming_is_entry = [False] * len(incoming)
        incoming_with_is_entry = zip(incoming, incoming_is_entry)
        outgoing = junction.getOutgoing()
        outgoing_is_entry = [True] * len(outgoing)
        outgoing_with_is_entry = zip(outgoing, outgoing_is_entry)
        
        all_edges_with_entry = list(incoming_with_is_entry) + list(outgoing_with_is_entry)
        for edge, is_entry in all_edges_with_entry:
            for lane in edge.getLanes():
                calibrator = get_lanes_lane_calibrator_element(lane, edge, is_entry)
                root.append(calibrator)
        
    return root

def get_lanes_lane_calibrator_element(lane:sumolib.net.lane.Lane, parent_edge: sumolib.net.edge.Edge, is_entry: bool, *args, **kwargs) -> ET.Element:
    lane_id = lane.getID()
    calibrator_id = f"ca_{lane_id}"
    calibrator = ET.Element("calibrator")
    calibrator.set("id", calibrator_id)
    calibrator.set("lane", lane_id)
    if is_entry:
        calibrator_pos = str(0.0)
    else:
        calibrator_pos = str(lane.getLength()-CALIBRATOR_LENGTH)
    calibrator.set("pos", calibrator_pos)
    calibrator.set("output", calibrator_id)
    return calibrator

def parse_arguments():
    parser = argparse.ArgumentParser(description='Description of your script')

    # Add command line arguments
    parser.add_argument('--sumo-net-file', '-s', type=str, help='Path to the SUMO network file')
    parser.add_argument('--network-additionals-file', type=str, help='Path to the network additionals file')
    parser.add_argument('--network-connections-file', type=str, help='Path to the network connections file')
    parser.add_argument("--output", "-o", type=str, help="Path to the output file")
    parser.add_argument('--overwrite', action='store_true', help='Overwrite the input network additionals file. Ignore Output argument')



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

    if args.network_connections_file is None:
        network_connections_file = DEFAULT_NETWORK_CONNECTIONS_FILE
    else:
        network_connections_file = args.network_connections_file

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
    df = pd.read_csv(network_connections_file)
    junctions_ids = df['id'].astype('str').tolist()

    junctions = {net.getNode(junc_id) for junc_id in junctions_ids}
    
    root = main(root, net, junctions, args)

    # Save to mem
    write_root(root, output)