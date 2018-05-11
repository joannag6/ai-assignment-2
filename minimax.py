"""COMP30024 Artificial Intelligence Project Part B (2018 Sem 1)

Authors:
Joanna Grace Cho Ern LEE (710094)
Jia Shun LOW (743436)

This module contains the Player class and all the accompanying functions needed
to play the Watch Your Back game, utilising:
    - A heuristic decision-making algorithm for the Placement stage
    - A minimax algorithm with alpha-beta pruning for the Movement stage
"""

import random
from moves import *


class Player:
    def __init__(self, colour):
        self.colour = colour
        self.isWhite = True if self.colour == "white" else False
        self.state = GameState(INITIAL_BOARD_SIZE, set(), set(),
                               self.isWhite, self.isWhite)
        self.placingPhase = True
        self.turns = 0

    def action(self, turns):
        """
        Returns a valid action for this player

        :param int turns: total turns for that phase
        """

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

        return nextMove

    def updateMovement(self, move):
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
            if self.turns == MOVEMENT_ONE: # end of first moving stage (going to 6x6)
                self.state.shrink(1)
            if self.turns == MOVEMENT_TWO: # end of second moving stage (going to 4x4)
                self.state.shrink(2)

        removeEatenPieces(self.state, not self.state.isWhiteTurn)
        removeEatenPieces(self.state, self.state.isWhiteTurn)

        # When black makes 24th move, white's self.turns == 24 after the
        # increment in update(). Then, after the code for update reaches this
        # point, we have to toggle white's placingPhase to False.
        if self.placingPhase and self.turns >= STARTING_PIECES*2:
            self.placingPhase = False

def getMoves(state):
    """Returns set of possible moves for a player given a state"""
    moveList = set()
    if state.isWhiteTurn:
        for piece in state.whitePieces:
            moveList |= state.calcMovesForCoord(piece, state.blackPieces)
    else:
        for piece in state.blackPieces:
            moveList |= state.calcMovesForCoord(piece, state.whitePieces)
    return moveList


def getEvaluationValue(state):
    """Returns the evaluation value for a given state"""
    if state.isWhitePlayer:
        return len(state.whitePieces) - len(state.blackPieces)
    return len(state.blackPieces) - len(state.whitePieces)


def getMoveValue(move, ownTurn, state, turnsLeft, turns, alpha, beta):
    """
    Returns integer value representing evaluation value for that move. If own turn,
    get the maximum possible value. If not own turn, get minimum possible value.
    Also practices alpha beta pruning.
    """

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
        nextVal = getMoveValue(nextMove, not ownTurn, newState, turnsLeft-1,
                               turns+1, alpha, beta)

        if alpha != None and beta != None and beta <= alpha:
           return nextVal

        if ownTurn:
            if alpha == None or nextVal >= alpha:
                alpha = nextVal
        if not ownTurn:
            if beta == None or nextVal <= beta:
                beta = nextVal

    if not possibleMoves:
        return getEvaluationValue(newState)

    if ownTurn:
        return alpha
    return beta


def minimaxMovement(state, turnsLeft, turns):
    """Returns the 'best' move determined by minimax algorithm"""
    choices = []
    if turns == MOVEMENT_ONE - 1: # end of first moving stage (going to 6x6)
        state.shrink(1)
    if turns == MOVEMENT_TWO - 1: # end of second moving stage (going to 4x4)
        state.shrink(2)

    for move in getMoves(state):
        choices.append((getMoveValue(move, False, state, turnsLeft-1, turns+1,
                                     None, None), move))

    return getRandMax(choices)[1]


def getRandMax(tupList):
    """Gets a random max value in case of ties"""
    if not tupList: return None

    smallestVal = max(tupList)[0]
    return random.choice([tup for tup in tupList if tup[0] == smallestVal])


def getPlaces(state):
    """Gets list of valid places given state"""
    # If it is white's turn, it means we can only put in white's starting zone.
    # Create a set of all the coordinates minus the bottom two rows, then
    # check if occupied or corner.
    if state.isWhiteTurn:
        yRange = range(INITIAL_BOARD_SIZE-STARTING_LINE)
    else:
        yRange = range(STARTING_LINE,INITIAL_BOARD_SIZE)

    placeList = []
    for x in range(INITIAL_BOARD_SIZE):
        for y in yRange:
            coord = (x, y)
            if (coord not in state.whitePieces and
                coord not in state.blackPieces and not state.isCorner(x, y)):
                    placeList.append(coord)
    return placeList


