# Takes a sumo network and a set of edges and returns a new set of edges
# The new set of edges is derived from the original according to
#   the types of edge that are adjacent to the original set of edges
#   the names of the edges
import argparse
import os
import sumolib
from src.VCI.utils.string_comparison import levenshtein_similarity
from src.VCI.utils.path_utils import true_basename
from src.VCI.utils.datetime_utils import get_current_time_file_format
from src.VCI.utils.sumo_lib_net import get_net_file
from unidecode import unidecode

STRING_SIMILARITY_THRESHOLD = 0.8


def rec_get_adjacent_same_type_edges(all_edges: set[sumolib.net.edge.Edge], to_get_adjacent_edges: set[sumolib.net.edge.Edge], edge_types: set[str], max_depth: int, current_depth: int) -> set[sumolib.net.edge.Edge]:
    if len(to_get_adjacent_edges) == 0:
        return all_edges
    if current_depth == max_depth:
        return all_edges
    new_adjacent_edges = set()
    for edge in to_get_adjacent_edges:
        outgoing = set(edge._outgoing)
        incoming_edges = set(edge._incoming)
        adjacent_edges = outgoing.union(incoming_edges)
        this_edge_adjacent_edges_of_type = {edge for edge in adjacent_edges if edge._type in edge_types}
        this_edge_new_edges = this_edge_adjacent_edges_of_type.difference(all_edges)
        new_adjacent_edges = new_adjacent_edges.union(this_edge_new_edges)
    
    all_edges = all_edges.union(new_adjacent_edges)
    adjacent_same_type_edges = rec_get_adjacent_same_type_edges(all_edges, new_adjacent_edges, edge_types, max_depth, current_depth+1)
    return adjacent_same_type_edges

def get_edges_types(edges: set[sumolib.net.edge.Edge]) -> set[str]:
    edge_types = {edge._type for edge in edges}
    return edge_types

def get_adjacent_same_type_edges(current_edges: set[sumolib.net.edge.Edge]) -> set[sumolib.net.edge.Edge]:
    edge_types = get_edges_types(current_edges)
    all_edges = rec_get_adjacent_same_type_edges(current_edges, current_edges, edge_types)
    return all_edges
    

def extend_network_by_adjacent_types_and_depth(edges: set[sumolib.net.edge.Edge], edge_type_depth: dict[str, int]) -> set[sumolib.net.edge.Edge]:
    # Get all keys with the same value from edge_type_depth
    keys_with_infinite_depth = {key for key, value in edge_type_depth.items() if value == -1}

    edges = rec_get_adjacent_same_type_edges(edges, edges, keys_with_infinite_depth, -1, 0)

    extended_edges_by_depth = set()
    depths = set(edge_type_depth.values())
    for depth in depths:
        keys_with_depth = {key for key, value in edge_type_depth.items() if value == depth}
        this_edge_extended_edges = rec_get_adjacent_same_type_edges(edges, edges, keys_with_depth, depth, 0)
        this_edge_new_edges = this_edge_extended_edges.difference(edges)
        extended_edges_by_depth = extended_edges_by_depth.union(this_edge_new_edges)

    # Only add the extended edges in the end so each depth doesn't influence the others
    edges = edges.union(extended_edges_by_depth)
    return edges

def main(sumo_net_file: str, output: str, edge_names_file: str, edge_types_file: str) -> None:
    net = get_net_file(sumo_net_file)

    if output is None:
        sumo_net_file_path = os.path.dirname(sumo_net_file)
        sumo_net_file_truebasename, sumo_net_file_extension = true_basename(sumo_net_file)
        output_time = get_current_time_file_format()
        output = os.path.join(sumo_net_file_path, f"{sumo_net_file_truebasename}_extended_{output_time}.txt")

    if edge_names_file is not None:
        with open(edge_names_file, "r") as f:
            lines= f.readlines()
        aliases = set([line.strip() for line in lines])
    else:
        aliases = ["vci", "via de cintura interna", "ic23", "no de coimbroes", "Nó do Areinho"]

    if edge_types_file is not None:
        edge_type_depth = {}
        with open(edge_types_file, "r") as f:
            for line in f:
                edge_type, depth = line.split(" ")
                edge_type_depth[edge_type] = int(depth)
    else:
        edge_type_depth = {
            'highway.motorway': -1,
            'highway.motorway_link': 1,
            'highway.primary': 2,
            'highway.primary_link': 1,
            'highway.secondary': 2,
            'highway.secondary_link': 1,
        }

    print(f"edge_names: {aliases}")
    print(f"edge_types: {edge_type_depth}")
    if len(aliases) == 0:
        named_edges = get_named_edges(net, aliases)
    else:
        named_edges = net.getEdges()
    extended_edges = extend_network_by_adjacent_types_and_depth(named_edges, edge_type_depth)
    extended_edges_ids = [edge._id for edge in extended_edges]

    

    print(f"Writing extended edges to {output}")
    with open(output, "w") as f:
        f.writelines([f"{edge_id}\n" for edge_id in extended_edges_ids])

def compare_strings(string1: str, string2: str) -> float:
    # return the similarity between two strings
    return levenshtein_similarity(string1, string2)

def is_alias(to_compare_string: str, alias_string: str) -> bool:
    if to_compare_string == "" or alias_string == "":
        return False
    
    to_compare_string = unidecode(to_compare_string.lower())
    alias_string = unidecode(alias_string.lower())
    if alias_string in to_compare_string:
        return True
    if to_compare_string in alias_string:
        return True
    similarity = compare_strings(alias_string, to_compare_string)
    if similarity > STRING_SIMILARITY_THRESHOLD:
        return True

def is_aliases(to_compare_string: str, aliases: set[str]) -> bool:
    for alias in aliases:
        if is_alias(to_compare_string, alias):
            return True
    return False

    
def get_named_edges(net: sumolib.net.Net, aliases: set[str]) -> set[sumolib.net.edge.Edge]:

    named_edges = set()
    for edge in net.getEdges():
        edge_name = edge._name
        if is_aliases(edge_name, aliases):
            named_edges.add(edge)

    return named_edges


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("sumo_net_file", metavar="sumo-net-file", default="", type=str, help="Directory with the network files")
    parser.add_argument("-o", "--output", type=str, help="Output directory")
    parser.add_argument("--edge-names-file", type=str, help="File with the names of the edges to be extended")
    parser.add_argument("--edge-types-file", type=str, help="File with the types of the edges to be extended")

    return parser.parse_args()

if __name__ == "__main__":
    print("Starting")
    args = parse_arguments()
    sumo_net_file: str = args.sumo_net_file
    output: str = args.output
    edge_names_file: str = args.edge_names_file
    edge_types_file: str = args.edge_types_file
    main(sumo_net_file, output, edge_names_file, edge_types_file)




