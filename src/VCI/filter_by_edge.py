# Takes a network and a set of edges
# Runs netconvert to create a new network with just the set of edges.
import argparse
import os
import shutil
from src.VCI.utils.run import run_subprocess
from src.VCI.utils.datetime_utils import get_current_time_file_format

OSM_FOLDER = "osm"
NETWORKS_DIR = "networks"
EDGE_FILE_PREFIX = "edges_"
OUTPUT_FILE_PREFIX = "filter_by_edge_"


def main(sumo_net_file: str, config_file: str, edge_names_file: str, edge_types_depth_file: str, options: dict, *args, **kwargs):
    # Run netconvert with the given configuration file
    file_datetime = get_current_time_file_format()

    config_file_dir = os.path.dirname(config_file)
    config_file_name, config_file_ext = os.path.splitext(os.path.basename(config_file))

    copy_config_file = f"{config_file_dir}/{config_file_name}_{file_datetime}{config_file_ext}"

    edges_file_name = f"{EDGE_FILE_PREFIX}{file_datetime}.txt"
    edges_file = os.path.join(config_file_dir, edges_file_name)
    command = f"python utils\\extend_edges_in_network.py {sumo_net_file} -o {edges_file} --edge-names-file {edge_names_file} --edge-types-file {edge_types_depth_file}"
    run_subprocess(command)
    
    if "output_file" in options:
        output_file = options["output_file"]
    else:
        output_file = f"{NETWORKS_DIR}/{OUTPUT_FILE_PREFIX}{file_datetime}.net.xml"

    # Run command with save configuration (doesn't execute, just saves)
    base_command = f"netconvert --sumo-net-file {sumo_net_file} --keep-edges.input-file {edges_file} --configuration-file {config_file} --output-file {output_file}"
    command = f"{base_command} --save-configuration {copy_config_file}"
    run_subprocess(command)
    # Actually run netconvert
    command = base_command
    run_subprocess(command, True)



def parse_arguments():
    parser = argparse.ArgumentParser(description='Description of your script')

    # Add command line arguments
    parser.add_argument("--output-file", "-o", type=str, help="Path to the output file")
    parser.add_argument("--sumo-net-file", "--s", type=str,
                        help="Path to the SUMO network file")
    parser.add_argument("--config-file", "--c", type=str,
                        help="Path to the netconvert configuration file")
    
    parser.add_argument("--edge-names-file", type=str, help="File with the names of the edges to be extended")
    parser.add_argument("--edge-types-file", type=str, help="File with the types of the edges to be extended")

    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()

    options = {}

    if args.output_file is not None:
        options["output_file"] = args.output_file

    if args.sumo_net_file is None:
        sumo_net_file = "networks/base.net.xml"
    else:
        sumo_net_file = args.sumo_net_file

    if args.config_file is None:
        config_file = "netconvert_configs/filter_by_edge.cfg"
    else:
        config_file = args.config_file

    if args.edge_names_file is None:
        edge_names_file = "netconvert_configs/network_road_names"
    else:
        edge_names_file = args.edge_names_file

    if args.edge_types_file is None:
        edge_types_depth_file = "netconvert_configs/network_road_type_depth"
    else:
        edge_types_depth_file = args.edge_types_file

    # Call the main function with parsed arguments
    main(sumo_net_file, config_file, edge_names_file, edge_types_depth_file, options)
