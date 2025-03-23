from collections import defaultdict
from typing import List, Tuple

class TupleProcessor:
    def __init__(self):
        pass

    def remove_fully_contained_tuples(self, tuple_list: List[Tuple[str]]) -> List[Tuple[str]]:
        tuple_sets = [(t, set(t)) for t in tuple_list]
        result = []

        for i, (t1, s1) in enumerate(tuple_sets):
            is_contained = False
            for j, (t2, s2) in enumerate(tuple_sets):
                if i != j and s1.issubset(s2) and len(s2) > len(s1):
                    is_contained = True
                    break
            if not is_contained:
                result.append(t1)
        return result

    class UnionFind:
        def __init__(self):
            self.parent = {}

        def find(self, x):
            if x not in self.parent:
                self.parent[x] = x
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]

        def union(self, x, y):
            self.parent[self.find(x)] = self.find(y)

    def merge_overlapping_tuples(self, tuple_list: List[Tuple[str]]) -> List[Tuple[str]]:
        uf = self.UnionFind()

        for t in tuple_list:
            for i in range(1, len(t)):
                uf.union(t[0], t[i])

        groups = defaultdict(set)
        for t in tuple_list:
            for elem in t:
                root = uf.find(elem)
                groups[root].add(elem)

        return [tuple(sorted(group)) for group in groups.values()]

    def process_tuples(self, tuple_list: List[Tuple[str]]) -> List[Tuple[str]]:
        cleaned = self.remove_fully_contained_tuples(tuple_list)
        merged = self.merge_overlapping_tuples(cleaned)
        return merged
