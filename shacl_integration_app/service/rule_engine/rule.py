from .fact import Fact
from .condition import Condition
from .action import Action
from typing import List, Any
from functools import reduce

class Rule:
    def __init__(self, condition: Condition, action: Action, else_action: Action = None):
        self.conditions = [condition]
        self.actions = [action]
        self.else_actions = [else_action] if else_action else []

    def add_condition(self, condition: Condition) -> None:
        self.conditions.append(condition)

    def add_action(self, action: Action) -> None:
        self.actions.append(action)

    def add_else_action(self, else_action: Action) -> None:
        self.else_actions.append(else_action)

    def evaluate(self, facts: List[Fact]) -> Any:
        def fact_generator(conditions: List[Condition], facts: List[Fact]):
            for fact in facts:
                results = map(lambda condition: condition.eval_func(fact), conditions)
                all_conditions_true = reduce(lambda x, y: x and y, results)
                if all_conditions_true:
                    yield fact

        true_facts = list(fact_generator(self.conditions, facts))
        false_facts = [fact for fact in facts if fact not in true_facts]

        for fact in true_facts:
            for action in self.actions:
                action.exec_func(fact)

        for fact in false_facts:
            for else_action in self.else_actions:
                else_action.exec_func(fact)

    def evaluate_with_result(self, facts: List[Fact]) -> Any:
        def fact_generator(conditions: List[Condition], facts: List[Fact]):
            for fact in facts:
                results = map(lambda condition: condition.eval_func(fact), conditions)
                all_conditions_true = reduce(lambda x, y: x and y, results)
                if all_conditions_true:
                    yield fact

        true_facts = list(fact_generator(self.conditions, facts))
        false_facts = [fact for fact in facts if fact not in true_facts]

        return_res = []

        for fact in true_facts:
            for action in self.actions:
                return_res.append(action.exec_func(fact))

        for fact in false_facts:
            for else_action in self.else_actions:
                return_res.append(else_action.exec_func(fact))

        return return_res
    
    def evaluate_multiple_rules(self, facts: List[Fact], rules: List['Rule']) -> Any:
        for rule in rules:
            rule.evaluate(facts)
    def evaluate_multiple_rules_with_result(self, facts: List[Fact], rules: List['Rule']) -> Any:
        res = []
        for rule in rules:
            res += rule.evaluate_with_result(facts)
        return res
