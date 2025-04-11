from rdflib import Graph
import xml.etree.ElementTree as ET
import xml.dom.minidom

def convert_to_alignment(input_file, output_file):
    # Load RDF graph and auto-detect format
    g = Graph()
    g.parse(input_file)

    # Detect any predicate with 'similarTo' in its local name
    alignment_triples = []
    for s, p, o in g:
        if p.split("/")[-1] == "similarTo" or p.split("#")[-1] == "similarTo":
            alignment_triples.append((s, p, o))

    # Build RDF/XML structure
    rdf_root = ET.Element("rdf:RDF", {
        "xmlns": "http://knowledgeweb.semanticweb.org/heterogeneity/alignment",
        "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "xmlns:xsd": "http://www.w3.org/2001/XMLSchema#"
    })

    alignment = ET.SubElement(rdf_root, "Alignment")
    ET.SubElement(alignment, "xml").text = "yes"
    ET.SubElement(alignment, "level").text = "0"
    ET.SubElement(alignment, "type").text = "??"

    for s, p, o in alignment_triples:
        map_elem = ET.SubElement(alignment, "map")
        cell = ET.SubElement(map_elem, "Cell")

        ET.SubElement(cell, "entity1", {"rdf:resource": str(s)})
        ET.SubElement(cell, "entity2", {"rdf:resource": str(o)})
        ET.SubElement(cell, "measure", {"rdf:datatype": "xsd:float"}).text = "1.0"
        ET.SubElement(cell, "relation").text = "="

    # Pretty print
    xml_str = ET.tostring(rdf_root, encoding='utf-8')
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml()

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"Alignment file saved to '{output_file}' with {len(alignment_triples)} correspondences.")

# Example usage
if __name__ == "__main__":
    convert_to_alignment("C:\\Users\\salgo\\Developer\\tesis\\shacl_integration\\evaluation_files\\mse\\alignment-references\\matonto-material_information_reduced-final.ttl", "C:\\Users\\salgo\\Developer\\tesis\\shacl_integration\\examples\\output_alignment.rdf")
