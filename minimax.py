import random
from moves import *

PLACEMENT_LINE = 2
STARTING_PIECES = 12
LOOKAHEAD = 2
LOOKAHEAD_MOVE = 3
MOVEMENT_ONE = 128 + STARTING_PIECES * 2#128 + STARTING_PIECES * 2
MOVEMENT_TWO = 64 + MOVEMENT_ONE + STARTING_PIECES * 2#64 + MOVEMENT_ONE + STARTING_PIECES * 2
QUAD_ONE = [(0,0), (1,0), (2,0), (3,0), (0,1),(1,1),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(0,3),(1,3),(2,3),(3,3)] 
QUAD_TWO = [(4,0),(5,0),(6,0),(7,0),(4,1),(5,1),(6,1),(7,1),(4,2),(5,2),(6,2),(7,2),(4,3),(5,3),(6,3),(7,3)]
QUAD_THREE = [(0,4),(1,4),(2,4),(3,4),(0,5),(1,5),(2,5),(3,5),(0,6),(1,6),(2,6),(3,6),(0,7),(1,7),(2,7),(3,7)]
QUAD_FOUR = [(4,4),(5,4),(6,4),(7,4),(4,5),(5,5),(6,5),(7,5),(4,6),(5,6),(6,6),(7,6),(4,7),(5,7),(6,7),(7,7)]

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
            nextMove = heurPlacement(self.state, min(LOOKAHEAD, STARTING_PIECES*2 - turns + 1))
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

def weakestQuadrant(state):
    return



# Function that is meant to make good placements.
def heurPlacement(state, turnsLeft):
    # TODO: place this better. 
    # if is white turn, then enemy pieces are black.
    # if is black turn, enemy pieces are white. 
    if state.isWhiteTurn:
        enemyPieces = state.blackPieces
        allyPieces = state.whitePieces
    else:
        enemyPieces = state.whitePieces
        allyPieces = state.blackPieces
    
    availableCells = getPlaces(state)
    # Determine weakest quadrant. 

    # First, we prioritize kills. 
    killList = []
    # Construct a list of cells that can result in kills. 
    for cell in availableCells:
        if killValue(state,cell)>0:
            killList.append((killValue,cell))
    # From cells that result in kills, we choose a random cell with max kills. 
    # TODO: Implement quadrant selection, then maybe distance to centre calculation. 
    if len(killList)>0:
        # Prune the current killList so it only contains entries with max killValue. 
        killList2 = []
        maxKillValue, cell = max(killList)
        for entry in killList:
            if entry[0] == maxKillValue:
                killList2.append(entry)
        # Prune the current killList so it only contains entries in weakest quadrant. 
        killList3 = []
        
        returnEntry = random.choice(killList2)
        return returnEntry[1]

    # if we reach here, no kills possible. 
    # If we can't kill, we just play for control. 
    controlList = []
    # Construct a list for control evaluation.
    for cell in availableCells:
        controlList.append((controlValue(state,cell,enemyPieces,allyPieces), cell))
    maxControlScore,maxControlCoord = max(controlList)
    controlList2 = []
    for entry in controlList:
        if entry[0] is maxControlScore:
            controlList2.append(entry)
    a,b = random.choice(controlList2)
    print(a,b)
    return b

# We control an adjacent cell if the next one in that direction is not enemy cell, or not out of bounds
# That first adjacent cell has to be empty. 
# This function calculates the number of cell that we can GAIN in control if we place a piece there. 
def controlValue(state, coord, enemyPieces, allyPieces):
    controlScore = 0
    coordPairsToCheck = ((up(coord), twoUp(coord)),(down(coord), twoDown(coord)),(left(coord),twoLeft(coord)),(right(coord), twoRight(coord)))
    for coord1,coord2 in coordPairsToCheck:
        if inBoardRange(coord1) and inBoardRange(coord2) and state.isEmpty(coord1) and not state.isEnemy(enemyPieces,coord2):
            controlScore += 1
    return controlScore       

# Number of kills that can result from placing a piece on a particular cell. 
def killValue(state, coord):
    # TODO: place this better. 
    # if is white turn, then enemy pieces are black.
    # if is black turn, enemy pieces are white. 
    if state.isWhiteTurn:
        enemyPieces = state.blackPieces
        allyPieces = state.whitePieces
    else:
        enemyPieces = state.whitePieces
        allyPieces = state.blackPieces
    killValue = 0
    # if adjacent coords contain enemy and one more cell in that 
    # direction contains ally piece, we can eliminate that enemy.
    coordPairsToCheck = ((up(coord), twoUp(coord)),(down(coord), twoDown(coord)),(left(coord),twoLeft(coord)),(right(coord), twoRight(coord)))
    for coord1,coord2 in coordPairsToCheck:
        if inBoardRange(coord1) and inBoardRange(coord2) and state.isEnemy(enemyPieces, coord1) and state.isAlly(allyPieces, coord2):
            killValue+=1
    return killValue


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
