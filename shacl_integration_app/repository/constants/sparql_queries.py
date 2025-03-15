# SPARQL QUERIES FOR SHACL SHAPE EXTRACTION

SPARQL_QUERY_TARGET_CLASS_PATH_SHAPE: str = """
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    SELECT DISTINCT ?NodeShape ?class WHERE
    {
        ?NodeShape a sh:NodeShape ;
                sh:targetClass ?class .
    }
"""

SPARQL_QUERY_TARGET_CLASS_PATH_SHAPE_values: list[str] = ["NodeShape", "class", "http://www.w3.org/ns/shacl#targetClass"]



SPARQL_QUERY_TARGET_SUBJECTS_OF_PATH_SHAPE: str = """
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    SELECT DISTINCT ?NodeShape ?path WHERE
    {
        ?NodeShape a sh:NodeShape ;
                sh:targetSubjectsOf ?path .
    }
"""

SPARQL_QUERY_TARGET_SUBJECTS_OF_PATH_SHAPE_values: list[str] = ["NodeShape", "path", "http://www.w3.org/ns/shacl#targetSubjectsOf"]


SPARQL_QUERY_TARGET_OBJECTS_OF_PATH_SHAPE: str = """
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    SELECT DISTINCT ?NodeShape ?path WHERE
    {
        ?NodeShape a sh:NodeShape ;
                sh:targetObjectsOf ?path .
    }
"""

SPARQL_QUERY_TARGET_OBJECTS_OF_PATH_SHAPE_values: list[str] = ["NodeShape", "path", "http://www.w3.org/ns/shacl#targetObjectsOf"]


SPARQL_QUERY_PROPERTY_PATH_SHAPE: str = """
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT ?NodeShape ?path
    WHERE {
        ?NodeShape a sh:NodeShape ;
                sh:property ?property .
        OPTIONAL {
            ?property sh:path ?path .
        }
        OPTIONAL {
            ?property sh:or/rdf:rest*/rdf:first ?p .
            ?p sh:path ?path .
        }
        OPTIONAL {
            ?property sh:and/rdf:rest*/rdf:first ?p .
            ?p sh:path ?path .
        }
        OPTIONAL {
            ?property sh:xone/rdf:rest*/rdf:first ?p .
            ?p sh:path ?path .
        }
    }
"""

SPARQL_QUERY_PROPERTY_PATH_SHAPE_values: list[str] = ["NodeShape", "path", "http://www.w3.org/ns/shacl#path"]

node_queries_target_class: list[list[str]] = [
            [SPARQL_QUERY_TARGET_CLASS_PATH_SHAPE, SPARQL_QUERY_TARGET_CLASS_PATH_SHAPE_values]]

node_queries_subjects_objects: list[list[str]] = [
            [SPARQL_QUERY_TARGET_SUBJECTS_OF_PATH_SHAPE, SPARQL_QUERY_TARGET_SUBJECTS_OF_PATH_SHAPE_values],
            [SPARQL_QUERY_TARGET_OBJECTS_OF_PATH_SHAPE, SPARQL_QUERY_TARGET_OBJECTS_OF_PATH_SHAPE_values]]


# SPARQL QUERIES FOR ONTOLOGY EXTRACTION

SPARQL_QUERY_TARGET_CLASS_PATH: str = (lambda target_class_path, ontology_class: f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    SELECT DISTINCT *
    WHERE {{
        <{target_class_path}> a ?type ;
            (rdfs:domain | schema:domainIncludes) <{ontology_class}> .
        OPTIONAL {{
            <{target_class_path}> (rdfs:range | schema:rangeIncludes) ?range .
        }}
    }} """)

SPARQL_QUERY_TARGET_SUBJECTS_OBJECTS_OF_PATH: str = (lambda target_of_path: f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    SELECT DISTINCT ?domain ?property ?range
    WHERE {{
        BIND(<{target_of_path}> AS ?property)
        ?property a ?type ;
            (rdfs:domain | schema:domainIncludes) ?domain .
        OPTIONAL {{
            ?property (rdfs:range | schema:rangeIncludes) ?range .
        }}
    }} """)


SPARQL_QUERY_ONTOLOGY_RESTRICTIONS_EXTRACTION: str = f"""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT DISTINCT ?class ?property ?restriction ?restrictionValue
    WHERE {{
        ?s a owl:Restriction ;
            owl:onProperty ?property ;
            ?restriction ?restrictionValue .
        ?class ?relation ?s .
        FILTER (?restrictionValue != ?property)
        FILTER (?restrictionValue != owl:Restriction)
    }} """

__all__ = [*locals().keys()]
