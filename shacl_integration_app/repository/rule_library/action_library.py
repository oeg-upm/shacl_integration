from shacl_integration_app.service.rule_engine.action import Action

class Action_Library():
    def __init__(self):
        # Return action
        self.returnFirst = Action(name="Return First", execution_function=lambda fact: fact.first)
        self.returnSecond = Action(name="Return Second", execution_function=lambda fact: fact.second)
        self.returnNone = Action(name="Return None", execution_function=lambda fact: None)
        self.returnNotNone = Action(name="Return Not None", execution_function=lambda fact: fact.first if fact.first != None else fact.second)