from Point import Point
from Edge import Edge

class GridItem:
    def __init__(self, uintValue, row, column):
        self._value = uintValue
        self._top_left = Point.instance(column*2, row)
        self._top_right = Point.instance(column*2 + 2, row)
        self._bottom_left = Point.instance(column*2, row + 1)
        self._bottom_right = Point.instance(column*2 + 2, row + 1)
        self.initialize_edges()
    
    def get_points(self):
        return self._top_left, self._top_right, self._bottom_right, self._bottom_left
    
    def get_value(self):
        return self._value

    def initialize_edges(self):
        edge = Edge.instance(self._top_left, self._top_right)
        edge.add_score(self._value)
        edge = Edge.instance(self._top_right, self._bottom_right)
        edge.add_score(self._value)
        edge = Edge.instance(self._bottom_right, self._bottom_left)
        edge.add_score(self._value)
        edge = Edge.instance(self._top_left, self._bottom_left)
        edge.add_score(self._value)