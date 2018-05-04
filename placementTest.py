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


        nextMove = blackPlayer.userAction(turns+1)
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