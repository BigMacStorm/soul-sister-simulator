# Configuration constants for the simulator
ESPER_PAY_RATE = 0.2
CHANCE_NON_BASIC_LAND = 0.25
NUM_SIMULATIONS = 10000

# Opponent simulation configuration
OPPONENT_CONFIG = {
    # Number of opponents to simulate
    'num_opponents': 1,
    
    # Base probability of playing a land on each turn (0.0 to 1.0)
    'land_play_probability': 0.85,
    
    # Base probability of playing a creature on each turn (0.0 to 1.0)
    'creature_play_probability': 0.70,
    
    # Base probability of a creature dying on opponent's board each turn (0.0 to 1.0)
    'creature_death_probability': 0.15,
    
    # Base probability of playing removal (targeting our creatures) each turn (0.0 to 1.0)
    'removal_play_probability': 0.1,
    
    # Base probability of playing a board wipe each turn (0.0 to 1.0)
    'board_wipe_probability': 0.05,
    
    # Maximum number of creatures each opponent can have on board
    'max_creatures': 24,
    
    # Scaling configuration for turn-based event frequency
    'scaling': {
        # Base scaling factor (how much events increase per turn)
        'base_scaling_factor': 0.1,
        
        # Maximum scaling factor (cap on how much events can increase)
        'max_scaling_factor': 4.0,
        
        # Turn at which scaling starts (before this turn, use base probabilities)
        'scaling_start_turn': 1,
        
        # Maximum number of events per action type per turn
        'max_events_per_turn': {
            'play_creature': 3,
            'creature_death': 2,
            'play_removal': 2,
            'play_board_wipe': 1,
        },
        
        # Scaling formula: 'linear', 'exponential', or 'logarithmic'
        'scaling_formula': 'exponential',
    }
} 