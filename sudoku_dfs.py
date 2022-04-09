import copy
import time
import pygame
import sys

rowSize = 0

# read from input file
# input file name when run the cmd
if(len(sys.argv) > 1):
    fileName = sys.argv[1]
else: fileName = "input1.txt"

# count num of lines in file
def countLines():
    with open(fileName) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

rowSize = countLines()

# get number of line in f
grid = [['x' for i in range(rowSize)] for j in range(rowSize)]

# read from file
with open(fileName, 'r') as f:
    i = 0
    for line in f:
        # split the line into a list
        line = list(line)
        # for each element in the list
        for j in range(rowSize):
            # if the element is a dot
            if line[j] == '.':
                # set the element to 0
                grid[i][j] = 0
            else:
                # set the element to othernumber
                grid[i][j] = int(line[j])
        # increment the row
        i += 1


class MyGame(object):
    def __init__(self, initial):
        self.initial = initial # initial state
        self.size = len(initial) # size of grid
        self.height = int(self.size/3) # height of square
        global rowSize
        rowSize = self.size # global var for size of grid

    def checkIfOkay(self, state):
        # max sum
        exp_sum = sum(range(1, self.size+1))

        # Returns false if expected sum of row or column are invalid
        for row in range(self.size):
            if (len(state[row]) != self.size) or (sum(state[row]) != exp_sum):
                return False
            column_sum = 0
            for column in range(self.size):
                column_sum += state[column][row]
            if (column_sum != exp_sum):
                return False

        # Returns false if expected sum of a quadrant is invalid
        for column in range(0,self.size,3):
            for row in range(0,self.size,self.height):
                block_sum = 0
                for block_row in range(0,self.height):
                    for block_column in range(0,3):
                        block_sum += state[row + block_row][column + block_column]

                if (block_sum != exp_sum):
                    return False
        return True

    # Return first empty spot
    def get_next(self, boardSize, state):
        for row in range(boardSize):
            for column in range(boardSize):
                if state[row][column] == 0:
                    return row, column

    # Return set of valid numbers from values that do not appear in used
    def filter_values(self, values, used):
        return [number for number in values if number not in used]

    # Filter valid values based on row
    def filter_row(self, state, row):
        values = range(1, self.size + 1)
        used = [number for number in state[row] if number > 0]
        options = self.filter_values(values, used)
        return options

    # Filter valid values based on column
    def filter_col(self, options, state, column):
        for row in range(self.size):
            if state[row][column] != 0 and state[row][column] in options:
                options.remove(state[row][column])
        return options

    # Filter valid values based on square
    def filter_square(self, options, state, row, column):
        in_block = []
        row_start = int(row/self.height)*self.height
        column_start = int(column/3)*3
        
        for block_row in range(0, self.height):
            for block_column in range(0,3):
                in_block.append(state[row_start + block_row][column_start + block_column])
        options = self.filter_values(options, in_block)
        return options


    def get_possible_states(self, state):
        row,column = self.get_next(self.size, state)

        # Remove a square's invalid values
        options = self.filter_row(state, row)
        options = self.filter_col(options, state, column)
        options = self.filter_square(options, state, row, column)

        # Return states for each valid option
        for number in options:
            new_state = copy.deepcopy(state)
            new_state[row][column] = number
            yield new_state

class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent

    def expand(self, problem, parent):
        return [Node(state, parent) for state in problem.get_possible_states(self.state)]

    def get_parent(self):
        return self.parent

    def print(self):
        print(self.state)


solvedPath = [] # save rowID, colID, value 

def get_all_path(node):
    global solvedPath
    path = []
    while node:
        path.append(node)
        node = node.get_parent()
    path.reverse()
    for i in range(len(path)):
        if i > 0:
            diffRow, diffCol, value = find_difference(path[i-1].state, path[i].state)
            solvedPath.append((diffRow, diffCol, value))

