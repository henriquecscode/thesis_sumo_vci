# This script takes the lanes with detectors and cuts them  from the network for the process of isolating the weakly connected components 
# These weakly connected components are the ones that are going to be subject to flow equations

import argparse
import os
import sumolib
import lxml.etree as ET
from src.VCI.utils.sumo_lib_net import get_net_file, get_edges_list_str
from src.VCI.utils.path_utils import true_basename
from src.VCI.utils.datetime_utils import get_current_time_file_format
from src.VCI.utils.run import run_system

CUT_SYSTEMS_FILENAME_SUFFIX = "_cut_systems"
DEFAULT_SUMO_NET_FILE = f"networks/filter_by_edge{CUT_SYSTEMS_FILENAME_SUFFIX}.net.xml"
DEFAULT_SYSTEMS_DETECTOR_SYSTEMS_FOLDER_SUFFIX = "_detector_systems"
DEFAULT_CONFIG_FILE = "network_configs/filter_by_edge.cfg"


def main(sumo_net_file: str, config_file: str, output_folder: str, *args, **kwargs):
    
    # Need to do the output file relative to the config file
    os.makedirs(output_folder, exist_ok=True)

    analysed_edges = set()
    to_analyse_detector_systems_net_file = sumo_net_file
    number_systems = 0
    sumo_net_file_truebasename, _ = true_basename(sumo_net_file)
    net = get_net_file(sumo_net_file)
    all_edges = net.getEdges()
    if len(net.getEdges()) == 0:
        print("No edges to analyse")
        return
    all_edges_ids = set([edge.getID() for edge in all_edges])
    
    while True:
        if all_edges_ids == analysed_edges:
            print("All edges have been analysed")
            break
        remove_edges_list_str = get_edges_list_str(analysed_edges)
        # Make numbersystem pad with 0's to 3 chars
        system_net_output_name = f"{sumo_net_file_truebasename}_{number_systems+1:03}"
        system_net_output_file = f"{system_net_output_name}.net.xml"
        system_net_output_filepath = os.path.join(output_folder, system_net_output_file)

        if number_systems == 63:
            print("Reached maximum number of systems")
        command = f"netconvert -c {config_file} --remove-edges.explicit {remove_edges_list_str} --sumo-net-file {sumo_net_file} --output-file {system_net_output_filepath}"
        run_system(command)
        net = get_net_file(system_net_output_filepath)
        system_edges = net.getEdges()
        if len(system_edges) == 0:
            break
        
        system_edges_ids = set([edge.getID() for edge in system_edges])
        system_edges_output_file = f"{system_net_output_name}.txt"
        system_edges_output_filepath = os.path.join(output_folder, system_edges_output_file)

        with open(system_edges_output_filepath, "w") as f:
            f.write("\n".join(system_edges_ids))
        analysed_edges = analysed_edges.union(system_edges_ids)
        number_systems += 1
        


    print("All edges have been analysed")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Description of your script')

    # Add command line arguments
    parser.add_argument('--sumo-net-file', type=str, help='Path to the SUMO network file')
    parser.add_argument("--config-file", "--c", type=str,
                        help="Path to the netconvert configuration file")
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

    if args.output is None:
        sumo_net_file_path = os.path.dirname(sumo_net_file)
        sumo_net_file_truebasename, sumo_net_file_extension = true_basename(sumo_net_file)
        output_time = get_current_time_file_format()
        output_folder = os.path.join(sumo_net_file_path, f"{sumo_net_file_truebasename}{DEFAULT_SYSTEMS_DETECTOR_SYSTEMS_FOLDER_SUFFIX}_{output_time}")
    else:
        output_folder = args.output
    # Call the main function with parsed arguments

    main(sumo_net_file, config_file, output_folder)