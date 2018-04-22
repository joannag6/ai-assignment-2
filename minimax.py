from moves import *

INITIAL_BOARD_SIZE = 8

class GameState:
    """
    Class which stores the state of the game at a given time. This includes
    the locations of all the white pieces and all the black pieces on the board.
    It also keeps track of phase, whose turn it is, and current size of board.
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


class Player:
    def __init__(self, colour):
        self.colour = colour

    def action(self, turns):
        """turns: int, total turns"""
        # check if turns is odd (black's turn)
        # check if turns > n, (placing or moving stage)

        # return (x, y) for placing piece
        # return ((oldx, oldy), (newx, newy)) for moving piece
        return None # if passing turn

    def update(self, action):
        """Update internal game state according to opponent's action"""


def getMoves(state, movementService):
    moveList = []
    if state.isWhiteTurn:
        for piece in state.whitePieces:
            moveList += movementService.calcMovesForCoord(piece)
    else:
        for piece in state.blackPieces:
            moveList += movementService.calcMovesForCoord(piece)
    return moveList # list of possible moves for that player

# dummy utility function for terminal states
def getUtilityValue(state):
    if isWhitePlayer:
        return len(state.whitePieces) - len(state.blackPieces)
    return len(state.blackPieces) - len(state.whitePieces)

# different for placing and moving stage??
def minimaxGenerate(move, state, ownTurn, movementService):
    # just implement for moving stage first

    # for now = ownPieces - oppPieces

    # if ownTurn is True, get max.
    newWhitePieces = state.whitePieces.copy()
    newBlackPieces = state.blackPieces.copy()

    if ownTurn:
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
        return getUtilityValue(newState)

    movementService.updateState(newState)

    choices = []
    for move in getMoves(state, movementService):
        choices.append((minimaxGenerate(move, state, not ownTurn, movementService)))

    if ownTurn:
        return max(choices)
    return min(choices)


def minimax(state, movementService):
    choices = []
    for move in getMoves(state, movementService):
        choices.append((minimaxGenerate(move, state, False, movementService), move))
    return max(choices)[1]


def main():
    movementService = Movement(GameState(INITIAL_BOARD_SIZE, {}, {}, True, True))
    print("MINIMAXING")

if __name__ == "__main__":
    main()
