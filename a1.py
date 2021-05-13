import argparse
import numpy as np
from whaaaaat import prompt, print_json


PLAYGROUND = "Playground"
VAX_SPOT = "Vaccination Spot"
QUARANTINE = "Quarantine Center"
NOTHING = "Nothing"

#index 0 = Playground, index 1 = Vaccination Spot, index 2 = Quarantine Center, index 3 = Nothing
uintToLocationList = [PLAYGROUND, VAX_SPOT, QUARANTINE, NOTHING]
#maps the long form name of a location to its index
locationToUintDict = dict([(PLAYGROUND, 0), (VAX_SPOT, 1), (QUARANTINE, 2), (NOTHING, 3)])

#Credit: Paul Manta https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
class PointSingleton:

    _instance_dict = dict()
    
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self, x, y):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        """
        try:
            return self._instance_dict[f"{str(x)},{str(y)}"]
        except Exception:
            self._instance_dict[f"{str(x)},{str(y)}"] = self._decorated(x, y)
            return self._instance_dict[f"{str(x)},{str(y)}"]

    def __call__(self, x, y):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

class EdgeSingleton:

    _instance_dict = dict()
    
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self, x, y):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        """
        try:
            return self._instance_dict[f"{str(x)},{str(y)}"]
        except Exception:
            try:
                return self._instance_dict[f"{str(y)},{str(x)}"]
            except Exception:
                self._instance_dict[f"{str(x)},{str(y)}"] = self._decorated(x, y)
                return self._instance_dict[f"{str(x)},{str(y)}"]

    def __call__(self, x, y):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@PointSingleton
class Point:
    def __init__(self, x, y):
        self._x, self._y = x, y

    def __str__(self):
        return "({}, {})".format(self._x, self._y)

@EdgeSingleton
class Edge:
    def __init__(self, point1, point2):
        self._point1, self._point2 = point2, point2
        self._score = 0
    
    def __str__(self):
        return "{} <-> {}".format(self._point1, self._point2)

    def add_score(self, scoreToAdd):
        self._score += scoreToAdd

    def get_score(self):
        return self._score

class GridItem:
    def __init__(self, uintValue, row, column):
        self._value = uintValue
        self._top_left = Point.instance(row, column)
        self._top_right = Point.instance(row, column + 1)
        self._bottom_left = Point.instance(row + 1, column)
        self._bottom_right = Point.instance(row + 1, column + 1)
        self.initialize_edges()

    def initialize_edges(self):
        edge = Edge.instance(self._top_left, self._top_right)
        #TODO: need to actually get score from dict instead of this
        edge.add_score(self._value)
        edge = Edge.instance(self._top_right, self._bottom_right)
        edge.add_score(self._value)
        edge = Edge.instance(self._bottom_right, self._bottom_left)
        edge.add_score(self._value)
        edge = Edge.instance(self._top_left, self._bottom_left)
        edge.add_score(self._value)

        #TODO: when an edge passes by two playgrounds --> make score infinity

def askQuestions(num_rows, num_cols):
    table = np.zeros((num_rows, num_cols), dtype=object)
    for row in range(num_rows):
        for col in range(num_cols):
            question = [{
                "type": "list",
                "name": "entry",
                "message": f"What do you want to enter at row {row}, column {col}?",
                "choices": [
                    PLAYGROUND,
                    VAX_SPOT,
                    QUARANTINE,
                    NOTHING
                ]
            }]
            answer = prompt(question)
            table[row, col] = GridItem(locationToUintDict[answer["entry"]], row, col)
    return table

def main():
    parser = argparse.ArgumentParser(description='Covid-19 Map Simulation')
    parser.add_argument('num_rows', type=int, help='The number of rows')
    parser.add_argument('num_columns', type=int, help='The number of columns')

    args = parser.parse_args()

    num_rows = args.num_rows
    num_columns = args.num_columns

    if num_rows <= 0 or num_columns <= 0:
        raise argparse.ArgumentTypeError("You cannot enter a negative value for num_rows or num_columns")

    print(f"Creating a map with {num_rows} rows and {num_columns} columns")
    
    table = askQuestions(num_rows, num_columns)

if __name__ == "__main__":
    main()