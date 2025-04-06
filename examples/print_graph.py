from rdflib import Graph, Namespace, Literal, BNode
from rdflib.namespace import RDF, XSD

# Namespaces
EX = Namespace("http://example.com/")
EX2 = Namespace("http://example2.com/")
SH = Namespace("http://www.w3.org/ns/shacl#")

# Crear un grafo
g = Graph()

# Bindear prefijos
g.bind("ex", EX)
g.bind("ex2", EX2)
g.bind("sh", SH)
g.bind("xsd", XSD)

# Nodo principal: ex:ClassExampleShape
class_example_shape = EX.ClassExampleShape
g.add((class_example_shape, RDF.type, SH.NodeShape))
g.add((class_example_shape, SH.targetClass, EX.Person))
g.add((class_example_shape, SH.targetClass, EX2.Person))
g.add((class_example_shape, SH.property, EX.PropertyExample))

# Nodo para ex:PropertyExample
property_example = EX.PropertyExample
g.add((property_example, RDF.type, SH.PropertyShape))
g.add((property_example, SH.path, EX.address))

# Nodo para sh:or
or_node = BNode()
g.add((property_example, SH.or_, or_node))

# Rama 1: sh:class ex:City
branch_1 = BNode()
g.add((or_node, RDF.first, branch_1))
g.add((branch_1, SH.class_, EX.City))

# Rama 2: sh:class ex:PostalAddress
branch_2 = BNode()
rest_node = BNode()
g.add((or_node, RDF.rest, rest_node))
g.add((rest_node, RDF.first, branch_2))
g.add((branch_2, SH.class_, EX.PostalAddress))

# Finalizar la lista RDF
g.add((rest_node, RDF.rest, RDF.nil))

# Guardar el grafo en formato Turtle
with open("output.ttl", "w") as f:
    f.write(g.serialize(format="turtle"))