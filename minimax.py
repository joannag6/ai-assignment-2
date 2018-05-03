import random
from moves import *

PLACEMENT_LINE = 2
STARTING_PIECES = 12
LOOKAHEAD = 2
LOOKAHEAD_MOVE = 3
MOVEMENT_ONE = 128 + STARTING_PIECES * 2#128 + STARTING_PIECES * 2
MOVEMENT_TWO = 64 + MOVEMENT_ONE + STARTING_PIECES * 2#64 + MOVEMENT_ONE + STARTING_PIECES * 2


class Player:
    def __init__(self, colour):
        self.colour = colour
        isWhite = True if self.colour == "white" else False
        self.state = GameState(INITIAL_BOARD_SIZE, set(), set(), isWhite, isWhite)
        self.turns = 0

    def action(self, turns):
        """turns: int, total turns"""
        # check if turns is odd (black's turn)
        # check if turns > STARTING_PIECES * 2, (placing or moving stage)
        nextMove = None # if passing turn
        print("####################################################################")

        if turns == MOVEMENT_ONE: # end of first moving stage (going to 6x6)
            self.state.shrink(1)
        if turns == MOVEMENT_TWO: # end of second moving stage (going to 4x4)
            self.state.shrink(2)

        # check if turns is even (black's turn)
        if turns % 2 != 0:
            self.state.isWhiteTurn = True
        else:
            self.state.isWhiteTurn = False

        if turns <= STARTING_PIECES * 2:
            nextMove = minimaxPlacement(self.state, min(LOOKAHEAD, STARTING_PIECES*2 - turns + 1))
        else:
            # if (MOVEMENT_ONE - turns <= 0):
            #     turnsLeft = MOVEMENT_TWO - turns
            # else:
            #     turnsLeft = MOVEMENT_ONE - turns
            nextMove = minimaxMovement(self.state, LOOKAHEAD_MOVE, turns)

        self.update(nextMove)

        self.state.printBoard()

        # return (x, y) for placing piece
        # return ((oldx, oldy), (newx, newy)) for moving piece
        return nextMove

    # TODO: remove. Hackish way to get user input for placing phase, used in placementTest.py
    def userAction(self, turns):
        """turns: int, total turns"""
        # check if turns is odd (black's turn)
        # check if turns > STARTING_PIECES * 2, (placing or moving stage)
        nextMove = None # if passing turn
        print("####################################################################")

        if turns == MOVEMENT_ONE: # end of first moving stage (going to 6x6)
            self.state.shrink(1)
        if turns == MOVEMENT_TWO: # end of second moving stage (going to 4x4)
            self.state.shrink(2)

        # check if turns is even (black's turn)
        if turns % 2 != 0:
            self.state.isWhiteTurn = True
        else:
            self.state.isWhiteTurn = False

        # Collects user input and uses that for nextMove. 
        x = int(input("Enter a first digit of coord: "))
        y = int(input("Enter a second digit of coord: "))
        nextMove = (x,y)
        self.update(nextMove)

        self.state.printBoard()

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

        if self.turns == MOVEMENT_ONE: # end of first moving stage (going to 6x6)
            self.state.shrink(1)
        if self.turns == MOVEMENT_TWO: # end of second moving stage (going to 4x4)
            self.state.shrink(2)

        if action == None: return

        # check if turns is odd (black's turn)
        if self.turns % 2 != 0:
            self.state.isWhiteTurn = True
        else:
            self.state.isWhiteTurn = False

        if self.turns <= STARTING_PIECES * 2:
            # update placement
            self.updatePlacement(action)
        else:
            # update movement
            self.updateMovement(action)

        removeEatenPieces(self.state, not self.state.isWhiteTurn)
        removeEatenPieces(self.state, self.state.isWhiteTurn)

        # TODO: Add check for endstate, and do something


def getMoves(state):
    # print("*")
    # state.printBoard()
    moveList = []
    if state.isWhiteTurn:
        for piece in state.whitePieces:
            moveList += state.calcMovesForCoord(piece)
    else:
        for piece in state.blackPieces:
            moveList += state.calcMovesForCoord(piece)
    # print(moveList)
    # print("*")

    return moveList # list of possible moves for that player


