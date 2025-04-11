from rdflib import Graph
from shacl_integration_app.repository.constants import sparql_queries


def run_query_for_target(target: str, ontology_path: str) -> list[tuple[str]]:
    try:
        g = Graph()
        g.parse(ontology_path)  # asumimos que ontology se carga desde un archivo TTL
        query = sparql_queries.SPARQL_QUERY_TARGET_SUBJECTS_OBJECTS_OF_PATH(target_of_path=target)
        results = g.query(query)
        return [
            (str(row[0]), str(row[1]), str(row[2]))
            for row in results
            if str(row[0]) != 'None' and str(row[1]) != 'None'
        ]
    except Exception as e:
        print(f"Error with target {target}: {e}")
        return []