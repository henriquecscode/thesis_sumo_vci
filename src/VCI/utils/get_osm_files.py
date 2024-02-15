import argparse
import os

def parser_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("osm_source_folder", default="osm", help="Directory with the osm files")
    args = parser.parse_args()
    return args.osm_source_folder

def main(osm_source_folder: str):
    osm_files = os.listdir
    osm_file_paths = [os.path.join(osm_source_folder, osm_file) for osm_file in osm_files]
    return osm_file_paths
    

if __name__ == "__main__":
    osm_source_folder = parser_arguments()
    main(osm_source_folder=osm_source_folder)
