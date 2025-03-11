from dataclasses import dataclass

@dataclass
class Axiom:
    pred: str
    obj: str

    def __str__(self) -> str:
        return f"Axiom predicate: {self.pred}, axiom object: {self.obj}"