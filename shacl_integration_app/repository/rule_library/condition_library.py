from shacl_integration_app.service.rule_engine.condition import Condition

class Condition_Library():
    def __init__(self):
        # Max condition
        self.maxFirst = Condition(name="MaxFirst", evaluation_function=lambda fact: True if fact.first != None and fact.second != None and fact.first >= fact.second else False)
        self.maxSecond = Condition(name="MaxSecond", evaluation_function=lambda fact: True if fact.first != None and fact.second != None and fact.first < fact.second else False)
        self.maxNone = Condition(name="MaxNone", evaluation_function=lambda fact: True if fact.first == None or fact.second == None else False)

        #Min condition
        self.minFirst = Condition(name="MinFirst", evaluation_function=lambda fact: True if fact.first != None and fact.second != None and fact.first <= fact.second else False)
        self.minSecond = Condition(name="MinSecond", evaluation_function=lambda fact: True if fact.first != None and fact.second != None and fact.first > fact.second else False)
        self.minNone = Condition(name="MinNone", evaluation_function=lambda fact: True if fact.first == None or fact.second == None else False)

        # FILTER CONDITIONS

        # Count filter conditions
        self.evaluateCount = Condition(name="CountFilter", evaluation_function=lambda fact: True if fact.minCount != None and fact.maxCount != None and fact.minCount > fact.maxCount else False)

        # InExClusive filter conditions

        self.evaluateMinInExClusive = Condition(name="evaluateMinMaxInclusive", evaluation_function=lambda fact: True if fact.minInclusive != None and fact.minExclusive != None and fact.minInclusive == fact.minExclusive else False)
        self.evaluateMaxInExClusive = Condition(name="evaluateMaxMaxInclusive", evaluation_function=lambda fact: True if fact.maxInclusive != None and fact.maxExclusive != None and fact.maxInclusive == fact.maxExclusive else False)
        self.evaluateMinMaxInclusive = Condition(name="evaluateMinMaxInclusive", evaluation_function=lambda fact: True if fact.minInclusive != None and fact.maxInclusive != None and fact.minInclusive > fact.maxInclusive else False)
        self.evaluateMinMaxExclusive = Condition(name="evaluateMinMaxExclusive", evaluation_function=lambda fact: True if fact.minExclusive != None and fact.maxExclusive != None and fact.minExclusive > fact.maxExclusive else False)
        self.evaluateMinMaxInExClusive = Condition(name="evaluateMinMaxInExClusive", evaluation_function=lambda fact: True if fact.minInclusive != None and fact.maxExclusive != None and fact.minInclusive >= fact.maxExclusive else False)
        self.evaluateMaxMinInExClusive = Condition(name="evaluateMaxMinInExClusive", evaluation_function=lambda fact: True if fact.maxInclusive != None and fact.minExclusive != None and fact.maxInclusive <= fact.minExclusive else False)

        # Equals Disjoint condition

        self.equalsDisjoint = Condition(name="EqualsDisjoint", evaluation_function=lambda fact: True if fact.equals != None and type(fact.equals) == str and fact.disjoint != None and type(fact.disjoint) == str and fact.equals == fact.disjoint else False)

        # Closed condition
        self.closed = Condition(name="Closed", evaluation_function=lambda fact: True if fact.closed1 != None and type(fact.closed1) == bool and fact.closed2 != None and type(fact.closed2) == bool and fact.closed1 != fact.closed2 else False)


        # Logical condition
        self.logicalIntersection = Condition(name="LogicalIntersection", evaluation_function=lambda fact: True if fact.logical1 != None and type(fact.logical1) == list and fact.logical2 != None and type(fact.logical2) == list and fact.logical1 != fact.logical2 else False)


        # Language condition
        self.languageIn = Condition(name="Language", evaluation_function=lambda fact: True if fact.uniqueLang != None and type(fact.uniqueLang) == str and fact.languageIn != None and type(fact.languageIn) == list and fact.uniqueLang not in fact.languageIn else False)
        self.uniqueLang = Condition(name="Language", evaluation_function=lambda fact: True if fact.uniqueLang1 != None and type(fact.uniqueLang1) == str and fact.uniqueLang1 != None and type(fact.uniqueLang2) == str and fact.uniqueLang1 != fact.uniqueLang2 else False)

        # In condition
        self.inCondition = Condition(name="In", evaluation_function=lambda fact: True if fact.in1 != None and type(fact.in1) == list and fact.in2 != None and type(fact.in2) == list and fact.in1 != fact.in2 else False)

        # NodeKind condition UNION
        literalUnionList : list[str] = ['http://www.w3.org/ns/shacl#Literal', 'http://www.w3.org/ns/shacl#IRI', 'http://www.w3.org/ns/shacl#IRIOrLiteral']
        self.nodeKindUnionLiteral = Condition(name="NodeKindUnionLiteral", evaluation_function=lambda fact: True if fact.nodeKind1 != None and fact.nodeKind2 != None and fact.nodeKind1 == 'http://www.w3.org/ns/shacl#Literal' and fact.nodeKind2 not in literalUnionList else False)

        blankNodeUnionList : list[str] = ['http://www.w3.org/ns/shacl#BlankNode', 'http://www.w3.org/ns/shacl#IRI', 'http://www.w3.org/ns/shacl#BlankNodeOrIRI']
        self.nodeKindUnionBlankNode = Condition(name="NodeKindUnionBlankNode", evaluation_function=lambda fact: True if fact.nodeKind1 != None and fact.nodeKind2 != None and fact.nodeKind1 == 'http://www.w3.org/ns/shacl#BlankNode' and fact.nodeKind2 not in blankNodeUnionList else False)

        # NodeKind condition INTERSECTION
        literalIntersectionList : list[str] = ['http://www.w3.org/ns/shacl#Literal', 'http://www.w3.org/ns/shacl#IRIOrLiteral']
        self.nodeKindIntersectionLiteral = Condition(name="NodeKindIntersectionLiteral", evaluation_function=lambda fact: True if fact.nodeKind1 != None and fact.nodeKind2 != None and fact.nodeKind1 == 'http://www.w3.org/ns/shacl#Literal' and fact.nodeKind2 not in literalIntersectionList else False)

        iriIntersectionList : list[str] = ['http://www.w3.org/ns/shacl#IRI', 'http://www.w3.org/ns/shacl#BlankNodeOrIRI', 'http://www.w3.org/ns/shacl#IRIOrLiteral']
        self.nodeKindIntersectionIRI = Condition(name="NodeKindIntersectionIRI", evaluation_function=lambda fact: True if fact.nodeKind1 != None and fact.nodeKind2 != None and fact.nodeKind1 == 'http://www.w3.org/ns/shacl#IRI' and fact.nodeKind2 not in iriIntersectionList else False)

        blankNodeIntersectionList : list[str] = ['http://www.w3.org/ns/shacl#BlankNode', 'http://www.w3.org/ns/shacl#BlankNodeOrIRI']
        self.nodeKindIntersectionBlankNode = Condition(name="NodeKindIntersectionBlankNode", evaluation_function=lambda fact: True if fact.nodeKind1 != None and fact.nodeKind2 != None and fact.nodeKind1 == 'http://www.w3.org/ns/shacl#BlankNode' and fact.nodeKind2 not in blankNodeIntersectionList else False)

        