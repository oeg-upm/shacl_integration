from dataclasses import dataclass

@dataclass
class Axiom:
    pred: str
    obj: str
    logical_operator: str = None
    link: str = None

    def __str__(self) -> str:
        return f"Axiom predicate: {self.pred}, axiom object: {self.obj}, logical operator: {self.logical_operator}, link: {self.link}"