from service.rule_engine.rule import Rule
from Repository.rule_library.condition_library import Condition_Library
from Repository.rule_library.action_library import Action_Library

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