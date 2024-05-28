from service.rule_engine.condition import Condition

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


        