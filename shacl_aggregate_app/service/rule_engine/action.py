from typing import Callable, Any, Dict, List
from service.rule_engine.fact import Fact

class Action:

    def __init__(self, name: str, execution_function: Callable[[Fact], None]):
        self.name: str = name
        self.exec_func: Callable[[Fact], None] = execution_function

    def execute(self, fact: Fact) -> None:
        self.exec_func(fact)