import random
from moves import *
from minimax import *

PLACEMENT_LINE = 2
STARTING_PIECES = 12
LOOKAHEAD_MOVE = 5
MOVEMENT_ONE = 128
MOVEMENT_TWO = 192
QUAD_ONE = [(0,0), (1,0), (2,0), (3,0), (0,1),(1,1),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(0,3),(1,3),(2,3),(3,3)]
QUAD_TWO = [(4,0),(5,0),(6,0),(7,0),(4,1),(5,1),(6,1),(7,1),(4,2),(5,2),(6,2),(7,2),(4,3),(5,3),(6,3),(7,3)]
QUAD_THREE = [(0,4),(1,4),(2,4),(3,4),(0,5),(1,5),(2,5),(3,5),(0,6),(1,6),(2,6),(3,6),(0,7),(1,7),(2,7),(3,7)]
QUAD_FOUR = [(4,4),(5,4),(6,4),(7,4),(4,5),(5,5),(6,5),(7,5),(4,6),(5,6),(6,6),(7,6),(4,7),(5,7),(6,7),(7,7)]
CORNERS = [(0,0),(7,0),(0,7),(7,7)]

def noobPlacement(state):
    choices = []
    x = getPlaces(state)
    return random.choice(x) #max(choices)[1]

def noobMovement(state, turnsLeft, turns):
    choices = []
    if turns == MOVEMENT_ONE - 1: # end of first moving stage (going to 6x6)
        state.shrink(1)
    if turns == MOVEMENT_TWO - 1: # end of second moving stage (going to 4x4)
        state.shrink(2)

    for move in getMoves(state):
        choices.append(move)

    if choices == []:
        return None
    return random.choice(choices)

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
            nextMove = noobPlacement(self.state)
        else:
            nextMove = noobMovement(self.state, LOOKAHEAD_MOVE, turns)

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
