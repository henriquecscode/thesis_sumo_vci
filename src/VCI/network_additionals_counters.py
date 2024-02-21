# Takes a network
import argparse
import os
import sumolib
import lxml.etree as ET
from src.VCI.utils.sumo_lib_net import get_net_file, create_additionals_root, is_dead_end_junction
from src.VCI.utils.path_utils import true_basename
from src.VCI.utils.datetime_utils import get_current_time_file_format
from src.VCI.utils.xml_utils import write_root

DEFAULT_SUMO_NET_FILE = "networks\\filter_by_edge.net.xml"
DEFAULT_SUMO_ADDITIONALS_FILE = "networks\\filter_by_edge.add.xml"
NETWORK_ADDITIONALS_FILENAME_SUFFIX = "_network_additionals"
DEFAULT_INDUCTION_LOOP_PERIOD = 300.00
DEFAULT_INDUCTION_LOOP_OFFSET = 0

def get_lane_induction_loop_element(lane:sumolib.net.lane.Lane, *args, **kwargs) -> ET.Element:
    lane_id = lane.getID()
    inductionLoop_id = f"e_{lane_id}"
    inductionLoop = ET.Element("inductionLoop")
    inductionLoop_pos = str(DEFAULT_INDUCTION_LOOP_OFFSET)
    inductionLoop_period = str(DEFAULT_INDUCTION_LOOP_PERIOD)
    inductionLoop.set("id", inductionLoop_id)
    inductionLoop.set("lane", lane_id)
    inductionLoop.set("pos", inductionLoop_pos)
    inductionLoop.set("period", inductionLoop_period)
    inductionLoop.set("file", f"{inductionLoop_id}.xml")
    return inductionLoop

def main(root: ET.Element  , net: sumolib.net.Net, *args, **kwargs) -> ET.Element:
    # Get junctions inside the network
    all_junctions = net.getNodes()

    # Create detectors after the junction for junctions with different number of incoming and outgoing edges
    for junction in all_junctions:
        incoming = junction.getIncoming()
        outgoing = junction.getOutgoing()
        if len(incoming) != len(outgoing):
            for edge in outgoing:
                for lane in edge.getLanes():
                    inductionLoop = get_lane_induction_loop_element(lane)
                    root.append(inductionLoop)
    return root           
            

def parse_arguments():
    parser = argparse.ArgumentParser(description='Description of your script')

    parser.add_argument('--sumo-net-file', type=str, help='Path to the SUMO network file')
    parser.add_argument('--network-additionals-file', type=str, help='Path to the network additionals file')
    parser.add_argument('--output', type=str, help='Path to the output file')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite the input network additionals file. Ignore Output argument')
    # Add command line arguments
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
            output_file = os.path.join(sumo_net_file_path, f"{sumo_net_file_truebasename}{NETWORK_ADDITIONALS_FILENAME_SUFFIX}_{output_time}.add.xml")
        else:
            output_file = args.output


    # Call the main function with parsed arguments
    net = get_net_file(sumo_net_file)
    root = main(root, net, args)

    # Save to mem
    write_root(root, output_file)