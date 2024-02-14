import argparse
import os
import shutil
from utils.run import run_system
from utils.datetime_utils import get_current_time_file_format

OSM_FOLDER = "osm"
NETWORKS_DIR = "networks"

def main(config_file: str, options: dict, *args, **kwargs):
    file_datetime = get_current_time_file_format()

    config_file_dir = os.path.dirname(config_file)
    config_file_basename = os.path.basename(config_file)
    config_file_name, config_file_ext = os.path.splitext(config_file_basename)

    copy_config_file_basename = f"{config_file_name}_{file_datetime}{config_file_ext}"
    copy_config_file = os.path.join(config_file_dir, copy_config_file_basename)
    osm_copy_config_file = os.path.relpath(copy_config_file, OSM_FOLDER)


    osm_config_file = config_file_basename
    shutil.copy(config_file, os.path.join(OSM_FOLDER, config_file_basename))

    if "output_file" in options:
        output_file = options["output_file"]
    else:
        output_file= os.path.join(NETWORKS_DIR, f"{config_file_name}_{file_datetime}.net.xml")
    osm_output_file = os.path.relpath(output_file, OSM_FOLDER)

    os.chdir(OSM_FOLDER)

    # Run command with save configuration (doesn't execute, just saves)
    command = f"netconvert --save-configuration {osm_copy_config_file} --configuration-file {osm_config_file} --output-file {osm_output_file}"
    run_system(command)

    # Actually run netconvert
    command = f"netconvert --configuration-file {osm_config_file} --output-file {osm_output_file}"
    run_system(command)

    os.remove(config_file_basename)

    pass


def parse_arguments():
    parser = argparse.ArgumentParser(description='Description of your script')

    # Add command line arguments
    parser.add_argument("--output-file", "-o", type=str, help="Path to the output file")
    parser.add_argument("--config_file", type=str, help="Path to the configuration file")
    #parser.add_argument('arg1', type=str, help='Description of arg1')
    #parser.add_argument('--arg2', type=int, default=10, help='Description of arg2 (default: 10)')

    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    options = {}

    if args.output_file is not None:
        options["output_file"] = args.output_file

    if args.config_file is None:
        config_file = "networks/base.cfg"
    else:
        config_file = args.config_file



    # Call the main function with parsed arguments
    main(config_file, options)