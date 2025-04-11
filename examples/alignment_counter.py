from rdflib import Graph, Namespace, URIRef
from rdflib.util import guess_format
import json

def count_alignments(file_path):
    format_ = guess_format(file_path)
    
    if format_ is None:
        print(f"Format file cannot be obtained: {file_path}")
        return
    
    g = Graph()
    g.parse(file_path, format=format_)

    # Define the alignment namespace using the default namespace URI as declared in the RDF file.
    # Notice that there's no trailing '#' here.
    ALIGN = Namespace("http://knowledgeweb.semanticweb.org/heterogeneity/alignment")

    # Count alignment cells by looking at subjects which have the 'entity1' predicate.
    # Each alignment cell should contribute one triple with the property entity1.
    alignment_cells = {s for s, p, o in g.triples((None, ALIGN.entity1, None))}
    print(f"Number of alignment cells: {len(alignment_cells)}")

def load_json_in_dictionary(file_path:str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


# Example usage
if __name__ == "__main__":
    path = "C:\\Users\\salgo\\Developer\\tesis\\shacl_integration\\evaluation_files\\sosa-ssn-saref\\alignment_references\\reference.rdf"  # Change this to your RDF file path
    count_alignments(path)

    json_file_path: str = 'C:\\Users\\salgo\\Developer\\tesis\\shacl_integration\\examples\\files_windows.json'
    json_dict : dict = load_json_in_dictionary(json_file_path)

    for elem in json_dict.keys():
        print(f'Description: {json_dict[elem]["description"]}')
        path_list: list[str] = []
        total_triples: int = 0
        if json_dict[elem]["alignment_reference"] != None:
            count_alignments(json_dict[elem]["alignment_reference"])
