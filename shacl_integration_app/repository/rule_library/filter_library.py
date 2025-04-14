from shacl_integration_app.service.rule_engine.rule import Rule
from shacl_integration_app.repository.rule_library import *

class Filter_Library():
    def __init__(self):
        self.condition_library = Condition_Library()
        self.action_library = Action_Library()
        self.rule_multiple = Rule(condition=None, action=None)


        # FILTER RULES

        # Count filter rules
        self.countFilter: Rule = Rule(condition=self.condition_library.evaluateCount, action=self.action_library.returnTrue)
        
        # InExClusive filter rules
        self.evaluateMinInExClusiveRule: Rule = Rule(condition=self.condition_library.evaluateMinInExClusive, action=self.action_library.returnTrue)
        self.evaluateMaxInExClusiveRule: Rule = Rule(condition=self.condition_library.evaluateMaxInExClusive, action=self.action_library.returnTrue)
        self.evaluateMinMaxInclusiveRule: Rule = Rule(condition=self.condition_library.evaluateMinMaxInclusive, action=self.action_library.returnTrue)
        self.evaluateMinMaxExclusiveRule: Rule = Rule(condition=self.condition_library.evaluateMinMaxExclusive, action=self.action_library.returnTrue)
        self.evaluateMinMaxInExClusiveRule: Rule = Rule(condition=self.condition_library.evaluateMinMaxInExClusive, action=self.action_library.returnTrue)
        self.evaluateMaxMinInExClusiveRule: Rule = Rule(condition=self.condition_library.evaluateMaxMinInExClusive, action=self.action_library.returnTrue)
        self.evaluateInExClusiveFilter = [self.evaluateMinInExClusiveRule, self.evaluateMaxInExClusiveRule, self.evaluateMinMaxInclusiveRule, self.evaluateMinMaxExclusiveRule, self.evaluateMinMaxInExClusiveRule, self.evaluateMaxMinInExClusiveRule]

        # Equals Disjoint filter rules
        self.equalsDisjointFilter: Rule = Rule(condition=self.condition_library.equalsDisjoint, action=self.action_library.returnTrue)

        # Closed filter rules
        self.closedFilter: Rule = Rule(condition=self.condition_library.closed, action=self.action_library.returnTrue)

        # Logical filter rules
        self.logicalIntersectionFilter: Rule = Rule(condition=self.condition_library.logicalIntersection, action=self.action_library.returnTrue)

        # Language filter rules
        self.uniqueLangFilter: Rule = Rule(condition=self.condition_library.uniqueLang, action=self.action_library.returnTrue)
        self.languageInFilter: Rule = Rule(condition=self.condition_library.languageIn, action=self.action_library.returnTrue)

        # In filter rules
        self.inFilter: Rule = Rule(condition=self.condition_library.inCondition, action=self.action_library.returnTrue)
        
        # NodeKind filter rules
        self.nodeKindUnionLiteralFilter: Rule = Rule(condition=self.condition_library.nodeKindUnionLiteral, action=self.action_library.returnTrue)
        self.nodeKindUnionBlankNodeFilter: Rule = Rule(condition=self.condition_library.nodeKindUnionBlankNode, action=self.action_library.returnTrue)
        # self.nodeKindUnionBlankNodeOrLiteralFilter: Rule = Rule(condition=self.condition_library.nodeKindUnionBlankNodeOrLiteral, action=self.action_library.returnTrue)
        # self.nodeKindUnionBlankNodeOrIRIFilter: Rule = Rule(condition=self.condition_library.nodeKindUnionBlankNodeOrIRI, action=self.action_library.returnTrue)
        # self.nodeKindUnionIRIOrLiteralFilter: Rule = Rule(condition=self.condition_library.nodeKindUnionIRIOrLiteral, action=self.action_library.returnTrue)
        # self.nodeKindUnionFilter = [self.nodeKindUnionLiteralFilter, self.nodeKindUnionBlankNodeFilter, self.nodeKindUnionBlankNodeOrLiteralFilter, self.nodeKindUnionBlankNodeOrIRIFilter, self.nodeKindUnionIRIOrLiteralFilter]
        self.nodeKindUnionFilter = [self.nodeKindUnionLiteralFilter, self.nodeKindUnionBlankNodeFilter]

        self.nodeKindIntersectionLiteralFilter: Rule = Rule(condition=self.condition_library.nodeKindIntersectionLiteral, action=self.action_library.returnTrue)
        self.nodeKindIntersectionIRIFilter: Rule = Rule(condition=self.condition_library.nodeKindIntersectionIRI, action=self.action_library.returnTrue)
        self.nodeKindIntersectionBlankNodeFilter: Rule = Rule(condition=self.condition_library.nodeKindIntersectionBlankNode, action=self.action_library.returnTrue)
        self.nodeKindIntersectionFilter = [self.nodeKindIntersectionLiteralFilter, self.nodeKindIntersectionIRIFilter]

