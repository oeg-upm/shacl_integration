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

SPARQL_QUERY_REAL_PROPERTY_PATH_SHAPE: str = """
PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT ?PropertyShape ?path
    WHERE {
        ?PropertyShape a sh:PropertyShape.
        OPTIONAL {
            ?PropertyShape sh:path ?path .
        }
        OPTIONAL {
            ?PropertyShape sh:or/rdf:rest*/rdf:first ?p .
            ?p sh:path ?path .
        }
        OPTIONAL {
            ?PropertyShape sh:and/rdf:rest*/rdf:first ?p .
            ?p sh:path ?path .
        }
        OPTIONAL {
            ?PropertyShape sh:xone/rdf:rest*/rdf:first ?p .
            ?p sh:path ?path .
        }
    }
"""

SPARQL_QUERY_PROPERTY_PATH_SHAPE_values: list[str] = ["NodeShape", "path", "http://www.w3.org/ns/shacl#path"]
SPARQL_QUERY_REAL_PROPERTY_PATH_SHAPE_values: list[str] = ["PropertyShape", "path", "http://www.w3.org/ns/shacl#path"]

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
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX schema: <http://schema.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT ?domain ?property ?range
    WHERE {{
        BIND(<{target_of_path}> AS ?property)

        OPTIONAL {{
            ?property (rdfs:domain | schema:domainIncludes) ?crude_domain .
            {{
                ?crude_domain owl:unionOf ?domain_list .
                ?domain_list rdf:rest*/rdf:first ?domain .
            }}
            UNION {{
                FILTER(NOT EXISTS {{ ?crude_domain owl:unionOf ?_ }})
                BIND(?crude_domain AS ?domain)
            }}
        }}

        OPTIONAL {{
            ?property (rdfs:range | schema:rangeIncludes) ?crude_range .
            {{
                ?crude_range owl:unionOf ?range_list .
                ?range_list rdf:rest*/rdf:first ?range .
            }}
            UNION {{
                FILTER(NOT EXISTS {{ ?crude_range owl:unionOf ?_ }})
                BIND(?crude_range AS ?range)
            }}
        }}
    }}
""")




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


# SPARQL QUERIES FOR ALIGNMENT REFERENCE EXTRACTION

SPARQL_QUERY_ALIGNMENT_REFERENCE: str = (lambda threshold: f"""
PREFIX align: <http://knowledgeweb.semanticweb.org/heterogeneity/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?entity1 ?entity2
WHERE {{
    ?init a align:alignmentCell .
    ?init align:alignmententity1 ?entity1 .
    ?init align:alignmententity2 ?entity2 .
    ?init align:alignmentmeasure ?rawMeasure .
    ?init align:alignmentrelation ?relation .

    BIND(xsd:float(str(?rawMeasure)) AS ?measure)

    FILTER (?measure >= {threshold})
    FILTER (?relation = "=")
}}
""")


SPARQL_QUERY_EXTRACT_SHAPES: str = """
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?root ?propertyShape ?subj ?pred ?obj
WHERE {
    {
        # Extract all triples from the main NodeShape
        ?root a ?type .
        VALUES ?type { sh:NodeShape sh:PropertyShape }
        BIND(?root AS ?subj)
        ?subj ?pred ?obj .
    }
    UNION
    {
        # Extract all properties (including rdfs:comment and others)
        ?root sh:property ?propertyShape .
        BIND(?propertyShape AS ?subj)
        ?subj ?pred ?obj .
    }
    UNION
    {
        ?root sh:qualifiedValueShape ?subj .
        ?subj ?pred ?obj .
    }
    UNION
    {
        # Extract sh:or, sh:and, sh:xone, sh:not when defined in the NodeShape directly
        ?root (sh:or|sh:and|sh:xone|sh:not) ?list .
        ?list rdf:rest*/rdf:first ?subj .
        ?subj ?pred ?obj .
    }
    UNION
    {
        # Extract sh:or, sh:and, sh:xone, sh:not when defined inside a PropertyShape
        ?root sh:property ?propertyShape .
        ?propertyShape (sh:or|sh:and|sh:xone|sh:not) ?list .
        ?list rdf:rest*/rdf:first ?subj .
        ?subj ?pred ?obj .
    }
    UNION
    {
        ?root sh:property ?propertyShape .
        ?root sh:qualifiedValueShape ?subj .
        ?subj ?pred ?obj .
    }
    UNION
    {
        # Extract restrictions within sh:or, sh:and, sh:xone, sh:not (lists inside NodeShape)
        ?root (sh:or|sh:and|sh:xone|sh:not) ?list .
        ?list rdf:rest*/rdf:first ?innerShape .
        ?innerShape ?pred ?obj .
        BIND(?innerShape AS ?subj)
    }
    UNION
    {
        # Extract restrictions within sh:or, sh:and, sh:xone, sh:not (lists inside PropertyShape)
        ?root sh:property ?propertyShape .
        ?propertyShape (sh:or|sh:and|sh:xone|sh:not) ?list .
        ?list rdf:rest*/rdf:first ?innerShape .
        ?innerShape ?pred ?obj .
        BIND(?innerShape AS ?subj)
    }
    UNION
    {
        # Extract sh:or, sh:and, sh:xone, sh:not (when they are direct nodes inside a NodeShape)
        ?root (sh:or|sh:and|sh:xone|sh:not) ?subj .
        ?subj ?pred ?obj .
    }
    UNION
    {
        # Extract sh:or, sh:and, sh:xone, sh:not (when they are direct nodes inside a PropertyShape)
        ?root sh:property ?propertyShape .
        ?propertyShape (sh:or|sh:and|sh:xone|sh:not) ?subj .
        ?subj ?pred ?obj .
    }
    UNION
    {
        # Extract rdfs:comment and other predicates within each PropertyShape
        ?root sh:property ?propertyShape .
        ?propertyShape ?pred ?obj .
        FILTER(?pred != sh:property)  # Exclude sh:property to avoid duplicating properties
        BIND(?propertyShape AS ?subj)
    }
}
"""

__all__ = [*locals().keys()]
