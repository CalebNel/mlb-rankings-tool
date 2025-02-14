# Inputs changed on FE - will change frequently


user_inputs = {
    "teams": 15,
    "budget": 260,
    "type": "Mixed",
    "hitting_budget_pct": 0.64,
    "num_slots": {
        "c": 2,
        "1b": 1,
        "3b": 1,
        "ci": 1,
        "2b": 1,
        "ss": 1,
        "mi": 1,
        "o": 5,
        "u": 1,
        "p": 9,
        "b": 5
    },
    "cutline_penalties": {
        "dh_penalty": 0,
        "mult_position_2": 0,
        "mult_position_3plus": 0,
        "mult_position_4plus": 0
    },
    "hitter_scoring_coef": {
        "sb": 5,
        "rbi": 2,
        "homerun": 6,
        "run": 2,
        "hit": 4,
        "ab": -1
    },
    "pitcher_scoring_coef": {
        "ip": 3,
        "win": 6,
        "save": 8,
        "er": -2,
        "k_allowed": 1,
        "bb_allowed": -1,
        "hit_allowed": -1,
    }
}


if __name__ == '__main__':
    print(user_inputs)
    
    # "marginal_value_threshold": [0.05, 0.1, 0.25, 0.5, 0.75, 1.0],
    # "marginal_value_threshold": [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],