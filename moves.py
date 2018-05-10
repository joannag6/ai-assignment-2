# Some functions from Part A, modified to fit Part B's requirements
# Also contains newly written helper functions, related to cell operations and movement.
START_PHASE = 0
INITIAL_BOARD_SIZE = 8


class GameState:
    """
    Class which stores the state of the game at a given time. This includes
    the locations of all the white pieces and all the black pieces on the board.
    It also keeps track of phase, whose turn it is, and current size of board.b
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
        newPieces = set()
        for i, j in pieces:
            if self.withinBounds(i, j) and not self.corner(i, j):
                newPieces.add((i, j))
        return newPieces

    def shrink(self, newPhase):
        if newPhase == 1:
            self.corners = {1,6}
            self.size = 6
        if newPhase == 2:
            self.corners = {2,5}
            self.size = 4
        self.whitePieces = self.removeOutOfBounds(self.whitePieces)
        self.blackPieces = self.removeOutOfBounds(self.blackPieces)
        removeEatenPieces(self, True)
        removeEatenPieces(self, False)


    def updateSets(self, newWhitePieces, newBlackPieces):
        """Updates the locations of the white and black pieces on the board."""
        self.whitePieces = newWhitePieces
        self.blackPieces = newBlackPieces

    # check if given state is an end state (there is a winner)
    # The game ends if either player has fewer than 2 pieces remaining. In this
    # case, the player with 2 or more pieces remaining wins the game. If both
    # players have fewer than 2 pieces remaining as a result of the same turn
    # (for example, due to multiple pieces being eliminated during the shrinking
    # of the board), then the game ends in a tie.
    def isEndState(self):
        return (len(self.whitePieces) < 2) or (len(self.blackPieces) < 2)

    def printBoard(self):
        print("Printing board")
        board = [[ '-' for y in range(8) ] for x in range(8)]
        for i,j in self.whitePieces:
            board[j][i] = 'O'
        for i,j in self.blackPieces:
            board[j][i] = '@'
        for row in board:
            print(row)

    def calcMovesForCoord(self, coord, enemy):
        """Returns a list of all coordinates reachable from given coord."""
        i, j = coord
        moveList = []
        for move in [self.canGoRight_(i, j),
                     self.canGoLeft_(i, j),
                     self.canGoUp_(i, j),
                     self.canGoDown_(i, j)]:
            if move and len(canEat(self, enemy, [move])) == 0:
                moveList.append((coord, move))
        return moveList

    def isEmpty_(self, i,j):
        """Checks if there are any pieces in the cell specified by (i, j)."""

        return ((i, j) not in self.blackPieces
                and (i, j) not in self.whitePieces
                and not self.corner(i, j))

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


    def corner(self, i, j):
        """Checks if coordinates given is a corner of the board."""
        return i in self.corners and j in self.corners


    def withinBounds(self, i, j):
        """Checks if coordinates given is on the board."""
        # TODO: find a better way to do this.
        corners = self.corners
        return (min(corners) <= i <= max(corners) and
                (min(corners) <= j <= max(corners)) and
                not self.corner(i, j))

    def isEnemy(self, enemyPieces, coordinate):
        """Checks if coordinates belong to the enemy (or is a corner)."""
        i, j = coordinate
        return (self.withinBounds(i, j) and coordinate in enemyPieces) or self.corner(i, j)

    def isAlly(self, allyPieces, coordinate):
        """Checks if coordinates belong to ally"""
        i, j = coordinate
        return self.withinBounds(i, j) and (coordinate in allyPieces or self.corner(i, j))


    def canEatSide(self, enemyPieces, side1, side2):
        """Checks a piece between side1 and side2 will be eaten."""
        return self.isEnemy(enemyPieces, side1) and self.isEnemy(enemyPieces, side2)

    def enemyPieces(self):
        if self.isWhitePlayer:
            return self.blackPieces
        else:
            return self.whitePieces

    def allyPieces(self):
        if self.isWhitePlayer:
            return self.whitePieces
        else:
            return self.blackPieces

def canEat(state, eatingPieces, toEatPieces):
    toRemove = []
    for piece in toEatPieces:
        i,j = piece
        down = (i,j+1)
        up = (i,j-1)
        left = (i-1,j)
        right = (i+1,j)

        # check if piece can be eaten from up and down / left and right
        # by checking if within bounds and if they are corner or white.
        if state.canEatSide(eatingPieces, up, down) or state.canEatSide(eatingPieces, left, right):
            toRemove.append(piece)
    return toRemove

def removeEatenPieces(state, eatWhite):
    """Given both sets of coordinates, remove own eaten pieces."""
    if eatWhite: # priority to eating blackPieces
        toEatPieces = state.whitePieces
        eatingPieces = state.blackPieces
    else:
        toEatPieces = state.blackPieces
        eatingPieces = state.whitePieces

    toRemove = canEat(state, eatingPieces, toEatPieces)
    for pieceToRemove in toRemove:
        toEatPieces.remove(pieceToRemove)
    return toEatPieces

# Function that determines if a cell is within range of the board.
def inBoardRange(coord):
    x,y = coord
    return x>-1 and x<8 and y >-1 and y <8

# Functions that return coord of cells up down left right,
# does not check for board range.
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

# Functions that return coord of cells that are two up, down,
# left, right. Does not check for board range.
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

# Function that returns coord of adjacent cells, checks for board
# range.
def adjacentCells(x,y):
    adjacentCells = [up(x,y), down(x,y), left(x,y), right(x,y)]
    for cell in adjacentCells:
        if not inBoardRange(cell):
            adjacentCells.remove(cell)
    return adjacentCells

# Function that returns coord of adjacent cells,
# two cells away, checks for board range.
def twoAdjacentCells(x,y):
    adjacentAdjacentCells = [twoUp(x,y), twoDown(x,y), twoLeft(x,y), twoRight(x,y)]
    for cell in adjacentCells:
        if not inBoardRange(cell):
            adjacentCells.remove(cell)
    return adjacentAdjacentCells
