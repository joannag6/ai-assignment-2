from moves import *

INITIAL_BOARD_SIZE = 8
STARTING_PIECES = 12


class Player:
    def __init__(self, colour):
        self.colour = colour
        isWhite = True if self.colour == "white" else isWhite = False
        self.state = GameState(INITIAL_BOARD_SIZE, {}, {}, isWhite, isWhite)
        self.movementService = Movement(self.state)
        self.turns = 0

    def action(self, turns):
        """turns: int, total turns"""
        # check if turns is odd (black's turn)
        # check if turns > STARTING_PIECES * 2, (placing or moving stage)
        nextMove = None

        if turns <= STARTING_PIECES * 2:
            nextMove = minimaxPlacement(self.state)
        else:
            nextMove = minimaxMovement(self.movementService)

        self.update(nextMove)

        # return (x, y) for placing piece
        # return ((oldx, oldy), (newx, newy)) for moving piece
        return nextMove # if passing turn

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
    def isEndState(self):
        return (not bool(self.whitePieces)) or (not bool(self.blackPieces))


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
def getTerminalStateValue(state):
    if state.isWhitePlayer:
        return len(state.whitePieces) - len(state.blackPieces)
    return len(state.blackPieces) - len(state.whitePieces)


# different for placing and moving stage??
# returns integer value representing utility value
def getMoveValue(move, ownTurn, movementService):
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

    if newState.isEndState():
        return getTerminalStateValue(newState)

    movementService.updateState(newState)

    choices = []
    for move in getMoves(movementService):
        choices.append((getMoveValue(move, state, not ownTurn, movementService)))

    if ownTurn:
        return max(choices)
    return min(choices)


def minimaxMovement(movementService):
    choices = []
    for move in getMoves(movementService):
        choices.append((getMoveValue(move, False, movementService), move))
    return max(choices)[1]


# returns integer value representing utility value
def getPlaceValue(place, ownTurn, state):
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

    if newState.isEndState():
        return getTerminalStateValue(newState)

    choices = []
    for place in getPlaces(newState):
        choices.append((getPlaceValue(place, not ownTurn, state)))

    if ownTurn:
        return max(choices)
    return min(choices)


def minimaxPlacement(state):
    choices = []
    for place in getPlaces(state):
        choices.append((getPlaceValue(place, False, state), place))
    return max(choices)[1]


def main():
    movementService = Movement(GameState(INITIAL_BOARD_SIZE, {}, {}, True, True))

if __name__ == "__main__":
    main()