def getPlaces(state):
    placeList = []

    if state.isWhiteTurn:
        start, end = 0, state.size - PLACEMENT_LINE
    else:
        start, end = PLACEMENT_LINE, state.size

    for coord in [(x, y) for y in range(start, end) for x in range(state.size)]:
        if (coord not in state.whitePieces and
                coord not in state.blackPieces and
                not state.corner(coord[0], coord[1])):
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
def getMoveValue(move, ownTurn, state, turnsLeft, turns):
    # just implement for moving stage first

    #state.printBoard()
    #print(move)

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

    # print(turnsLeft)
    # newState.printBoard()

    if turns == MOVEMENT_ONE: # end of first moving stage (going to 6x6)
        newState.shrink(1)
    if turns == MOVEMENT_TWO: # end of second moving stage (going to 4x4)
        newState.shrink(2)

    # run check if anything eaten, priority determined by turn
    removeEatenPieces(newState, not newState.isWhiteTurn)
    removeEatenPieces(newState, newState.isWhiteTurn)

    if turnsLeft == 0 or newState.isEndState():
        return getEvaluationValue(newState)

    choices = []
    for nextMove in getMoves(newState):
        choices.append(getMoveValue(nextMove, not ownTurn, newState, turnsLeft-1, turns+1))

    if choices == []:
        # print("no more choices")
        # print(state.whitePieces)
        # print(state.blackPieces)
        # print(move)
        # print(newState.whitePieces)
        # print(newState.blackPieces)
        if (getMoves(newState) == []):
            # print("no new moves?")
            return getEvaluationValue(newState) # TODO or None?

    if ownTurn:
        return max(choices)
    return min(choices)


def minimaxMovement(state, turnsLeft, turns):
    choices = []
    if turns == MOVEMENT_ONE: # end of first moving stage (going to 6x6)
        state.shrink(1)
    if turns == MOVEMENT_TWO: # end of second moving stage (going to 4x4)
        state.shrink(2)

    for move in getMoves(state):
        choices.append((getMoveValue(move, True, state, turnsLeft-1, turns+1), move))
    # print(choices)

    if choices == []:
        return None

    return getRandMax(choices)[1]


def getRandMin(tupList):
    smallestVal = min(tupList)[0]
    return random.choice([tup for tup in tupList if tup[0] == smallestVal])

def getRandMax(tupList):
    smallestVal = max(tupList)[0]
    return random.choice([tup for tup in tupList if tup[0] == smallestVal])


# returns integer value representing utility value
def getPlaceValue(place, ownTurn, state, turnsLeft):
    # just implement for moving stage first

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

    # newState.printBoard()

    if turnsLeft == 0 or newState.isEndState():
        return getEvaluationValue(newState)

    choices = []
    for place in getPlaces(newState):
        choices.append((getPlaceValue(place, not ownTurn, newState, turnsLeft-1)))

    if ownTurn:
        return max(choices)
    return min(choices)


# Function that just makes valid placements. 
def minimaxPlacement(state, turnsLeft):
    choices = []
    #for place in getPlaces(state):
    #    choices.append((getPlaceValue(place, False, state, turnsLeft-1), place))
    x = getPlaces(state)
    print(x)
    return random.choice(x) #max(choices)[1]

# Function that is meant to make good placements lol. 
def heurPlacement(state, turnsLeft):
    availableCells = getPlaces(state)
    # for every available cell:
        # create list of cells where we can eliminate them
        # killList = []
        # for cell in killList:
            # if killlist empty, break
            # Find the one with the most zone of control
            # If no ties, return that cell
            # if there are ties:
                # get our weakest quadrant
                # put it in cell in weakest quad
                # return that cell.
        # if we reach here, killList is empty. 
        # If we can't kill, we just play for control. 
        # for cell in availableCells:
            # find the cells with the most control. 
            # if there is tie, choose cells in quad of least ctrl
            # If there is still tie, random. 


def main():
    #movementService = Movement(GameState(INITIAL_BOARD_SIZE, set(), set(), True, True))
    whitePlayer = Player("white")
    blackPlayer = Player("black")


    for turns in range(1, MOVEMENT_TWO+2, 2):
        nextMove = whitePlayer.action(turns)
        print("white: " + str(nextMove))
        blackPlayer.update(nextMove)
        print("####################################################################")


        if turns > STARTING_PIECES * 2 and whitePlayer.state.isEndState():
            if len(whitePlayer.state.whitePieces) > len(whitePlayer.state.blackPieces):
                print("White player wins!")
                break
            if len(whitePlayer.state.whitePieces) < len(whitePlayer.state.blackPieces):
                print("Black player wins!")
                break
            else:
                print("It's a draw!!")
                break

        nextMove = blackPlayer.action(turns+1)
        print("black: " + str(nextMove))
        whitePlayer.update(nextMove)
        print("####################################################################")

        if turns > STARTING_PIECES * 2 and blackPlayer.state.isEndState():
            if len(whitePlayer.state.whitePieces) > len(whitePlayer.state.blackPieces):
                print("White player wins!")
                break
            if len(whitePlayer.state.whitePieces) < len(whitePlayer.state.blackPieces):
                print("Black player wins!")
                break
            else:
                print("It's a draw!!")
                break


if __name__ == "__main__":
    main()
