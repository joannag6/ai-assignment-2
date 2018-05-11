import random
from moves import *

PLACEMENT_LINE = 2
STARTING_PIECES = 12
LOOKAHEAD_MOVE = 3
MOVEMENT_ONE = 128
MOVEMENT_TWO = 192
QUAD_ONE = [(x, y) for x in range(INITIAL_BOARD_SIZE//2)
                   for y in range(INITIAL_BOARD_SIZE//2)]
QUAD_TWO = [(x, y) for x in range(INITIAL_BOARD_SIZE//2, INITIAL_BOARD_SIZE)
                   for y in range(INITIAL_BOARD_SIZE//2)]
QUAD_THREE = [(x, y) for x in range(INITIAL_BOARD_SIZE//2)
                     for y in range(INITIAL_BOARD_SIZE//2, INITIAL_BOARD_SIZE)]
QUAD_FOUR = [(x, y) for x in range(INITIAL_BOARD_SIZE//2, INITIAL_BOARD_SIZE)
                    for y in range(INITIAL_BOARD_SIZE//2, INITIAL_BOARD_SIZE)]
CORNERS = [(0,0),(7,0),(0,7),(7,7)]

class Player:
    def __init__(self, colour):
        self.colour = colour
        self.isWhite = True if self.colour == "white" else False
        self.state = GameState(INITIAL_BOARD_SIZE, set(), set(), self.isWhite, self.isWhite)
        self.placingPhase = True
        self.turns = 0

    def action(self, turns):
        """turns: int, total turns for that phase"""

        # Referee will pass the number of turns that have happened.
        self.turns = turns

        # if even number of turns have passed, it is white's turn to play
        if turns % 2 == 0:
            self.state.isWhiteTurn = True
        else:
            self.state.isWhiteTurn = False

        nextMove = None # if passing turn

        if self.placingPhase:
            nextMove = heurPlacement(self)
        else:
            nextMove = minimaxMovement(self.state, LOOKAHEAD_MOVE, turns)
        # Increments the number of turns that have happened, since an action took place.
        self.turns += 1

        self.selfUpdate(nextMove)

        # return (x, y) for placing piece
        # return ((oldx, oldy), (newx, newy)) for moving piece

        return nextMove

    def updateMovement(self, move): # PROBLEM IS HERE>
        if self.state.isWhiteTurn:
            self.state.whitePieces.remove(move[0])
            self.state.whitePieces.add(move[1])
        else:
            self.state.blackPieces.remove(move[0])
            self.state.blackPieces.add(move[1])

    def updatePlacement(self, place):
        if self.state.isWhiteTurn:
            self.state.whitePieces.add(place)
        else:
            self.state.blackPieces.add(place)

    # Function that is called only by player, to update it's own state
    # after a move has been made.
    def selfUpdate(self, action):
        """Update internal game state according to own action"""
        if action == None: return

        if self.placingPhase:
            # update placement
            self.updatePlacement(action)
        else:
            # update movement
            self.updateMovement(action)

        if not self.placingPhase:
            # Code that implements shrinking.
            if self.turns == MOVEMENT_ONE: # end of first moving stage (going to 6x6)

                self.state.shrink(1)

            if self.turns == MOVEMENT_TWO: # end of second moving stage (going to 4x4)
                self.state.shrink(2)

        removeEatenPieces(self.state, not self.state.isWhiteTurn)
        removeEatenPieces(self.state, self.state.isWhiteTurn)

        if self.placingPhase and self.turns >= STARTING_PIECES*2:
            self.placingPhase = False


    def update(self, action):
        self.turns += 1
        """Update internal game state according to opponent's action"""

        if action == None:
            return

        # Different equalities from action, this is intentional.
        if self.turns % 2 != 0:
            self.state.isWhiteTurn = True
        else:
            self.state.isWhiteTurn = False

        if self.placingPhase:
            # update placement
            self.updatePlacement(action)
        else:
            # update movement
            self.updateMovement(action)

        if not self.placingPhase:
            # Code that implements shrinking.
            if self.turns == MOVEMENT_ONE: # end of first moving stage (going to 6x6)
                self.state.shrink(1)
            if self.turns == MOVEMENT_TWO: # end of second moving stage (going to 4x4)
                self.state.shrink(2)

        removeEatenPieces(self.state, not self.state.isWhiteTurn)
        removeEatenPieces(self.state, self.state.isWhiteTurn)

        # When black makes 24th move, white's self.turns == 24 after the increment in update().
        # Then, after the code for update reaches this point, we have to toggle white's placingPhase
        # to False.
        if self.placingPhase and self.turns >= STARTING_PIECES*2:
            self.placingPhase = False

def getMoves(state):
    moveList = set()
    if state.isWhiteTurn:
        for piece in state.whitePieces:
            moveList |= state.calcMovesForCoord(piece, state.blackPieces)
    else:
        for piece in state.blackPieces:
            moveList |= state.calcMovesForCoord(piece, state.whitePieces)
    return moveList # set of possible moves for that player


# dummy utility function for terminal states
# for now = ownPieces - oppPieces
def getEvaluationValue(state):
    if state.isWhitePlayer:
        return len(state.whitePieces) - len(state.blackPieces)
    return len(state.blackPieces) - len(state.whitePieces)


# different for placing and moving stage??
# returns integer value representing utility value
def getMoveValue(move, ownTurn, state, turnsLeft, turns, alpha, beta):

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

    if turns == MOVEMENT_ONE - 1: # end of first moving stage (going to 6x6)
        newState.shrink(1)
    if turns == MOVEMENT_TWO - 1: # end of second moving stage (going to 4x4)
        newState.shrink(2)

    # run check if anything eaten, priority determined by turn
    removeEatenPieces(newState, not newState.isWhiteTurn)
    removeEatenPieces(newState, newState.isWhiteTurn)

    if turnsLeft == 0 or newState.isEndState():
        return getEvaluationValue(newState)


    # choices = []
    possibleMoves = getMoves(newState)
    for nextMove in possibleMoves:
        # if ownTurn: alpha = None
        # else: beta = None

        nextVal = getMoveValue(nextMove, not ownTurn, newState, turnsLeft-1, turns+1, alpha, beta)

        # newState.printBoard()
        # print(nextMove)
        # print("alpha: " + str(alpha))
        # print("beta: " + str(beta))
        # print("this val: " + str(nextVal))

        if alpha != None and beta != None and beta <= alpha:
           return nextVal

        if ownTurn:
            if alpha == None or nextVal >= alpha:
                alpha = nextVal
                # choices.append(nextVal)
                # elif nextVal >= alpha:
                # print("CUT")
                # return nextVal
                # else:
                # choices.append(nextVal)
        if not ownTurn:
            if beta == None or nextVal <= beta:
                beta = nextVal
                # choices.append(nextVal)
                # elif nextVal <= beta:
                # print("CUT")
                # return nextVal
                # else:
                # choices.append(nextVal)

    if not possibleMoves:
        return getEvaluationValue(newState) # TODO or None?


    if ownTurn:
        return alpha#max(choices)
    return beta#min(choices)


def minimaxMovement(state, turnsLeft, turns):
    choices = []
    if turns == MOVEMENT_ONE - 1: # end of first moving stage (going to 6x6)
        state.shrink(1)
    if turns == MOVEMENT_TWO - 1: # end of second moving stage (going to 4x4)
        state.shrink(2)

    for move in getMoves(state):
        choices.append((getMoveValue(move, False, state, turnsLeft-1, turns+1, None, None), move))

    if choices == []:
        return None
    return getRandMax(choices)[1]


def getRandMin(tupList):
    smallestVal = min(tupList)[0]
    return random.choice([tup for tup in tupList if tup[0] == smallestVal])

def getRandMax(tupList):
    smallestVal = max(tupList)[0]
    return random.choice([tup for tup in tupList if tup[0] == smallestVal])

# only used in placing phase.
def getPlaces(state):
    # If it is white's turn, it means we can only put in white's starting zone.
    # Create a set of all the coordinates minus the bottom two rows, then exclude
    # the ones already with pieces and corners.
    if state.isWhiteTurn:
        yRange = range(INITIAL_BOARD_SIZE-STARTING_LINE)
    else:
        yRange = range(STARTING_LINE,INITIAL_BOARD_SIZE)

    placeList = []
    for x in range(INITIAL_BOARD_SIZE):
        for y in yRange:
            coord = (x,y)
            if (coord not in state.whitePieces and coord not in state.blackPieces
                    and not state.isCorner(coord[0], coord[1])):
                placeList.append(coord)
    return placeList

def weakestQuadrant(state):
    quadOneCount = 0
    quadTwoCount = 0
    quadThreeCount = 0
    quadFourCount = 0
    allyPieces = state.allyPieces()
    for piece in allyPieces:
        if piece in QUAD_ONE:
            quadOneCount+=1
        if piece in QUAD_TWO:
            quadTwoCount+=1
        if piece in QUAD_THREE:
            quadThreeCount+=1
        if piece in QUAD_FOUR:
            quadFourCount+=1
    weakestCount = min(quadOneCount,quadTwoCount,quadThreeCount,quadFourCount)
    if quadOneCount is weakestCount:
        return QUAD_ONE
    if quadTwoCount is weakestCount:
        return QUAD_TWO
    if quadThreeCount is weakestCount:
        return QUAD_THREE
    if quadFourCount is weakestCount:
        return QUAD_FOUR


# Function that is meant to make good placements.
def heurPlacement(player):
    if player.isWhite and player.turns is 0:
        return (3,4)
    state = player.state

    availableCells = getPlaces(state)
    weakestQuad = weakestQuadrant(state)

    # First, we prioritize kills.
    killList = []
    # Construct a list of cells that can result in kills.
    for cell in availableCells:
        if killValue(state,cell)>0:
            killList.append((killValue,cell))
    # From cells that result in kills, we choose a random cell with max kills.
    if len(killList)>0:
        # Prune the current killList so it only contains entries with max killValue.
        killList2 = []
        maxKillValue, cell = max(killList)
        for entry in killList:
            if entry[0] == maxKillValue:
                killList2.append(entry)
        returnEntry = random.choice(killList2)
        # Prune the current killList so it only contains entries in weakest quadrant.
        killList3 = []
        for entry in killList2:
            if entry[1] in weakestQuad:
                killList3.append(entry[1])
        # If not possible to control maxControl number of cells by placing in weakest quadrant,
        # then we disregard quadrant analysis and place it on random cell that returns most control.
        if len(killList3) == 0:
            returnEntry =  random.choice(killList2)
            return returnEntry[1]
        else:
            return random.choice(killList3)

    # if we reach here, no kills possible.
    # If we can't kill, we just play for control.
    controlList = []
    nonAllowedList = enemyControlledCells(player.state)

    # Set of coords we can place pieces that will result in them instantly dying.
    instantDeathCoords = instantDeathPlacement(state, availableCells)
    for cell in instantDeathCoords:
        if cell not in nonAllowedList:
            nonAllowedList.append(cell)

    # Construct a list for control evaluation.
    for cell in availableCells:
        controlList.append((controlValue(state,cell), cell))
    maxControlScore,maxControlCoord = max(controlList)

    # Construct a list that only holds coords with best control score at this point.
    controlList2 = []
    for entry in controlList:
        if entry[0] is maxControlScore and entry[0] not in nonAllowedList:
            controlList2.append(entry)

    # Prune controlList further to only include coords in weakest quadrant.
    controlList3 = []
    for entry in controlList2:
        if entry[1] in weakestQuad and entry[1] not in nonAllowedList:
            controlList3.append(entry[1])
    # If not possible to control maxControl number of cells by placing in weakest quadrant,
    # then we disregard quadrant analysis and place it on random cell that returns most control.
    if len(controlList3) == 0:
        returnEntry =  random.choice(controlList2)
        return returnEntry[1]
    else:
        return random.choice(controlList3)

# Function that takes a state and returns list of cells that, if we place a piece, allows opponent to instantly kill that piece.
def enemyControlledCells(state):
    enemyPieces = state.enemyPieces()
    allyPieces = state.allyPieces()
    nonAllowedList = []
    for coord in enemyPieces:
        coordPairsToCheck = ((up(coord), twoUp(coord)),(down(coord), twoDown(coord)),(left(coord),twoLeft(coord)),(right(coord), twoRight(coord)))
        for coord1,coord2 in coordPairsToCheck:
            if inBoardRange(coord1) and inBoardRange(coord2) and state.isEmpty_(coord1[0], coord1[1]) and state.isEmpty_(coord2[0], coord2[0]):
                nonAllowedList.append(coord1)
    return nonAllowedList

# Function that takes a state and list of already non allowed cells, and returns cells that will instantly get us killed, without opponent doing anything
# if we place a piece there.
def instantDeathPlacement(state, placeList):
    enemyPieces = state.enemyPieces()
    toRemove = set()
    for cell in placeList:
        coordPairsToCheck = ((up(cell), down(cell)), (left(cell), right(cell)))
        for coord1, coord2 in coordPairsToCheck:
            if inBoardRange(coord1) and inBoardRange(coord2) and (coord1 in enemyPieces) and (coord2 in enemyPieces):
                toRemove.add(cell)
    return toRemove


def controlValue(state, coord):
    """
    We control an adjacent cell if the next one in that direction is not enemy
    cell, or not out of bounds. That first adjacent cell has to be empty.
    This function calculates the number of cells that we can GAIN in control if
    we place a piece there.
    """
    enemyPieces = state.enemyPieces()
    allyPieces = state.allyPieces()
    controlScore = 0
    coordPairsToCheck = ((up(coord), twoUp(coord)),(down(coord), twoDown(coord)),(left(coord),twoLeft(coord)),(right(coord), twoRight(coord)))
    for coord1,coord2 in coordPairsToCheck:
        if inBoardRange(coord1) and inBoardRange(coord2) and state.isEmpty_(coord1[0], coord1[1]) and not state.isEnemy(enemyPieces,coord2):
            controlScore += 1
    return controlScore


def killValue(state, coord):
    """Returns number of kills that can result from placing a piece on a particular cell."""
    enemyPieces = state.enemyPieces()
    allyPieces = state.allyPieces()
    killValue = 0
    # if adjacent coords contain enemy and one more cell in that
    # direction contains ally piece, we can eliminate that enemy.
    coordPairsToCheck = ((up(coord), twoUp(coord)),(down(coord), twoDown(coord)),(left(coord),twoLeft(coord)),(right(coord), twoRight(coord)))
    for coord1,coord2 in coordPairsToCheck:
        if inBoardRange(coord1) and inBoardRange(coord2) and state.isEnemy(enemyPieces, coord1) and state.isAlly(allyPieces, coord2):
            killValue+=1
    return killValue
