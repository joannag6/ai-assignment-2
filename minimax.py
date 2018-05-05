import random
from moves import *

PLACEMENT_LINE = 2
STARTING_PIECES = 12
LOOKAHEAD = 1
LOOKAHEAD_MOVE = 2
MOVEMENT_ONE = 128 + STARTING_PIECES * 2#128 + STARTING_PIECES * 2
MOVEMENT_TWO = 64 + MOVEMENT_ONE + STARTING_PIECES * 2#64 + MOVEMENT_ONE + STARTING_PIECES * 2
QUAD_ONE = [(0,0), (1,0), (2,0), (3,0), (0,1),(1,1),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(0,3),(1,3),(2,3),(3,3)] 
QUAD_TWO = [(4,0),(5,0),(6,0),(7,0),(4,1),(5,1),(6,1),(7,1),(4,2),(5,2),(6,2),(7,2),(4,3),(5,3),(6,3),(7,3)]
QUAD_THREE = [(0,4),(1,4),(2,4),(3,4),(0,5),(1,5),(2,5),(3,5),(0,6),(1,6),(2,6),(3,6),(0,7),(1,7),(2,7),(3,7)]
QUAD_FOUR = [(4,4),(5,4),(6,4),(7,4),(4,5),(5,5),(6,5),(7,5),(4,6),(5,6),(6,6),(7,6),(4,7),(5,7),(6,7),(7,7)]
CORNERS = [(0,0),(7,0),(0,7),(7,7)]

class Player:
    def __init__(self, colour):
        self.colour = colour
        self.isWhite = True if self.colour == "white" else False
        self.state = GameState(INITIAL_BOARD_SIZE, set(), set(), self.isWhite, self.isWhite)
        self.turns = 0 
        self.placementPhase = True

    def action(self, turns):
        if self.isWhite:
            print("calling action on whitePlayer on turn")
        else:
            print("calling action on blackPlayer on turn")
        self.turns = turns
        print(turns)

        # if even number of turns have passed, it is white's turn to play
        if turns % 2 == 0:
            self.state.isWhiteTurn = True
        else:
            self.state.isWhiteTurn = False   
        if self.state.isWhiteTurn:
            print("WHITE TURN")
        if not self.state.isWhiteTurn:
            print("BLACK TURN") 

        """turns: int, total turns"""
        # check if turns is odd (black's turn)
        # check if turns > STARTING_PIECES * 2, (placing or moving stage)
        nextMove = None # if passing turn
        #print("####################################################################")
        #self.turns += 1
        
        # Code that implements shrinking. 
        if turns == MOVEMENT_ONE: # end of first moving stage (going to 6x6)
            self.state.shrink(1)
        if turns == MOVEMENT_TWO: # end of second moving stage (going to 4x4)
            self.state.shrink(2)


        # the first STARTING_PIECES*2 turns are definitely placement turns. 
        if self.placementPhase:
            nextMove = heurPlacement(self.state)
        else:
            # if (MOVEMENT_ONE - turns <= 0):
            #     turnsLeft = MOVEMENT_TWO - turns
            # else:
            #     turnsLeft = MOVEMENT_ONE - turns
            nextMove = minimaxMovement(self.state, LOOKAHEAD_MOVE, turns)

        self.selfUpdate(nextMove)

        # return (x, y) for placing piece
        # return ((oldx, oldy), (newx, newy)) for moving piece
        if turns == 23:
            self.placementPhase = False
      
        return nextMove

    def updatePlacement(self, place):
        if self.state.isWhiteTurn:
            self.state.whitePieces.add(place)
        else:
            self.state.blackPieces.add(place)

    def updateMovement(self, move): # PROBLEM IS HERE> 
        if self.state.isWhiteTurn:
            self.state.whitePieces.remove(move[0])
            self.state.whitePieces.add(move[1])
        else:
            self.state.blackPieces.remove(move[0])
            self.state.blackPieces.add(move[1])

    # Function that is called only by player, to update it's own state
    # after a move has been made. 
    def selfUpdate(self, action):
        """Update internal game state according to own action"""
        if action == None: return

        if self.placementPhase:
            # update placement
            self.updatePlacement(action)
        else:
            # update movement
            self.updateMovement(action)

        removeEatenPieces(self.state, not self.state.isWhiteTurn)
        removeEatenPieces(self.state, self.state.isWhiteTurn)
        

    def update(self, action):
        # Hacky way to get turns to be right, from the way it is called in referee.py
        self.turns += 1
        if self.turns > 1: 
            self.turns += 1

        if self.isWhite:
            print("calling update on whitePlayer on turn")
        else:
            print("calling update on blackPlayer on turn")
        print(self.turns)
        """Update internal game state according to opponent's action"""

        if self.turns == MOVEMENT_ONE: # end of first moving stage (going to 6x6)
            self.state.shrink(1)
        if self.turns == MOVEMENT_TWO: # end of second moving stage (going to 4x4)
            self.state.shrink(2)

        if action == None: 
            if not self.isWhite:
                self.turns += 1
            return

        if self.turns % 2 == 0:
            self.state.isWhiteTurn = True
        else:
            self.state.isWhiteTurn = False

        if self.placementPhase:
            # update placement
            self.updatePlacement(action)
        else:
            # update movement
            self.updateMovement(action)

        removeEatenPieces(self.state, not self.state.isWhiteTurn)
        removeEatenPieces(self.state, self.state.isWhiteTurn)
        if self.turns >= 24:
            self.placementPhase = False

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
    # If it is white's turn, it means we can only put in white's starting zone. 
    # Create a set of all the coordinates minus the bottom two rows, then exclude
    # the ones already with pieces and corners. 
    placeList = []
    if state.isWhiteTurn:
        for x in range(8):
            for y in range(6):
                coord = (x,y)
                if (coord not in state.whitePieces and coord not in state.blackPieces
                        and coord not in CORNERS):
                    placeList.append(coord)

    else:
        for x in range(8):
            for y in range(2,8):
                coord = (x,y)
                if (coord not in state.whitePieces and coord not in state.blackPieces
                        and coord not in CORNERS):
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

    #newState.printBoard()

    if turnsLeft == 0 or newState.isEndState():
        return getEvaluationValue(newState)

    choices = []
    for place in getPlaces(newState):
        choices.append((getPlaceValue(place, not ownTurn, newState, turnsLeft-1)))

    if ownTurn:
        return max(choices)
    return min(choices)


