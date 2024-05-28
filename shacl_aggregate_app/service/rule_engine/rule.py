from service.rule_engine.fact import Fact
from service.rule_engine.condition import Condition
from service.rule_engine.action import Action
from typing import List, Any
from functools import reduce

class Rule:
    def __init__(self, condition: Condition, action: Action):
        self.conditions = [condition]
        self.actions = [action]

    def add_condition(self, condition: Condition) -> None:
        self.conditions.append(condition)

    def add_action(self, action: Action) -> None:
        self.actions.append(action)

    def evaluate(self, facts: List[Fact]) -> Any:
        def fact_gnerator(conditions: List[Condition], facts: List[Fact]):
            all_conditions_true = True
            for fact in facts:
                results = map(lambda condition: condition.eval_func(fact), conditions)
                all_conditions_true = reduce(lambda x, y: x and y, results)

                if all_conditions_true:
                    yield fact

        true_facts = list(fact_gnerator(self.conditions, facts))

        if len(true_facts) > 0:
            for fact in true_facts:
                for action in self.actions:
                    action.exec_func(fact)

    def evaluate_with_result(self, facts: List[Fact]) -> Any:
        def fact_gnerator(conditions: List[Condition], facts: List[Fact]):
            all_conditions_true = True
            for fact in facts:
                results = map(lambda condition: condition.eval_func(fact), conditions)
                all_conditions_true = reduce(lambda x, y: x and y, results)

                if all_conditions_true:
                    yield fact

        true_facts = list(fact_gnerator(self.conditions, facts))

        return_res = []
        if len(true_facts) > 0:
            for fact in true_facts:
                for action in self.actions:
                    return_res.append(action.exec_func(fact))

        return return_res

    def evaluate_multiple_rules(self, facts: List[Fact], rules: List['Rule']) -> Any:
        for rule in rules:
            rule.evaluate(facts)

    def evaluate_multiple_rules_with_result(self, facts: List[Fact], rules: List['Rule']) -> Any:
        res = []
        for rule in rules:
            res += rule.evaluate_with_result(facts)
        return res
        