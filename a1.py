import argparse
import numpy as np
import math
import heapq
from Colors import bcolors
from Edge import Edge
from Point import Point
from GridItem import GridItem
from whaaaaat import prompt, print_json

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

#asks the user what they want to populate each grid item with
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

#determines whether the point the user entered falls within the grid
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

#gets x and y coordinates from the user as input on the command line
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

#asks the user for the start and end points
def ask_placement_questions(num_rows, num_cols, top_right_of_quarantine_places):
    print("You must enter values for the x and y coordinates of the start position")
    start_x, start_y = get_x_and_y_coords(num_rows, num_cols)
    print(f"Nice! Role C will be starting at point ({start_x},{start_y})")
    print("You must enter values for the x and y coordinates of the end position")
    end_x, end_y = get_x_and_y_coords(num_rows, num_cols, top_right_of_quarantine_places)
    print(f"Nice! The ending point ({end_x},{end_y}) you entered is the top right of a quarantine place")
    #we don't do anything with the endpoints so we just return the start points ¯\_(ツ)_/¯
    return start_x, start_y

#wraps location codes in colours for the command line interface
def wrap_location_code_in_color(code):
    return location_code_to_color_code[code] + code + bcolors.ENDC

#helper function used to draw the horizontal part of the grid
def drawHorizontal(left_point, right_point, j, col):
    out = ""
    out += bcolors.OKCYAN + str(left_point) + bcolors.ENDC
    out += "--------"
    if j == col - 1:
        out += bcolors.OKCYAN + str(right_point) + bcolors.ENDC
        out += "\n"
    return out

#helper function used to draw the vertical part of the grid
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

#draws the grid based on the inputs of the user
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

#calculates heuristic for the current point based on the locations of the destination (quarantine center)
def calculate_heuristic(current, top_right_of_quarantine_places):
    current_x = current.get_x()
    current_y = current.get_y()
    best_h = math.inf
    for i in range(len(top_right_of_quarantine_places)):
        valid_destination = top_right_of_quarantine_places[i]
        #we use manhattan distance with each move costing 0.5
        #we subtract 0.5 to account for the 0 costing edges that are possible with quarantine places
        manhattan_distance = abs((current_x - valid_destination.get_x())/4) + abs((current_y - valid_destination.get_y())/2) - 0.5
        if manhattan_distance <= 0:
            return 0
        elif manhattan_distance < best_h:
            best_h = manhattan_distance
    return best_h

#returns a list of direct neighbours for the passed in point
def get_neighbours_of_point(point, num_rows, num_cols):
    x = point.get_x()
    y = point.get_y()
    neighbours = []
    if x - 2 >= 0:
        neighbours.append(Point.instance(x-2, y))
    if y - 1 >= 0:
        neighbours.append(Point.instance(x, y-1))
    if y + 1 <= num_rows:
        neighbours.append(Point.instance(x, y+1))
    if x + 2 <= num_cols*2:
        neighbours.append(Point.instance(x + 2, y))
    return neighbours

#reconstructs the path from the start point to the goal point
def reconstruct_path(came_from, current):
    total_path = [current]
    while str(current) in came_from.keys():
        current = came_from[str(current)]
        total_path.append(current)
    total_path.reverse()
    return total_path

#used to print the optimal path
def print_path(path):
    for i in range(len(path)):
        print(str(path[i]), end='')
        if i != len(path) - 1:
            print('-->', end='')
    print('')

#performs the A* search
def a_star(start, goals, num_rows, num_cols):
    open_set = [start]
    heapq.heapify(open_set)
    came_from = dict()

    while len(open_set) > 0:
        current = heapq.heappop(open_set)

        if current in goals:
            print(f"We have found the shortest path")
            path = reconstruct_path(came_from, current)
            print_path(path)
            return
        
        #iterating over the neighbours of the current point, updating the g and f scores if necessary
        neighbours = get_neighbours_of_point(current, num_rows, num_cols)
        for i in range(len(neighbours)):
            neighbour = neighbours[i]
            tentative_g_score = current.get_g_score() + Edge.instance(current, neighbour).get_score()
            if tentative_g_score < neighbour.get_g_score():
                came_from[str(neighbour)] = current
                neighbour.set_g_score(tentative_g_score)
                neighbour.set_f_score(tentative_g_score + calculate_heuristic(neighbour, goals))
                if neighbour not in open_set:
                    heapq.heappush(open_set, neighbour)

    print("No path is found. Please try again!")

#calls all the necessary functions to initialize the grid, collect the start/end point and perform A* search
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

    #getting the point object that refers to the start point the user entered
    start_x, start_y = ask_placement_questions(num_rows, num_columns, top_right_of_quarantine_places)
    start_point = Point.instance(start_x, start_y)
    start_point.set_f_score(calculate_heuristic(start_point, top_right_of_quarantine_places))
    start_point.set_g_score(0)
    a_star(start_point, top_right_of_quarantine_places, num_rows, num_columns)


if __name__ == "__main__":
    main()