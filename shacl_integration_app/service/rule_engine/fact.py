from typing import Any

class Fact:
    def __init__(self, **kwargs: Any):
        self.__dict__.update(kwargs)