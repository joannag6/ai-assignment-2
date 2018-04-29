from moves import *

INITIAL_BOARD_SIZE = 8
STARTING_PIECES = 12
LOOKAHEAD = 3
MOVEMENT_ONE = 128 + STARTING_PIECES * 2
MOVEMENT_TWO = 64 + MOVEMENT_ONE + STARTING_PIECES * 2


class Player:
    def __init__(self, colour):
        self.colour = colour
        isWhite = True if self.colour == "white" else isWhite = False
        self.state = GameState(INITIAL_BOARD_SIZE, {}, {}, isWhite, isWhite)
        self.movementService = Movement(self.state)
        self.turns = 0

    def shrink(self): #TODO: handle corners
        pass

    def action(self, turns):
        """turns: int, total turns"""
        # check if turns is odd (black's turn)
        # check if turns > STARTING_PIECES * 2, (placing or moving stage)
        nextMove = None # if passing turn

        if (self.turns + 1) <= STARTING_PIECES * 2:
            nextMove = minimaxPlacement(self.state, min(LOOKAHEAD, STARTING_PIECES*2 - (self.turns+1)))
        else:
            if (MOVEMENT_ONE - (self.turns+1) <= 0):
                turnsLeft = MOVEMENT_TWO - (self.turns+1)
            else:
                turnsLeft = MOVEMENT_ONE - (self.turns+1)
            nextMove = minimaxMovement(self.movementService, min(LOOKAHEAD, turnsLeft))

        self.update(nextMove)

        # return (x, y) for placing piece
        # return ((oldx, oldy), (newx, newy)) for moving piece
        return nextMove

    def updatePlacement(self, place):
        if self.state.isWhiteTurn:
            self.state.whitePieces.add(place)
        else:
            self.state.blackPieces.add(place)

    def updateMovement(self, move):
        if self.state.isWhiteTurn:
            self.state.whitePieces.remove(move[0])
            self.state.whitePieces.add(move[1])
        else:
            self.state.blackPieces.remove(move[0])
            self.state.blackPieces.add(move[1])

    def update(self, action):
        """Update internal game state according to opponent's action"""
        self.turns += 1

        # check if turns is odd (black's turn)
        if self.turns % 2 == 0:
            self.state.isWhiteTurn = True
        else:
            self.state.isWhiteTurn = False

        if turns <= STARTING_PIECES * 2:
            # update placement
            updatePlacement(action)
        else:
            # update movement
            updateMovement(action)

        removeEatenPieces(self.state, not self.state.isWhiteTurn)
        removeEatenPieces(self.state, self.state.isWhiteTurn)


class GameState:
    """
    Class which stores the state of the game at a given time. This includes
    the locations of all the white pieces and all the black pieces on the board.
    It also keeps track of phase, whose turn it is, and current size of board.b
    """

    def __init__(self, boardSize, whitePieces, blackPieces, isWhitePlayer, isWhiteTurn):
        self.size = boardSize
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
        for i,j in state.whitePieces:
            board[i][j] = 'O'
        for i,j in state.blackPieces:
            board[i][j] = '@'
        for row in board:
            print(row)


def getMoves(movementService):
    moveList = []
    if movementService.state.isWhiteTurn:
        for piece in movementService.state.whitePieces:
            moveList += movementService.calcMovesForCoord(piece)
    else:
        for piece in movementService.state.blackPieces:
            moveList += movementService.calcMovesForCoord(piece)
    return moveList # list of possible moves for that player


def getPlaces(state):
    placeList = []
    for coord in [(x, y) for x in range(state.size) and y in range(state.size)]:
        if coord not in state.whitePieces and coord not in state.blackPieces:
            placeList.append(coord)
    return placeList


# dummy utility function for terminal states
# for now = ownPieces - oppPieces
def getEvaluationValue(state):
    if state.isWhitePlayer:
        return len(state.whitePieces) - len(state.blackPieces)
    return len(state.blackPieces) - len(state.whitePieces)


# different for placing and moving stage??
# returns integer value representing utility value
def getMoveValue(move, ownTurn, movementService, turnsLeft):
    # just implement for moving stage first

    state = movementService.state

    # if ownTurn is True, get max.
    newWhitePieces = state.whitePieces.copy()
    newBlackPieces = state.blackPieces.copy()

    if state.isWhiteTurn:
        newWhitePieces.remove(move[0])
        newWhitePieces.add(move[1])
    else:
        newBlackPieces.remove(move[0])
        newBlackPieces.add(move[1])

    newState = GameState(state.size,
                         newWhitePieces,
                         newBlackPieces,
                         state.isWhitePlayer,
                         not state.isWhiteTurn)

    # run check if anything eaten, priority determined by turn
    removeEatenPieces(newState, not newState.isWhiteTurn)
    removeEatenPieces(newState, newState.isWhiteTurn)

    if turnsLeft == 0 or newState.isEndState:  #TODO: OR is end state
        return getEvaluationValue(newState)
    #if newState.isEndState():
    #    return getTerminalStateValue(newState)

    movementService.updateState(newState)

    choices = []
    for move in getMoves(movementService):
        choices.append((getMoveValue(move, state, not ownTurn, movementService, turnsLeft-1)))

    if ownTurn:
        return max(choices)
    return min(choices)


def minimaxMovement(movementService, turnsLeft):
    choices = []
    for move in getMoves(movementService):
        choices.append((getMoveValue(move, False, movementService), move, turnsLeft-1))
    return max(choices)[1]


# returns integer value representing utility value
def getPlaceValue(place, ownTurn, state, turnsLeft):
    # just implement for moving stage first

    state = movementService.state

    # if ownTurn is True, get max.
    newWhitePieces = state.whitePieces.copy()
    newBlackPieces = state.blackPieces.copy()

    if state.isWhiteTurn:
        newWhitePieces.add(place)
    else:
        newBlackPieces.add(place)

    newState = GameState(state.size,
                         newWhitePieces,
                         newBlackPieces,
                         state.isWhitePlayer,
                         not state.isWhiteTurn)

    # run check if anything eaten, priority determined by turn
    removeEatenPieces(newState, not newState.isWhiteTurn)
    removeEatenPieces(newState, newState.isWhiteTurn)

    if turnsLeft == 0 or newState.isEndState():
        return getEvaluationValue(newState)

    choices = []
    for place in getPlaces(newState):
        choices.append((getPlaceValue(place, not ownTurn, state, turnsLeft-1)))

    if ownTurn:
        return max(choices)
    return min(choices)


def minimaxPlacement(state, turnsLeft):
    choices = []
    for place in getPlaces(state):
        choices.append((getPlaceValue(place, False, state), place, turnsLeft-1))
    return max(choices)[1]


def main():
    movementService = Movement(GameState(INITIAL_BOARD_SIZE, {}, {}, True, True))

if __name__ == "__main__":
    main()