def weakestQuadrant(state):
    """Get the 'weakest' quadrant for that current state"""
    quadOneCount = 0
    quadTwoCount = 0
    quadThreeCount = 0
    quadFourCount = 0
    allyPieces = state.allyPieces()
    for piece in allyPieces:
        if piece in QUAD_ONE:
            quadOneCount+=1
        elif piece in QUAD_TWO:
            quadTwoCount+=1
        elif piece in QUAD_THREE:
            quadThreeCount+=1
        elif piece in QUAD_FOUR:
            quadFourCount+=1
    return min((quadOneCount, QUAD_ONE),
               (quadTwoCount, QUAD_TWO),
               (quadThreeCount, QUAD_THREE),
               (quadFourCount, QUAD_FOUR))[1]


def heurPlacement(player):
    """
    Function that is meant to make good placements based on our self defined
    heuristics.
    """
    if player.isWhite and player.turns == 0:
        return BEST_STARTING_COORD
    state = player.state

    availableCells = getPlaces(state)
    weakestQuad = weakestQuadrant(state)

    # First, we prioritize kills.
    killList = []
    controlList = []

    # Construct a list of cells that can result in kills.
    for cell in availableCells:
        killValue, controlValue = getKillControlValue(state, cell)
        if killValue > 0:
            killList.append((killValue,cell))

        # Construct a list for control evaluation.
        controlList.append((controlValue, cell))

    # From cells that result in kills, we choose a random cell with max kills.
    if len(killList) > 0:
        # Prune the current killList to only contain entries with max killValue.
        killList2 = []
        maxKillValue, cell = max(killList)
        for entry in killList:
            if entry[0] == maxKillValue:
                killList2.append(entry)
        returnEntry = random.choice(killList2)
        # Prune the current killList to only contain weakest quadrant entries.
        killList3 = []
        for entry in killList2:
            if entry[1] in weakestQuad:
                killList3.append(entry[1])
        # If not possible to control maxControl number of cells by placing in
        # weakest quadrant, then we disregard quadrant analysis and place it on
        # random cell that returns most control.
        if len(killList3) == 0:
            return returnEntry[1]
        return random.choice(killList3)

    # if we reach here, no kills possible.
    # If we can't kill, we just play for control.
    nonAllowedList = enemyControlledCells(player.state)

    # Set of coords we can place pieces that will result in them instantly dying.
    instantDeathCoords = getEaten(state, state.enemyPieces(), availableCells)#instantDeathPlacement(state, availableCells)

    for cell in instantDeathCoords:
        if cell not in nonAllowedList:
            nonAllowedList.append(cell)

    maxControlScore, maxControlCoord = max(controlList)

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
        returnEntry = random.choice(controlList2)
        return returnEntry[1]
    else:
        return random.choice(controlList3)


def enemyControlledCells(state):
    """
    Function that takes a state and returns list of cells that, if we place a
    piece, allows opponent to instantly kill that piece.
    """
    enemyPieces = state.enemyPieces()
    nonAllowedList = []
    for coord in enemyPieces:
        coordPairsToCheck = ((up(coord), twoUp(coord)),(down(coord), twoDown(coord)),(left(coord),twoLeft(coord)),(right(coord), twoRight(coord)))
        for coord1,coord2 in coordPairsToCheck:
            x1, y1 = coord1
            x2, y2 = coord2
            if state.withinBounds(x1, y1) and state.withinBounds(x2, y2) and state.isEmpty_(x1, y1) and state.isEmpty_(x2, y2):
                nonAllowedList.append(coord1)
    return nonAllowedList


def getKillControlValue(state, coord):
    """
    We control an adjacent cell if the next one in that direction is not enemy
    cell, or not out of bounds. That first adjacent cell has to be empty.
    This function calculates the number of cells that we can GAIN in control if
    we place a piece there.
    """
    enemyPieces = state.enemyPieces()
    allyPieces = state.allyPieces()
    killValue = 0
    controlScore = 0
    coordPairsToCheck = ((up(coord), twoUp(coord)),(down(coord), twoDown(coord)),(left(coord),twoLeft(coord)),(right(coord), twoRight(coord)))
    for coord1,coord2 in coordPairsToCheck:
        x1, y1 = coord1
        x2, y2 = coord2
        if state.withinBounds(x1, y1) and state.withinBounds(x2, y2) and state.isEmpty_(x1, y1) and not state.isEnemyOrCorner(coord2):
            controlScore += 1
        if state.withinBounds(x1, y1) and state.withinBounds(x2, y2) and state.isEnemyOrCorner(coord1) and state.isAlly(coord2):
            killValue+=1
    return killValue, controlScore
