# Takes a network and a set of entry or exit junctions
# Outputs an additional file with calibrators for each lane in the entry or exit edges
import argparse
import os
import sumolib
from xml.dom import minidom
from src.VCI.utils.sumo_lib_net import get_net_file
from src.VCI.utils.path_utils import true_basename
from src.VCI.utils.datetime_utils import get_current_time_file_format
import pandas as pd

DEFAULT_SUMO_NET_FILE = "networks\\filter_by_edge.net.xml"
DEFAULT_NETWORK_CONNECTIONS_FILE = "networks\\filter_by_edge_system_connections.txt"
NETWORK_ADDITIONALS_FILENAME_SUFFIX = "_network_additionals"
CALIBRATOR_LENGTH = 2.0
def main(net: sumolib.net.Net, junctions: set[sumolib.net.node.Node], *args, **kwargs) -> minidom.Element:
    xml_file = minidom.Document()

    root = xml_file.createElement("additional")
    root.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.setAttribute("xsi:noNamespaceSchemaLocation", "http://sumo.dlr.de/xsd/additional_file.xsd")

    for junction in junctions:
        incoming = junction.getIncoming()
        incoming_is_entry = [False] * len(incoming)
        incoming_with_is_entry = zip(incoming, incoming_is_entry)
        outgoing = junction.getOutgoing()
        outgoing_is_entry = [True] * len(outgoing)
        outgoing_with_is_entry = zip(outgoing, outgoing_is_entry)
        
        all_edges_with_entry = list(incoming_with_is_entry) + list(outgoing_with_is_entry)
        for edge, is_entry in all_edges_with_entry:
            calibrators = get_edges_lane_calibrator_elements(xml_file, edge, is_entry)
            for calibrator in calibrators:
                root.appendChild(calibrator)
        
    return root

def get_lanes_lane_calibrator_element(xml_file: minidom.Document, lane:sumolib.net.lane.Lane, parent_edge: sumolib.net.edge.Edge, is_entry: bool, *args, **kwargs) -> minidom.Element:
    lane_id = lane.getID()
    calibrator_id = f"ca_{lane_id}"
    calibrator = xml_file.createElement("calibrator")
    calibrator.setAttribute("id", calibrator_id)
    calibrator.setAttribute("lane", lane_id)
    if is_entry:
        calibrator_pos = str(0.0)
    else:
        calibrator_pos = str(lane.getLength()-CALIBRATOR_LENGTH)
    calibrator.setAttribute("pos", calibrator_pos)
    calibrator.setAttribute("output", calibrator_id)
    return calibrator

def get_edges_lane_calibrator_elements(xml_file: minidom.Document, edge:sumolib.net.edge.Edge, is_entry:bool, *args, **kwargs) -> set[minidom.Element]:
    calibrator_elements = set()
    for lane in edge.getLanes():
        calibrator = get_lanes_lane_calibrator_element(xml_file, lane, edge, is_entry)
        calibrator_elements.add(calibrator)
    
    return calibrator_elements


def parse_arguments():
    parser = argparse.ArgumentParser(description='Description of your script')

    # Add command line arguments
    parser.add_argument('--sumo-net-file', '-s', type=str, help='Path to the SUMO network file')
    parser.add_argument('--network-connections-file', type=str, help='Path to the network connections file')
    parser.add_argument("--output", "-o", type=str, help="Path to the output file")


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
    xml_file = main(net, junctions, args)
    xml_file_str = xml_file.toprettyxml(indent="\t")

    with open(output, "w") as f:
        f.write(xml_file_str)