# Some functions from Part A, modified to fit Part B's requirements

class Movement:
    """Class for all movement functionality required for any piece."""
    def __init__(self, state):
        """Stores the current state of the game at setup. This lets the class
        know where all the pieces are at the current point in time.
        """
        self.state = state

    def updateState(self, newState):
        """Updates the current game state so calculations are up to date."""
        self.state = newState

    def calcMovesForCoord(self, coord):
        """Returns a list of all coordinates reachable from given coord."""
        i, j = coord
        moveList = []
        for move in [self.canGoRight_(i, j),
                     self.canGoLeft_(i, j),
                     self.canGoUp_(i, j),
                     self.canGoDown_(i, j)]:
            if move:
                moveList.append((coord, move))
        return moveList

    def isEmpty_(self, i, j):
        """Checks if there are any pieces in the cell specified by (i, j)."""
        return ((i, j) not in self.state.blackPieces
                and (i, j) not in self.state.whitePieces
                and not corner(i, j, self.state.size))

    def canJumpRight_(self, i, j):
        """Checks if piece can jump right"""
        if withinBounds(i+2, j, self.state.size) and self.isEmpty_(i+2, j):
            return (i+2, j)

    def canJumpLeft_(self, i, j):
        """Checks if piece can jump left"""
        if withinBounds(i-2, j, self.state.size) and self.isEmpty_(i-2, j):
            return (i-2, j)

    def canJumpUp_(self, i, j):
        """Checks if piece can jump up"""
        if withinBounds(i, j-2, self.state.size) and self.isEmpty_(i, j-2):
            return (i, j-2)

    def canJumpDown_(self, i, j):
        """Checks if piece can jump down"""
        if withinBounds(i, j+2, self.state.size) and self.isEmpty_(i, j+2):
            return (i, j+2)

    def canGoRight_(self, i, j):
        """Checks if piece can move right"""
        if withinBounds(i+1, j, self.state.size) and self.isEmpty_(i+1, j):
            return (i+1, j)
        return self.canJumpRight_(i, j)

    def canGoLeft_(self, i, j):
        """Checks if piece can move left"""
        if withinBounds(i-1, j, self.state.size) and self.isEmpty_(i-1, j):
            return (i-1, j)
        return self.canJumpLeft_(i, j)

    def canGoUp_(self, i, j):
        """Checks if piece can move up"""
        if withinBounds(i, j-1, self.state.size) and self.isEmpty_(i, j-1):
            return (i, j-1)
        return self.canJumpUp_(i, j)

    def canGoDown_(self, i, j):
        """Checks if piece can move down"""
        if withinBounds(i, j+1, self.state.size) and self.isEmpty_(i, j+1):
            return (i, j+1)
        return self.canJumpDown_(i, j)


def corner(i, j, boardSize):
    """Checks if coordinates given is a corner of the board."""
    corner_coords = {0, boardSize - 1}
    return i in corner_coords and j in corner_coords


def withinBounds(i, j, boardSize):
    """Checks if coordinates given is on the board."""
    return (0 <= i < boardSize) and (0 <= j < boardSize)


def isEnemy(enemyPieces, coordinate, boardSize):
    """Checks if coordinates belong to the enemy (or is a corner)."""
    i, j = coordinate
    return withinBounds(i, j, boardSize) and (coordinate in enemyPieces or corner(i, j, boardSize))


def canEat(enemyPieces, side1, side2, boardSize):
    """Checks a piece between side1 and side2 will be eaten."""
    return isEnemy(enemyPieces, side1, boardSize) and isEnemy(enemyPieces, side2, boardSize)


def removeEatenPieces(state, eatWhite):
    """Given both sets of coordinates, remove own eaten pieces."""
    if eatWhite: # priority to eating blackPieces
        toEatPieces = state.whitePieces
        eatingPieces = state.blackPieces
    else:
        toEatPieces = state.blackPieces
        eatingPieces = state.whitePieces

    toRemove = []
    for piece in toEatPieces:
        i,j = piece
        down = (i,j+1)
        up = (i,j-1)
        left = (i-1,j)
        right = (i+1,j)

        # check if piece can be eaten from up and down / left and right
        # by checking if within bounds and if they are corner or white.
        if canEat(eatingPieces, up, down, state.size) or canEat(eatingPieces, left, right, state.size):
            toRemove.append(piece)
    for pieceToRemove in toRemove:
        toEatPieces.remove(pieceToRemove)
    return toEatPieces
