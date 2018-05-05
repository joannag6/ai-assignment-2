import random
from moves import *
from minimax import *

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
CORNERS = [(0,0),(7,0),(0,7),(7,7)]

runningReferee = True # TODO remove before submission
class Player:
    def __init__(self, colour):
        self.colour = colour
        isWhite = True if self.colour == "white" else False
        self.state = GameState(INITIAL_BOARD_SIZE, set(), set(), isWhite, isWhite)
        self.turns = 0
        self.movementPhase = True

    def action(self, turns):
        self.turns = turns
        
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
        if self.movementPhase:
            nextMove = noobPlacement(self.state, min(LOOKAHEAD, STARTING_PIECES*2 - turns + 1))
        else:
            # if (MOVEMENT_ONE - turns <= 0):
            #     turnsLeft = MOVEMENT_TWO - turns
            # else:
            #     turnsLeft = MOVEMENT_ONE - turns
            nextMove = minimaxMovement(self.state, LOOKAHEAD_MOVE, turns)

        self.selfUpdate(nextMove)

        # TODO: prints board when not running from referee. 
        if not runningReferee:
            self.state.printBoard()

        # return (x, y) for placing piece
        # return ((oldx, oldy), (newx, newy)) for moving piece
        if turns == 23:
            self.movementPhase = False
      
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
            self.state. blackPieces.remove(move[0])
            self.state.blackPieces.add(move[1])

    # Function that is called only by player, to update it's own state
    # after a move has been made. 
    def selfUpdate(self, action):
        """Update internal game state according to own action"""
        if action == None: returns

        if self.turns < STARTING_PIECES * 2:
            # update placement
            self.updatePlacement(action)
        else:
            # update movement
            self.updateMovement(action)

        removeEatenPieces(self.state, not self.state.isWhiteTurn)
        removeEatenPieces(self.state, self.state.isWhiteTurn)
        

    def update(self, action):
        self.turns += 1
        """Update internal game state according to opponent's action"""

        if self.turns == MOVEMENT_ONE: # end of first moving stage (going to 6x6)
            self.state.shrink(1)
        if self.turns == MOVEMENT_TWO: # end of second moving stage (going to 4x4)
            self.state.shrink(2)

        if action == None: return

        # check if turns is odd (black's turn)
        if self.turns % 2 == 0:
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
        if self.turns == 23:
            self.movementPhase = False
    
    # hacky way to get a user to play as a player, see placementTest.py for more info. 
    def userAction(self, turns):
        self.turns = turns + 1
        turns = self.turns 
        # if odd turns, it is white's turn. 
        if turns % 2 != 0:
            self.state.isWhiteTurn = True
        # if even turns, it is black's turn. 
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


        x = input("input first digit of coord")
        y = input("input second digit of coord")
        x = int(x)
        y = int(y)
        nextMove = (x,y)
        self.selfUpdate(nextMove)

        # TODO: prints board when not running from referee. 
        if not runningReferee:
            self.state.printBoard()

        # return (x, y) for placing piece
        # return ((oldx, oldy), (newx, newy)) for moving piece
      
        return nextMove
        # TODO: Add check for endstate, and do something

