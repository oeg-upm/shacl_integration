
SPARQL_QUERY_TARGET_CLASS_PATH: str = (lambda ontology, target_class_path, ontology_class: f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    SELECT DISTINCT * FROM <{ontology}>
    WHERE {{
        <{target_class_path}> a ?type ;
            (rdfs:domain | schema:domainIncludes) <{ontology_class}> .
        OPTIONAL {{
            <{target_class_path}> (rdfs:range | schema:rangeIncludes) ?range .
        }}
    }} """)

SPARQL_QUERY_TARGET_SUBJECTS_OF_PATH: str = (lambda ontology, target_subjects_of_path: f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    SELECT DISTINCT * FROM <{ontology}>
    WHERE {{
        <{target_subjects_of_path}> a ?type ;
            (rdfs:domain | schema:domainIncludes) ?domain .
        OPTIONAL {{
            <{target_subjects_of_path}> (rdfs:range | schema:rangeIncludes) ?range .
        }}
    }} """)


SPARQL_QUERY_TARGET_OBJECTS_OF_PATH: str = (lambda ontology, target_objects_of_path: f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT DISTINCT * FROM <{ontology}>
    WHERE {{
        <{target_objects_of_path}> a owl.ObjectProperty ;
            (rdfs:domain | schema:domainIncludes) ?domain .
        OPTIONAL {{
            <{target_objects_of_path}> (rdfs:range | schema:rangeIncludes) ?range .
        }}
    }} """)


SPARQL_QUERY_ONTOLOGY_RESTRICTIONS_EXTRACTION: str = (lambda ontology: f"""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT DISTINCT ?class ?property ?restriction ?restrictionValue FROM <{ontology}>
    WHERE {{
        ?s a owl:Restriction ;
            owl:onProperty ?property ;
            ?restriction ?restrictionValue .
        ?class ?relation ?s .
        FILTER (?restrictionValue != ?property)
        FILTER (?restrictionValue != owl:Restriction)
    }} """)

__all__ = [*locals().keys()]
