from sudoku import Sudoku
from copy import deepcopy
# import numpy as np


class CSP_Solver(object):
    """
    This class is used to solve the CSP with backtracking using the minimum value remaining heuristic.
    HINT: you will likely want to implement functions in the backtracking sudo code in figure 6.5 in the text book.
            We have provided some prototypes that might be helpful. You are not required to use any functions defined
            here and can modify any function other than the solve method. We will test your code with the solve method
            and so it must have no parameters and return the type it says. 
         
    """
    def __init__(self, puzzle_file):
        '''
        Initialize the solver instance. The lower the number of the puzzle file the easier it is. 
        It is a good idea to start with the easy puzzles and verify that your solution is correct manually. 
        You should run on the hard puzzles to make sure you aren't violating corner cases that come up.
        Harder puzzles will take longer to solve.
        :param puzzle_file: the puzzle file to solve 
        '''
        self.unassigned = []  # list of unassigned cells as tuples (row, col)
        self.sudoku = Sudoku(puzzle_file) # this line has to be here to initialize the puzzle
        # print ("Sudoku", Sudoku.board_str(self.sudoku))
        # print("board", self.sudoku.board) - List of Lists 
        self.num_guesses = 0
        # self.unassigned = deque()
        self.assignment = {}
        
        # make domian the Given Puzzle
        self.domains = deepcopy(self.sudoku.board)
        # Overwrite 0's with their possibilities.
        for row in range(0,9):
            for col in range(0,9):
                # extract value
                value = self.sudoku.board[row][col]
                if value == 0:
                    self.domains[row][col] = [1,2,3,4,5,6,7,8,9]
                    # add this index to unassigned for faster look ups
                    self.unassigned.append((row,col))
                else: 
                    self.domains[row][col] = value
                    self.assignment[(row, col)] = value

        vars=[]
        # self.csp = CSP(vars, self.domains)

    ################################################################
    ### YOU MUST EDIT THIS FUNCTION!!!!!
    ### We will test your code by constructing a csp_solver instance
    ### e.g.,
    ### csp_solver = CSP_Solver('puz-001.txt')
    ### solved_board, num_guesses = csp_solver.solve()
    ### so your `solve' method must return these two items.
    ################################################################
    def solve(self):
        '''
        This method solves the puzzle initialized in self.sudoku 
        You should define backtracking search methods that this function calls
        The return from this function NEEDS to match the correct type
        Return None, number of guesses no solution is found
        :return: tuple (list of list (ie [[]]), number of guesses
        '''
        assignment = self.backtracking_search()
        if assignment:
            print("Solution found!")
            self.write_assignment_to_board(assignment)
        else:
            print("recursive backtracking returned FAILURE")
        print("board", self.sudoku.board)
        print("num",self.num_guesses)
        return self.sudoku.board, self.num_guesses

    def backtracking_search(self):
        '''
        This function might be helpful to initialize a recursive backtracking search function
        You do not have to use it.
        
        :param sudoku: Sudoku class instance
        :param csp: CSP class instance
        :return: board state (list of lists), num guesses 
        '''

        return self.recursive_backtracking(self.assignment)

    def recursive_backtracking(self, assignment):
        '''
        recursive backtracking search function.
        You do not have to use this
        :param sudoku: Sudoku class instance
        :param csp: CSP class instance
        :return: board state (list of lists)
        '''
        # returns a solution or failure

        # if assignment is complete then return the assignment
        if len(assignment) == 81:  # 81 assignments signals complete board
            return assignment

        # update the domain possibilities for each variable (i.e., cell)
        # to choose next variable to work with, using MRV heuristic
        cell = self.unassigned_var_with_mrv(assignment)
        cellRow = cell[0]
        cellCol = cell[1]

        # assign from domain
        for value in self.domains[cellRow][cellCol]:
            # check if value already exists in same row, column, or box
            if self.is_assignment_valid(assignment, value, cellRow, cellCol):
                assignment[(cellRow, cellCol)] = value
                if (cellRow, cellCol) in self.unassigned:
                    self.unassigned.remove((cellRow, cellCol))
                self.num_guesses += 1
            # recursive call
            if self.recursive_backtracking(assignment):
                return assignment
            # here is the backtracking
            assignment.pop((cellRow, cellCol))
            # reinstate domain as it was prior to the assignment of this backtracked value
            # without this,
             #self.fix_domains(backtracked_value, cellRow, cellCol)
        return False

    def unassigned_var_with_mrv(self, assignment):
        # keep self.unassigned up to date
        for row in range(0, 9):
            for col in range(0, 9):
                if (row, col) not in assignment:
                    if (row, col) not in self.unassigned:
                        self.unassigned.append((row, col))

        # update possibility domains for each var in unassigned
        for (row, col) in self.unassigned:
            # reset domains prior to updating
            # this ensures backtracked cell/value pairs are not
            # potentially left out of any unassigned variable/cell domains
            # and only values currently existing in "assignment" will be taken out of domain
            self.domains[row][col] = [1,2,3,4,5,6,7,8,9]

            # limit domain by row peers
            for i in range(0, 9):
                if (row, i) in assignment:  # checking if key in dict
                    # if any value in row is in unassigned cell's domain
                    if assignment[(row, i)] in self.domains[row][col]:
                        # remove that value from unassigned cell's domain
                        self.domains[row][col].remove(assignment[(row, i)])
            # limit domain by column peers
            for j in range(0, 9):
                if (j, col) in assignment:  # checking if key in dict
                    if assignment[(j, col)] in self.domains[row][col]:
                        self.domains[row][col].remove(assignment[(j, col)])
            # limit domain by box peers
            # first define box depending on unassigned cell coords
            if 0 <= row <= 2:
                box_xmin = 0
                box_xmax = 2
            elif 3 <= row <= 5:
                box_xmin = 3
                box_xmax = 5
            else:
                box_xmin = 6
                box_xmax = 8
            if 0 <= col <= 2:
                box_ymin = 0
                box_ymax = 2
            elif 3 <= col <= 5:
                box_ymin = 3
                box_ymax = 5
            else:
                box_ymin = 6
                box_ymax = 8
            # now that box range is defined, limit domain possibilities by box peers
            for k in range(box_xmin, box_xmax + 1):
                for m in range(box_ymin, box_ymax + 1):
                    if (k, m) in assignment:  # checking if key in dict
                        if assignment[(k, m)] in self.domains[row][col]:
                            self.domains[row][col].remove(assignment[(k, m)])

        # now we can calculate cell with minimum remain value in its domain
        # this lambda function provides criteria for min evaluation of domain length
        criteria = lambda cell: len(self.domains[cell[0]][cell[1]])
        # finds min domain length of all unassigned cells
        return min(self.unassigned, key=criteria)

    def is_assignment_valid(self, assignment, val, row, col):
        # check row
        for i in range(0, 9):
            if i != col:  # don't want to check against the cell just assigned
                if (row, i) in assignment:
                    if assignment[(row, i)] == val:
                        return False
        # check column
        for j in range(0, 9):
            if j != row:
                if (j, col) in assignment:
                    if assignment[(j, col)] == val:
                        return False
        # check box
        # first define box depending on recently assigned cell coords
        if 0 <= row <= 2:
            box_xmin = 0
            box_xmax = 2
        elif 3 <= row <= 5:
            box_xmin = 3
            box_xmax = 5
        else:
            box_xmin = 6
            box_xmax = 8
        if 0 <= col <= 2:
            box_ymin = 0
            box_ymax = 2
        elif 3 <= col <= 5:
            box_ymin = 3
            box_ymax = 5
        else:
            box_ymin = 6
            box_ymax = 8
        # now that box range is defined, check for box validity
        for k in range(box_xmin, box_xmax + 1):
            for m in range(box_ymin, box_ymax + 1):
                if k != row and m != col:
                    if (k, m) in assignment:
                        if assignment[(k, m)] == val:
                            return False
        return True

    def write_assignment_to_board(self, assignment):
        for i in range(0, 9):
            for j in range(0, 9):
                self.sudoku.board[i][j] = assignment[(i, j)]


if __name__ == '__main__':
    csp_solver = CSP_Solver('puz-100.txt')
    solution, guesses = csp_solver.solve()
    # csp_solver.sudoku.write('puz-001-solved.txt')

