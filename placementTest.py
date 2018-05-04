import random
from moves import *
from minimax import *
PLACEMENT_LINE = 2
STARTING_PIECES = 12
LOOKAHEAD = 2
LOOKAHEAD_MOVE = 3
MOVEMENT_ONE = 128 + STARTING_PIECES * 2#128 + STARTING_PIECES * 2
MOVEMENT_TWO = 64 + MOVEMENT_ONE + STARTING_PIECES * 2#64 + MOVEMENT_ONE + STARTING_PIECES * 2

# Python code to simulate placement phase. 
# User has to input move. 



def main():
    #movementService = Movement(GameState(INITIAL_BOARD_SIZE, set(), set(), True, True))
    whitePlayer = Player("white")
    blackPlayer = Player("black")


    for turns in range(1, MOVEMENT_TWO+2, 2):
        # White makes a move, then we do some assessing. 
        nextMove = whitePlayer.action(turns)
        print("white: " + str(nextMove))
        blackPlayer.update(nextMove)
        print("####################################################################")

        nextMove = blackPlayer.userAction(turns+1)
        print("black: " + str(nextMove))
        whitePlayer.update(nextMove)
        print("####################################################################")
        
if __name__ == "__main__":
    main()