def find_difference(state1, state2):
    value = -1
    diffRow = -1
    diffCol = -1
    for row in range(len(state1)):
        for column in range(len(state1[row])):
            if state1[row][column] != state2[row][column]:
                value = state2[row][column]
                diffRow = row
                diffCol = column
    return diffRow, diffCol, value

myBoard = []

def DFS(problem):
    start = Node(problem.initial)
    # if problem.checkIfOkay(start.state):
    #     return start.state

    stack = []
    stack.append(start)

    # count
    count  = 0

    while stack: 
        node = stack.pop()
        count += 1
        if problem.checkIfOkay(node.state):
            get_all_path(node) # save path to solution
            global myBoard
            myBoard = copy.deepcopy(node.state) # save to global var
            print("Solved after checked {} nodes".format(count))
            return node.state
            
        stack.extend(node.expand(problem, node))
        
    return None

def printBoard(board):
    for row in board:
        print(row)

def create_ui():
    # pygame create
    pygame.init()

    # size of the window
    MY_SIZE = 700
    WIDTH = MY_SIZE
    HEIGHT = MY_SIZE

    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # title
    pygame.display.set_caption("Sudoku Solver (Space: generate one, Enter: get all)")


    # set background color to white
    WHITE = (255, 255, 255)
    screen.fill(WHITE)


    # create lines each pixels
    for i in range(rowSize):
        if i % (rowSize/3) == 0 and i > 0 and i < rowSize - 1:
            pygame.draw.line(screen, (0, 0, 0), (0, i * MY_SIZE/rowSize), (WIDTH, i * MY_SIZE/rowSize), 4)
        else:
            pygame.draw.line(screen, (0, 0, 0), (0, i * MY_SIZE/rowSize), (WIDTH, i * MY_SIZE/rowSize))

    for j in range(rowSize):
        if j % 3 == 0 and j > 0 and j < rowSize - 1:
            pygame.draw.line(screen, (0, 0, 0), (j * MY_SIZE/rowSize, 0), (j * MY_SIZE/rowSize, HEIGHT), 4)
        else:
            pygame.draw.line(screen, (0, 0, 0), (j * MY_SIZE/rowSize, 0), (j * MY_SIZE/rowSize, HEIGHT))

    k = 0 # path index
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            # key pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if(k >= len(solvedPath)):
                        print("No more path")
                        break

                    i = solvedPath[k][0]
                    j = solvedPath[k][1]
                    value = solvedPath[k][2]

                    if value != 0:
                        font = pygame.font.SysFont('arial', 50)
                        # set font color to red
                        text = font.render(str(value), True, (0, 0, 0))
                        screen.blit(text, (j * WIDTH/rowSize + 27, i * HEIGHT/rowSize + 12)) 
                    
                    pygame.display.update()
                    k += 1
                if event.key == pygame.K_RETURN:
                    while k < len(solvedPath):
                        i = solvedPath[k][0]
                        j = solvedPath[k][1]
                        value = solvedPath[k][2]

                        # draw number into the board with value of solvedPath[k][0][2]
                        if value != 0:
                            font = pygame.font.SysFont('arial', 50)
                            text = font.render(str(value), True, (0, 0, 0))
                            screen.blit(text, (j * WIDTH/rowSize + 27, i * HEIGHT/rowSize + 12))
                        
                        pygame.display.update()
                        k += 1

        # draw the board
        for i in range(rowSize):
            for j in range(rowSize):
                if grid[i][j] != 0:
                    font = pygame.font.SysFont('arial', 50)
                    text = font.render(str(grid[i][j]), True, (0, 0, 255))
                    screen.blit(text, (j * WIDTH/rowSize + 27, i * HEIGHT/rowSize + 12))
        pygame.display.flip()


def solve_dfs(board):
    print ("DFS ?")

    t_start = time.time()
    solution = DFS(MyGame(board))
    t_end = time.time()
    take_time = t_end - t_start

    if solution:
        print ("Solution: ")
        printBoard(solution)
    else:
        print ("No sulution")

    # time execution
    print ("Time: " + str(take_time) + " seconds")

    create_ui()



# main
solve_dfs(grid)