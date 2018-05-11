"""COMP30024 Artificial Intelligence Project Part B (2018 Sem 1)

Authors:
Joanna Grace Cho Ern LEE (710094)
Jia Shun LOW (743436)

This module contains some functions from Part A, modified to fit Part B's
requirements, as well as newly written helper functions, related to cell
operations and movements. These functions are designed to be used in the
Minimax module.
"""
START_PHASE = 0
INITIAL_BOARD_SIZE = 8
STARTING_LINE = 2
PLACEMENT_LINE = 2
STARTING_PIECES = 12
LOOKAHEAD_MOVE = 3
MOVEMENT_ONE = 128
MOVEMENT_TWO = 192
BEST_STARTING_COORD = (3,4)
QUAD_ONE = [(x, y) for x in range(INITIAL_BOARD_SIZE//2)
                   for y in range(INITIAL_BOARD_SIZE//2)]
QUAD_TWO = [(x, y) for x in range(INITIAL_BOARD_SIZE//2, INITIAL_BOARD_SIZE)
                   for y in range(INITIAL_BOARD_SIZE//2)]
QUAD_THREE = [(x, y) for x in range(INITIAL_BOARD_SIZE//2)
                     for y in range(INITIAL_BOARD_SIZE//2, INITIAL_BOARD_SIZE)]
QUAD_FOUR = [(x, y) for x in range(INITIAL_BOARD_SIZE//2, INITIAL_BOARD_SIZE)
                    for y in range(INITIAL_BOARD_SIZE//2, INITIAL_BOARD_SIZE)]

class GameState:
    """
    Class which stores the state of the game at a given time. This includes
    the locations of all the white pieces and all the black pieces on the board.
    It also keeps track of current phase and current size of board.
    """

    def __init__(self, boardSize, whitePieces, blackPieces, isWhitePlayer, isWhiteTurn):
        self.size = boardSize
        self.phase = 0
        self.whitePieces = whitePieces
        self.blackPieces = blackPieces
        self.isWhitePlayer = isWhitePlayer
        self.isWhiteTurn = isWhiteTurn
        self.corners = {0,7}

    def removeOutOfBounds(self, pieces):
        """Removes pieces that are out of bounds"""
        newPieces = set()
        for i, j in pieces:
            if self.withinBounds(i, j) and not self.isCorner(i, j):
                newPieces.add((i, j))
        return newPieces

    def shrink(self, newPhase):
        """Shrinks board to new size according to newPhase argument given"""
        if self.size == INITIAL_BOARD_SIZE - 2*newPhase: return # already shrank

        self.corners = {newPhase,INITIAL_BOARD_SIZE-newPhase-1}
        self.size = INITIAL_BOARD_SIZE - 2*newPhase
        self.whitePieces = self.removeOutOfBounds(self.whitePieces)
        self.blackPieces = self.removeOutOfBounds(self.blackPieces)
        self.whitePieces = removeEatenPieces(self, True)
        self.blackPieces = removeEatenPieces(self, False)

    def isEndState(self):
        """
        Checks if this state is an end state (there is a winner). The game
        ends if either player has fewer than 2 pieces remaining. The player
        with 2 or more pieces remaining wins the game. If both players have
        fewer than 2 pieces remaining in the same turn (for example, due to
        multiple pieces being eliminated during the shrinking of the board),
        then the game ends in a tie.
        """
        return (len(self.whitePieces) < 2) or (len(self.blackPieces) < 2)

    def printBoard(self):
        """Prints board at current state"""
        print("Printing board")
        board = [[ '-' for y in range(8) ] for x in range(8)]
        for i,j in self.whitePieces:
            board[j][i] = 'O'
        for i,j in self.blackPieces:
            board[j][i] = '@'
        for row in board:
            print(row)

    def calcMovesForCoord(self, coord, enemy):
        """
        Returns a list of all coordinates reachable from given coord.
        (Suicides are allowed)
        """
        i, j = coord
        possibleMoves = set()
        for move in [self.canGoRight_(i, j),
                     self.canGoLeft_(i, j),
                     self.canGoUp_(i, j),
                     self.canGoDown_(i, j)]:
            if move: possibleMoves.add((coord, move))

        return possibleMoves# - eaten

    def isEmpty_(self, i,j):
        """Checks if there are any pieces in the cell specified by (i, j)."""

        return ((i, j) not in self.blackPieces
                and (i, j) not in self.whitePieces
                and not self.isCorner(i, j))

    def canJumpRight_(self, i, j):
        """Checks if piece can jump right"""
        if self.withinBounds(i+2, j) and self.isEmpty_(i+2, j):
            return (i+2, j)

    def canJumpLeft_(self, i, j):
        """Checks if piece can jump left"""
        if self.withinBounds(i-2, j) and self.isEmpty_(i-2, j):
            return (i-2, j)

    def canJumpUp_(self, i, j):
        """Checks if piece can jump up"""
        if self.withinBounds(i, j-2) and self.isEmpty_(i, j-2):
            return (i, j-2)

    def canJumpDown_(self, i, j):
        """Checks if piece can jump down"""
        if self.withinBounds(i, j+2) and self.isEmpty_(i, j+2):
            return (i, j+2)

    def canGoRight_(self, i, j):
        """Checks if piece can move right"""
        if self.withinBounds(i+1, j) and self.isEmpty_(i+1, j):
            return (i+1, j)
        return self.canJumpRight_(i, j)

    def canGoLeft_(self, i, j):
        """Checks if piece can move left"""
        if self.withinBounds(i-1, j) and self.isEmpty_(i-1, j):
            return (i-1, j)
        return self.canJumpLeft_(i, j)

    def canGoUp_(self, i, j):
        """Checks if piece can move up"""
        if self.withinBounds(i, j-1) and self.isEmpty_(i, j-1):
            return (i, j-1)
        return self.canJumpUp_(i, j)

    def canGoDown_(self, i, j):
        """Checks if piece can move down"""
        if self.withinBounds(i, j+1) and self.isEmpty_(i, j+1):
            return (i, j+1)
        return self.canJumpDown_(i, j)

    def isCorner(self, i, j):
        """Checks if coordinates given is a corner of the board."""
        return i in self.corners and j in self.corners

    def withinBounds(self, i, j):
        """Checks if coordinates given is on the board."""
        return (min(self.corners) <= i <= max(self.corners) and
                (min(self.corners) <= j <= max(self.corners)) and
                not self.isCorner(i, j))

    def isEnemy(self, enemyPieces, coordinate):
        """Checks if coordinates belong to the enemy (or is a corner)."""
        i, j = coordinate
        return (self.withinBounds(i, j) and
                (coordinate in enemyPieces or self.isCorner(i, j)))

    def isEnemyOrCorner(self, coordinate):
        """Checks if coordinates belong to the enemy (or is a corner)."""
        i, j = coordinate
        return coordinate in self.enemyPieces() or self.isCorner(i, j)

    def isAlly(self, coordinate):
        """Checks if coordinates belong to ally"""
        i, j = coordinate
        return (self.withinBounds(i, j) and
                (coordinate in self.allyPieces() or self.isCorner(i, j)))

    def canEatSide(self, enemyPieces, side1, side2):
        """Checks a piece between side1 and side2 will be eaten."""
        return self.isEnemy(enemyPieces, side1) and self.isEnemy(enemyPieces, side2)

    def enemyPieces(self):
        """Gets enemy pieces based on player colour"""
        if self.isWhitePlayer:
            return self.blackPieces
        return self.whitePieces

    def allyPieces(self):
        """Gets ally pieces based on player colour"""
        if self.isWhitePlayer:
            return self.whitePieces
        return self.blackPieces


def getEaten(state, eatingPieces, toEatPieces):
    """Gets pieces that will be eaten"""
    toRemove = set()
    for piece in toEatPieces:
        # check if piece can be eaten from up and down / left and right
        # by checking if within bounds and if they are corner or white.
        if (state.canEatSide(eatingPieces, up(piece), down(piece)) or
            state.canEatSide(eatingPieces, left(piece), right(piece))):
                toRemove.add(piece)
    return toRemove


def removeEatenPieces(state, eatWhite):
    """Given both sets of coordinates, remove own eaten pieces."""
    if eatWhite: # priority to eating blackPieces
        toEatPieces = state.whitePieces.copy()
        eatingPieces = state.blackPieces.copy()
    else:
        toEatPieces = state.blackPieces.copy()
        eatingPieces = state.whitePieces.copy()

    toRemove = getEaten(state, eatingPieces, toEatPieces)
    for pieceToRemove in toRemove:
        toEatPieces.remove(pieceToRemove)
    return toEatPieces

###############################################################################
#           Functions that return coord of cells up down left right           #
###############################################################################
def up(coord):
    x,y = coord
    return x,y-1
def down(coord):
    x,y = coord
    return x, y+1
def left(coord):
    x,y = coord
    return x-1, y
def right(coord):
    x,y = coord
    return x+1, y

###############################################################################
#         Functions that return coord of cells two up down left right         #
###############################################################################
def twoUp(coord):
    x,y = coord
    return x,y-2
def twoDown(coord):
    x,y = coord
    return x, y+2
def twoLeft(coord):
    x,y = coord
    return x-2, y
def twoRight(coord):
    x,y = coord
    return x+2, y