# Function that just makes valid placements. 
def noobPlacement(state):
    choices = []
    #for place in getPlaces(state):
    #    choices.append((getPlaceValue(place, False, state, turnsLeft-1), place))
    x = getPlaces(state)
    return random.choice(x) #max(choices)[1]

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
def heurPlacement(state):    
    availableCells = getPlaces(state)
    # Determine weakest quadrant. 
    weakestQuad = weakestQuadrant(state)

    # First, we prioritize kills. 
    killList = []
    # Construct a list of cells that can result in kills. 
    for cell in availableCells:
        if killValue(state,cell)>0:
            killList.append((killValue,cell))
    # From cells that result in kills, we choose a random cell with max kills. 
    # TODO: Implement distance to centre calculation for both kills and control style of play????
    if len(killList)>0:
        print("KIIIIILLLLILLLLLL")
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
    # Construct a list for control evaluation.
    for cell in availableCells:
        controlList.append((controlValue(state,cell), cell))
    maxControlScore,maxControlCoord = max(controlList)
    
    # Construct a list that only holds coords with best control score at this point. 
    controlList2 = []
    for entry in controlList:
        if entry[0] is maxControlScore:
            controlList2.append(entry)

    # Prune controlList further to only include coords in weakest quadrant. 
    controlList3 = []
    for entry in controlList2:
        if entry[1] in weakestQuad:
            controlList3.append(entry[1])
    # If not possible to control maxControl number of cells by placing in weakest quadrant,
    # then we disregard quadrant analysis and place it on random cell that returns most control. 
    if len(controlList3) == 0:
        returnEntry =  random.choice(controlList2)
        return returnEntry[1]
    else: 
        return random.choice(controlList3)

# We control an adjacent cell if the next one in that direction is not enemy cell, or not out of bounds
# That first adjacent cell has to be empty. 
# This function calculates the number of cell that we can GAIN in control if we place a piece there. 
def controlValue(state, coord):
    enemyPieces = state.enemyPieces()
    allyPieces = state.allyPieces()
    controlScore = 0
    coordPairsToCheck = ((up(coord), twoUp(coord)),(down(coord), twoDown(coord)),(left(coord),twoLeft(coord)),(right(coord), twoRight(coord)))
    for coord1,coord2 in coordPairsToCheck:
        if inBoardRange(coord1) and inBoardRange(coord2) and state.isEmpty(coord1) and not state.isEnemy(enemyPieces,coord2):
            controlScore += 1
    return controlScore       

# Number of kills that can result from placing a piece on a particular cell. 
def killValue(state, coord):
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
