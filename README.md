# COMP 472 A1

## Requirements
- You must install the necessary packages to run this program. These packages can be found in the requirements.txt file
- Please note that the prompt toolkit must be of version 1.0.14, otherwise the program won't work
- I used pip to install my packages, the process may be different for conda

## Running the Program
- The program is made to be run on the command line with the following format: `python a1.py <num_rows> <num_columns>`
- For example if you wanted to run the program with a grid with 3 rows and 4 columns you would run `python a1.py 3 4`
- The program will display an error message if it is missing inputs or the inputs are invalid (e.g. rows or columns <= 0)
- After running the program, the user will be prompted to populate the grid, cell by cell
- The user can select from the 4 available options (Quarantine Center, Vaccination Spot, Playground, and Nothing)
- After the user selects a location for each cell, the grid will be displayed
- The user will then be prompted to select a starting point by entering a valid x coordinate followed by a valid y coordinate (the grid display identifies the location of the whole coordinates in case you are unsure of where they are located)
- After selecting their starting point they will select their ending point in the same fashion. The ending point is more constrained as it must be at the top right of a quarantine center since this program only deals with Role C
- The coordinates are always rounded to the top right based on the assignment specifications
- If the user inputs invalid coordinates then they will be reprompted to enter the coordinates until they enter valid ones
- After this, the user's work is done. The program will find the optimal path (if it exists) using A* Search and output the path based on the coordinates as well as the score of the path. If no path exists, a message will be displayed to the user. I only outputted the path in text format since the assignment didn't specify how they wanted us to display it
- The program ends after the A* search concludes. In order to run the program with new inputs you must follow the steps at the beginning of this section