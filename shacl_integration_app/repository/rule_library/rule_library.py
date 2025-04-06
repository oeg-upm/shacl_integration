from shacl_integration_app.service.rule_engine.rule import Rule
from . import *

class Rule_Library():
    def __init__(self):
        self.condition_library = Condition_Library()
        self.action_library = Action_Library()
        self.rule_multiple = Rule(condition=None, action=None)

        # Max union rules
        self.unionMaxFirst = Rule(condition=self.condition_library.maxFirst, action=self.action_library.returnFirst)
        self.unionMaxSecond = Rule(condition=self.condition_library.maxSecond, action=self.action_library.returnSecond)
        self.unionMaxNone = Rule(condition=self.condition_library.maxNone, action=self.action_library.returnNone)
        self.unionMaxRules = [self.unionMaxFirst, self.unionMaxSecond, self.unionMaxNone]

        # Min union rules
        self.unionMinFirst = Rule(condition=self.condition_library.minFirst, action=self.action_library.returnFirst)
        self.unionMinSecond = Rule(condition=self.condition_library.minSecond, action=self.action_library.returnSecond)
        self.unionMinNone = Rule(condition=self.condition_library.minNone, action=self.action_library.returnNone)
        self.unionMinRules = [self.unionMinFirst, self.unionMinSecond, self.unionMinNone]

        # Max intersection rules
        self.intersectionMaxFirst = Rule(condition=self.condition_library.maxFirst, action=self.action_library.returnSecond)
        self.intersectionMaxSecond = Rule(condition=self.condition_library.maxSecond, action=self.action_library.returnFirst)
        self.intersectionMaxNone = Rule(condition=self.condition_library.maxNone, action=self.action_library.returnNotNone)
        self.intersectionMaxRules = [self.intersectionMaxFirst, self.intersectionMaxSecond, self.intersectionMaxNone]

        # Min intersection rules
        self.intersectionMinFirst = Rule(condition=self.condition_library.minFirst, action=self.action_library.returnSecond)
        self.intersectionMinSecond = Rule(condition=self.condition_library.minSecond, action=self.action_library.returnFirst)
        self.intersectionMinNone = Rule(condition=self.condition_library.minNone, action=self.action_library.returnNotNone)
        self.intersectionMinRules = [self.intersectionMinFirst, self.intersectionMinSecond, self.intersectionMinNone]

        # INTEGRATION RULES
        
        # NodeKind
        self.nodeKindIRIOnlyIntegration = Rule(condition=self.condition_library.nodeKindIRIOnlyIntegration, action=self.action_library.returnOne, else_action=self.action_library.returnZero)

        self.nodeKindLiteralOnlyIntegration = Rule(condition=self.condition_library.nodeKindLiteralOnlyIntegration, action=self.action_library.returnOne, else_action=self.action_library.returnZero)

        self.nodeKindBlankNodeOnlyIntegration = Rule(condition=self.condition_library.nodeKindBlankNodeOnlyIntegration, action=self.action_library.returnOne, else_action=self.action_library.returnZero)

        self.nodeKindIRIOrLiteralOnlyIntegration = Rule(condition=self.condition_library.nodeKindIRIOrLiteralOnlyIntegration, action=self.action_library.returnOne, else_action=self.action_library.returnZero)

        self.nodeKindBlankNodeOrLiteralOnlyIntegration = Rule(condition=self.condition_library.nodeKindBlankNodeOrLiteralOnlyIntegration, action=self.action_library.returnOne, else_action=self.action_library.returnZero)

        self.nodeKindBlankNodeOrIRIOnlyIntegration = Rule(condition=self.condition_library.nodeKindBlankNodeOrIRIOnlyIntegration, action=self.action_library.returnOne, else_action=self.action_library.returnZero)
        
        self.integrationNodeKindRules = [self.nodeKindIRIOnlyIntegration, self.nodeKindLiteralOnlyIntegration, self.nodeKindBlankNodeOnlyIntegration, self.nodeKindIRIOrLiteralOnlyIntegration, self.nodeKindBlankNodeOrLiteralOnlyIntegration, self.nodeKindBlankNodeOrIRIOnlyIntegration]


