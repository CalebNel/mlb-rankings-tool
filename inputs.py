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
        "p": 9
    },
    "cutline_penalties": {
        "dh_penalty": 0,
        "mult_position_2": 0,
        "mult_position_3plus": 0,
        "mult_position_4plus": 0
    },
    "scoring_coef": {
        "sb": 5,
        "rbi": 2,
        "hr": 6,
        "r": 2,
        "hit": 4,
        "ab": -1
    }
}


if __name__ == '__main__':
    print(user_inputs)