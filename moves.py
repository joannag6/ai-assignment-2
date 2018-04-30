# Some functions from Part A, modified to fit Part B's requirements

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

    def updateSize(self, newSize):
        self.size = newSize
        # call kill pieces that are outside borders

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
        board = [[ '-' for y in range(self.size) ] for x in range(self.size)]
        for i,j in self.whitePieces:
            board[i][j] = 'O'
        for i,j in self.blackPieces:
            board[i][j] = '@'
        for row in board:
            print(row)

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
        return ((i, j) not in self.blackPieces
                and (i, j) not in self.whitePieces
                and not corner(i, j, self))

    def canJumpRight_(self, i, j):
        """Checks if piece can jump right"""
        if withinBounds(i+2, j, self) and self.isEmpty_(i+2, j):
            return (i+2, j)

    def canJumpLeft_(self, i, j):
        """Checks if piece can jump left"""
        if withinBounds(i-2, j, self) and self.isEmpty_(i-2, j):
            return (i-2, j)

    def canJumpUp_(self, i, j):
        """Checks if piece can jump up"""
        if withinBounds(i, j-2, self) and self.isEmpty_(i, j-2):
            return (i, j-2)

    def canJumpDown_(self, i, j):
        """Checks if piece can jump down"""
        if withinBounds(i, j+2, self) and self.isEmpty_(i, j+2):
            return (i, j+2)

    def canGoRight_(self, i, j):
        """Checks if piece can move right"""
        if withinBounds(i+1, j, self) and self.isEmpty_(i+1, j):
            return (i+1, j)
        return self.canJumpRight_(i, j)

    def canGoLeft_(self, i, j):
        """Checks if piece can move left"""
        if withinBounds(i-1, j, self) and self.isEmpty_(i-1, j):
            return (i-1, j)
        return self.canJumpLeft_(i, j)

    def canGoUp_(self, i, j):
        """Checks if piece can move up"""
        if withinBounds(i, j-1, self) and self.isEmpty_(i, j-1):
            return (i, j-1)
        return self.canJumpUp_(i, j)

    def canGoDown_(self, i, j):
        """Checks if piece can move down"""
        if withinBounds(i, j+1, self) and self.isEmpty_(i, j+1):
            return (i, j+1)
        return self.canJumpDown_(i, j)


def corner(i, j, state):
    """Checks if coordinates given is a corner of the board."""
    corner_coords = {0, state.size - 1}
    return i in corner_coords and j in corner_coords


def withinBounds(i, j, state):
    """Checks if coordinates given is on the board."""
    return (0 <= i < state.size) and (0 <= j < state.size)


def isEnemy(enemyPieces, coordinate, state):
    """Checks if coordinates belong to the enemy (or is a corner)."""
    i, j = coordinate
    return withinBounds(i, j, state) and (coordinate in enemyPieces or corner(i, j, state))


def canEat(enemyPieces, side1, side2, state):
    """Checks a piece between side1 and side2 will be eaten."""
    return isEnemy(enemyPieces, side1, state) and isEnemy(enemyPieces, side2, state)


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
        if canEat(eatingPieces, up, down, state) or canEat(eatingPieces, left, right, state):
            toRemove.append(piece)
    for pieceToRemove in toRemove:
        toEatPieces.remove(pieceToRemove)
    return toEatPieces
