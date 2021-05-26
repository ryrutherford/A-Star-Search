import argparse
import numpy as np
import math
from whaaaaat import prompt, print_json

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

PLAYGROUND = "Playground"
VAX_SPOT = "Vaccination Spot"
QUARANTINE = "Quarantine Center"
NOTHING = "Nothing"

PLAYGROUND_CODE = "P"
VAX_SPOT_CODE = "V"
QUARANTINE_CODE = "Q"
NOTHING_CODE = "N"

#index 0 = Quarantine Center, index 1 = Nothing, index 2 = Vaccination Spot, index 3 = Playground
uint_to_location_list = [QUARANTINE, NOTHING, VAX_SPOT, PLAYGROUND]
uint_to_location_code = [QUARANTINE_CODE, NOTHING_CODE, VAX_SPOT_CODE, PLAYGROUND_CODE]

#maps the index of each location to its color in the map
location_code_to_color_code = dict([(QUARANTINE_CODE,bcolors.OKGREEN), (NOTHING_CODE,bcolors.OKBLUE), (VAX_SPOT_CODE,bcolors.WARNING), (PLAYGROUND_CODE,bcolors.FAIL)])
#maps the long form name of a location to its index in the above list as well as its edge score
location_to_uint_dict = dict([(PLAYGROUND, 3), (VAX_SPOT, 2), (QUARANTINE, 0), (NOTHING, 1)])

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
        self._score = None
    
    def __str__(self):
        return "{} <-> {}".format(self._point1, self._point2)

    def add_score(self, scoreToAdd):
        if self._score is None:
            self._score = scoreToAdd
        #two playgrounds next to each other --> edge value is infinity
        elif self._score == 3 and scoreToAdd == 3:
            self._score = math.inf
        else:
            self._score = (self._score + scoreToAdd)/2

    def get_score(self):
        return self._score

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

def ask_init_questions(num_rows, num_cols):
    table = np.zeros((num_rows, num_cols), dtype=object)
    for row in range(num_rows):
        for col in range(num_cols):
            question = [{
                "type": "list",
                "name": "entry",
                "message": f"What do you want to enter at row {row}, column {col}?",
                "choices": [QUARANTINE, NOTHING, VAX_SPOT, PLAYGROUND]
            }]
            answer = prompt(question)
            table[row, col] = GridItem(location_to_uint_dict[answer["entry"]], row, col)
    return table

def valid_starting_point(x, y, num_rows, num_cols):
    try:
        x = float(x)
        y = float(y)
    except ValueError:
        print("ValueError, at least one of x or y was not a float or integer")
        return False
    if x > num_cols*2 or y > num_rows or x < 0 or y < 0:
        print(f"The coordinates ({x}, {y}) you entered are not in the grid! Please try again")
        return False
    return True

def get_x_and_y_coords(num_rows, num_cols, top_right_of_quarantine_places=None):
    while True:
        question = [
        {
            'type': 'input',
            'name': 'x',
            'message': f'Enter a value for x (accepted range: [0 - {num_cols*2}])',
        },
        {
            'type': 'input',
            'name': 'y',
            'message': f'Enter a value for y (accepted range: [0 - {num_rows}])',
        }
        ]
        answer = prompt(question)
        x = answer["x"]
        y = answer["y"]
        if valid_starting_point(x, y, num_rows, num_cols):
            x = math.ceil(float(x))
            if x % 2 != 0:
                x = x + 1
            #if x is = 0 we need to add 2 as otherwise we won't be at the top right of a grid
            if x == 0:
                x = x + 2
            y = math.floor(float(y))
            #if y is = num_rows we need to subtract 1 since otherwise it won't be at the top right of a grid
            if y == num_rows:
                y = y - 1
            if top_right_of_quarantine_places != None and Point.instance(x, y) not in top_right_of_quarantine_places:
                print(f"The coordinates ({x}, {y}) you entered for the end point are not at the top right of a quarantine place! Please try again")
            else:
                break
    
    return x, y

def ask_placement_questions(num_rows, num_cols, top_right_of_quarantine_places):
    print("You must enter values for the x and y coordinates of the start position")
    start_x, start_y = get_x_and_y_coords(num_rows, num_cols)
    print(f"Nice! Role C will be starting at point ({start_x},{start_y})")
    print("You must enter values for the x and y coordinates of the end position")
    end_x, end_y = get_x_and_y_coords(num_rows, num_cols, top_right_of_quarantine_places)
    print(f"Nice! The ending point ({end_x},{end_y}) you entered is the top right of a quarantine place")
    #we don't do anything with the endpoints so we just return the start points ¯\_(ツ)_/¯
    return start_x, start_y

def wrap_location_code_in_color(code):
    return location_code_to_color_code[code] + code + bcolors.ENDC

def drawHorizontal(left_point, right_point, j, col):
    out = ""
    out += bcolors.OKCYAN + str(left_point) + bcolors.ENDC
    out += "--------"
    if j == col - 1:
        out += bcolors.OKCYAN + str(right_point) + bcolors.ENDC
        out += "\n"
    return out

def drawVertical(halfPointLength, value, j, y, col):
    out = ""
    for x in range(halfPointLength):
        out += " "
    code = wrap_location_code_in_color(uint_to_location_code[value])
    if y == 1:
        out += f"|      {code}   "
    else:
        out += "|          "
    if j == col - 1:
        for x in range(halfPointLength):
            out += " "
        out += "|\n"
    return out

def draw_grid(table):
    row, col = table.shape
    out = ""
    for i in range(row):
        for j in range(col):
            gridItem = table[i,j]
            top_left, top_right, _, _ = gridItem.get_points()
            out += drawHorizontal(top_left, top_right, j, col)
        for y in range(3):
            for j in range(col):
                gridItem = table[i,j]
                out += drawVertical(len(str(top_left)) // 2, gridItem.get_value(), j, y, col)
        if i == row - 1:
            for j in range(col):
                gridItem = table[i,j]
                _, _, bottom_right, bottom_left = gridItem.get_points()
                out += drawHorizontal(bottom_left, bottom_right, j, col)
    print(out)

#getting the top right points of each quarantine place in the map
def get_top_right_of_quarantine_places(table):
    row, col = table.shape
    quarantine_places_top_right_list = []
    for i in range(row):
        for j in range(col):
            if uint_to_location_code[table[i,j].get_value()] == QUARANTINE_CODE:
                quarantine_places_top_right_list.append(table[i,j].get_points()[1])
    return quarantine_places_top_right_list

def main():
    parser = argparse.ArgumentParser(description='Covid-19 Map Simulation')
    parser.add_argument('num_rows', type=int, help='The number of rows')
    parser.add_argument('num_columns', type=int, help='The number of columns')

    args = parser.parse_args()

    num_rows = args.num_rows
    num_columns = args.num_columns

    if num_rows <= 0 or num_columns <= 0:
        raise argparse.ArgumentTypeError("You cannot enter a negative or zero value for num_rows or num_columns")

    print(f"Creating a map with {num_rows} rows and {num_columns} columns")
    
    table = ask_init_questions(num_rows, num_columns)
    draw_grid(table)
    top_right_of_quarantine_places = get_top_right_of_quarantine_places(table)
    if(top_right_of_quarantine_places == []):
        print("The map you entered has no quarantine places! Exiting program")
        exit()
    ask_placement_questions(num_rows, num_columns, top_right_of_quarantine_places)


if __name__ == "__main__":
    main()