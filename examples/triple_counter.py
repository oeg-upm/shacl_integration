from rdflib import Graph
from rdflib.util import guess_format
import os
import json

def count_triples(file_path:str) -> int:
    format_ = guess_format(file_path)
    
    if format_ is None:
        print(f"Format file cannot be obtained: {file_path}")
        return

    g = Graph()
    g.parse(file_path, format=format_)
    
    num_triples = len(g)
    print(f"Number of triples at file '{file_path}' with format {format_}: {num_triples}")
    return num_triples

def load_json_in_dictionary(file_path:str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    
    json_file_path: str = 'C:\\Users\\salgo\\Developer\\tesis\\shacl_integration\\examples\\files_windows.json'
    json_dict : dict = load_json_in_dictionary(json_file_path)

    for elem in json_dict.keys():
        print(f'Description: {json_dict[elem]["description"]}')
        path_list: list[str] = []
        total_triples: int = 0

        for tup in json_dict[elem]['tuples']:
            path_list.append(tup['shape'])
        
        for path in path_list:
            num_triples: int = count_triples(file_path=path)
            total_triples += num_triples
        
        print(f'Total Number of Triples: {total_triples}')
