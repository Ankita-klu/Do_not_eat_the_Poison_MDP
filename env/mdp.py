def generate_all_states():
    '''
    This function generates all valid state representations for a 4x5 Chomp board.
    Instead of a 2D binary matrix (which would yield over 1 million combinations), 
    we represent the board as a tuple of 4 integers: (x0, x1, x2, x3).
    Each integer represents how many chocolate squares remain in that specific row.
    '''
    #We will store every valid board configuration in this list
    states= []

    #Row 0, the top row  
    #The grid is 4 row by 5 columns.
    #Therefore, a single row can have anywhere from 0 to 5 squares remaining. 
    #rannge(6) is used to produce the values 0, 1, 2, 3, 4, and 5 for the number of squares in the row.
    for x0 in range(6):
        #Row 1 cannot have have more squares than row 0
        # This row is geometrically constrained by Row 0 above it. 
        # Because biting a square in Chomp removes everything to the right and below,
        # a lower row can NEVER be wider than the row immediately above it.
        # range(x0 + 1) enforces this "staircase" rule, ensuring x1 <= x0.
        for x1 in range(x0+1):
            # ROW 2 (Third Row):
            # Similarly constrained by Row 1. It cannot be wider than x1.
            for x2 in range(x1+1):
                #Row 3 (The bottom row) cannot have more square than row 2
                for x3 in range(x2+1):
                    # Once the loops find a valid combination (e.g., 5, 5, 4, 2),
                    # we bundle those 4 lengths into an immutable tuple and save it.
                    states.append((x0, x1, x2, x3))
    # We reverse the list before returning it using Python slicing [::-1].
    # This is purely for our readability. It puts the starting full board  (5, 5, 5, 5) at index 0, and the completely eaten board (0, 0, 0, 0) at the end.
    return states[::-1]

#============================================================================================
# Module-Level Execution: Setup MDP Constraints
#============================================================================================

#Generate the exhuastive list of state exactly once when this file is imported. This is a computationally expensive operation, so we do it at the module level to ensure it's only done once.
ALL_STATES = generate_all_states()
#We explicitly identifies a risk that the state count might not equal 126.
# This assertion proves that our math successfully collapsed the 1 million+ combinations down to exactly 126 valid states
# If this fails, the code safely crashes.
assert len(ALL_STATES) == 126, f"Error:Expected 126 states, but got {len(ALL_STATES)}. Check the state generation logic."

# STATE-TO-INDEX MAPPING FOR Q-TABLES:
# Reinforcement learning algorithms (SARSA and Q-Learning) store their knowledge 
# in a Q-Table, which is built using a numpy matrix. 
# Matrices require integer row indices (0 to 125); they cannot use tuples like (5, 5, 5, 5).
# This dictionary maps each tuple to a unique integer for lightning-fast array lookups.
STATE_TO_INDEX = {state: idx for idx, state in enumerate(ALL_STATES)}

# This block only runs if you execute this specific file directly from the terminal.
# It acts as a quick sanity check.
if __name__ == "__main__":
    print(f"Successfully generated {len(ALL_STATES)} valid states!")
    print(f"Initial Starting State (Full Board): {ALL_STATES[0]}")
    print(f"Empty Terminal State (Game Over): {ALL_STATES[-1]}")
    
def get_legal_actions(state):
    """
    Determines all valid, non-poisonous moves for a given board state.
    In Chomp, a valid move is selecting any currently remaining chocolate square 
    EXCEPT the poisoned square at coordinate (0, 0).
    
    Args:
        state (tuple): The current board configuration, e.g., (5, 5, 4, 2).
        
    Returns:
        list of tuples: A list of valid (row, col) coordinates.
    """
    legal_actions = []
    
    # We iterate over all 4 rows of the board (r = 0, 1, 2, 3)
    for r in range(4):
        
        # state[r] tells us exactly how many squares are currently left in row 'r'.
        # For example, if state[0] is 5, the valid column indices are 0, 1, 2, 3, 4.
        # We use range(state[r]) to iterate through these valid column indices 'c'.
        for c in range(state[r]):
            
            # PHASE 1 ROADMAP REQUIREMENT: "excluding the poisoned (0,0) square"
            # The square at row 0, column 0 is the poison. 
            # A player cannot voluntarily choose to eat it because doing so loses the game.
            # By skipping it here, if a player is ever handed a board where ONLY (0,0) 
            # is left (the state (1, 0, 0, 0)), this function will return an empty list [].
            # An empty list will signal to our environment that the game is over.
            if r == 0 and c == 0:
                continue  # Skip the poison square
                
            # If the square exists and is not the poison, it is a legally valid bite.
            # We record the action as a coordinate tuple (row, column).
            legal_actions.append((r, c))
            
    return legal_actions