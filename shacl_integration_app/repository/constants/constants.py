import json
import os

json_file: str = os.getenv('FILES_JSON_PATH', 'files.json')

try:
    with open (json_file, 'r') as f:
        json_data: dict = json.loads(f.read())
        f.close()
except FileNotFoundError:
    json_data: dict = {}


# STATUS CODES

BAD_REQUEST: int = 400
OK: int = 200
INTERNAL_SERVER_ERROR: int = 500

global_aligned_properties: list[str] = []

global_aligned_properties_res : dict = {}

__all__ = [*locals().keys()]




nodeKindDict: dict = {
    "[1, 0, 0, 0, 0, 0]_union": ["http://www.w3.org/ns/shacl#IRI"],
    "[1, 0, 0, 0, 0, 0]_intersection": ["http://www.w3.org/ns/shacl#IRI"],
    "[1, 1, 0, 0, 0, 0]_union": ["http://www.w3.org/ns/shacl#IRIOrLiteral"],
    "[1, 0, 1, 0, 0, 0]_union": ["http://www.w3.org/ns/shacl#BlankNodeOrIRI"],
    "[1, 0, 0, 1, 0, 0]_union": ["http://www.w3.org/ns/shacl#IRIOrLiteral"],
    "[1, 0, 0, 1, 0, 0]_intersection": ["http://www.w3.org/ns/shacl#IRI"],
    "[1, 0, 0, 0, 0, 1]_union": ["http://www.w3.org/ns/shacl#BlankNodeOrIRI"],
    "[1, 0, 0, 0, 0, 1]_intersection": ["http://www.w3.org/ns/shacl#IRI"],
    "[1, 1, 0, 1, 0, 0]_union": ["http://www.w3.org/ns/shacl#IRIOrLiteral"],
    "[1, 1, 0, 1, 0, 0]_intersection": ["http://www.w3.org/ns/shacl#IRIOrLiteral"],
    "[1, 0, 1, 0, 0, 1]_union": ["http://www.w3.org/ns/shacl#BlankNodeOrIRI"],
    "[1, 0, 1, 0, 0, 1]_intersection": ["http://www.w3.org/ns/shacl#BlankNodeOrIRI"],
    "[1, 0, 0, 1, 0, 1]_intersection": ["http://www.w3.org/ns/shacl#IRI"],
    "[0, 1, 0, 0, 0, 0]_union": ["http://www.w3.org/ns/shacl#Literal"],
    "[0, 1, 0, 0, 0, 0]_intersection": ["http://www.w3.org/ns/shacl#Literal"],
    "[0, 1, 1, 0, 0, 0]_union": ["http://www.w3.org/ns/shacl#BlankNodeOrLiteral"],
    "[0, 1, 0, 1, 0, 0]_union": ["http://www.w3.org/ns/shacl#IRIOrLiteral"],
    "[0, 1, 0, 1, 0, 0]_intersection": ["http://www.w3.org/ns/shacl#Literal"],
    "[0, 1, 0, 0, 1, 0]_union": ["http://www.w3.org/ns/shacl#BlankNodeOrLiteral"],
    "[0, 1, 0, 0, 1, 0]_intersection": ["http://www.w3.org/ns/shacl#Literal"],
    "[0, 1, 1, 0, 1, 0]_union": ["http://www.w3.org/ns/shacl#BlankNodeOrLiteral"],
    "[0, 1, 1, 0, 1, 0]_intersection": ["http://www.w3.org/ns/shacl#BlankNodeOrLiteral"],
    "[0, 1, 0, 1, 1, 0]_intersection": ["http://www.w3.org/ns/shacl#Literal"],
    "[0, 0, 1, 0, 0, 0]_union": ["http://www.w3.org/ns/shacl#BlankNode"],
    "[0, 0, 1, 0, 0, 0]_intersection": ["http://www.w3.org/ns/shacl#BlankNode"],
    "[0, 0, 1, 0, 0, 1]_union": ["http://www.w3.org/ns/shacl#BlankNodeOrIRI"],
    "[0, 0, 1, 0, 0, 1]_intersection": ["http://www.w3.org/ns/shacl#BlankNode"],
    "[0, 0, 1, 0, 1, 0]_union": ["http://www.w3.org/ns/shacl#BlankNodeOrLiteral"],
    "[0, 0, 1, 0, 1, 0]_intersection": ["http://www.w3.org/ns/shacl#BlankNode"],
    "[0, 0, 1, 0, 1, 1]_intersection": ["http://www.w3.org/ns/shacl#BlankNode"],
    "[0, 0, 0, 1, 0, 0]_union": ["http://www.w3.org/ns/shacl#IRIOrLiteral"],
    "[0, 0, 0, 1, 0, 0]_intersection": ["http://www.w3.org/ns/shacl#IRIOrLiteral"],
    "[0, 0, 0, 1, 0, 1]_intersection": ["http://www.w3.org/ns/shacl#IRI"],
    "[0, 0, 0, 1, 1, 0]_intersection": ["http://www.w3.org/ns/shacl#Literal"],
    "[0, 0, 0, 0, 0, 1]_union": ["http://www.w3.org/ns/shacl#BlankNodeOrIRI"],
    "[0, 0, 0, 0, 0, 1]_intersection": ["http://www.w3.org/ns/shacl#BlankNodeOrIRI"],
    "[0, 0, 0, 1, 0, 1]_intersection": ["http://www.w3.org/ns/shacl#IRI"],
    "[0, 0, 0, 0, 1, 1]_intersection": ["http://www.w3.org/ns/shacl#BlankNode"],
    "[0, 0, 0, 0, 1, 0]_union": ["http://www.w3.org/ns/shacl#BlankNodeOrLiteral"],
    "[0, 0, 0, 0, 1, 0]_intersection": ["http://www.w3.org/ns/shacl#BlankNodeOrLiteral"],
    "[0, 0, 0, 0, 1, 1]_intersection": ["http://www.w3.org/ns/shacl#BlankNode"],
    "[0, 0, 0, 1, 1, 0]_intersection": ["http://www.w3.org/ns/shacl#Literal"],
    "[1, 0, 0, 1, 0, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 0, 0, 1, 1, 0]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 0, 0, 0, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 0, 0, 1, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 1, 0, 1, 0, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 1, 0, 1, 1, 0]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 1, 0, 0, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 1, 0, 1, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 0, 1, 1, 0, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 0, 1, 1, 1, 0]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 0, 1, 0, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 0, 1, 1, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 0, 0, 1, 0, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 0, 0, 1, 1, 0]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 0, 0, 0, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 0, 0, 1, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 1, 1, 0, 0, 0]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 1, 0, 1, 0, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 1, 0, 1, 1, 0]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 1, 0, 0, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 1, 0, 1, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 0, 1, 1, 0, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 0, 1, 1, 1, 0]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 0, 1, 0, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 0, 1, 1, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 1, 1, 1, 0, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 1, 1, 1, 1, 0]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 1, 1, 0, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[0, 1, 1, 1, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ],
    "[1, 1, 1, 1, 1, 1]_union": [
        "http://www.w3.org/ns/shacl#IRIOrLiteral",
        "http://www.w3.org/ns/shacl#BlankNodeOrIRI"
    ]
}



