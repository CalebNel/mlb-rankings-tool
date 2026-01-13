# Hardcoded factors used in calculations. Probably static but who knows

MARGINAL_VALUE_FACTOR = 0.75

eligible_cats = {
    'hitter': ["run", "homerun", "rbi", "sb", "avg", "obp", "slg", "ops", "bb", "k", "tb", "hit", "bb_per_k", "cs", "pa", "ab", "single", "double", "triple"],
    'pitcher': ["win", "save", "era", "k_allowed", "whip", "qs", "hold", "bb_allowed", "hit_allowed", "homerun_allowed", "k_per_9", "loss", "ip", "k_per_bb", "out_allowed", "sold"]
}

    
summarized_position_map = {
    "1B": {"detailed": "1", "summarized": "CI"},
    "1B, 2B": {"detailed": "12", "summarized": "MI"},
    "1B, 2B, 3B": {"detailed": "123", "summarized": "CI"},
    "1B, 2B, OF": {"detailed": "12O", "summarized": "MI"},
    "1B, 3B": {"detailed": "13", "summarized": "CI"},
    "1B, 3B, OF": {"detailed": "13O", "summarized": "CI"},
    "1B, OF": {"detailed": "1O", "summarized": "O"},
    "1B, SS": {"detailed": "1S", "summarized": "MI"},
    "2B": {"detailed": "2", "summarized": "MI"},
    "2B, 3B": {"detailed": "23", "summarized": "CI"},
    "2B, 3B, SS": {"detailed": "23S", "summarized": "MI"},
    "2B, 3B, SS, OF": {"detailed": "23SO", "summarized": "MI"},
    "2B, OF": {"detailed": "2O", "summarized": "MI"},
    "2B, SS": {"detailed": "2S", "summarized": "MI"},
    "2B, SS, OF": {"detailed": "2SO", "summarized": "MI"},
    "3B": {"detailed": "3", "summarized": "CI"},
    "3B, OF": {"detailed": "3O", "summarized": "CI"},
    "3B, SS": {"detailed": "3S", "summarized": "CI"},
    "3B, SS, OF": {"detailed": "3SO", "summarized": "CI"},
    "C": {"detailed": "C", "summarized": "C"},
    "C, 1B": {"detailed": "C1", "summarized": "C"},
    "C, OF": {"detailed": "CO", "summarized": "C"},
    "OF": {"detailed": "O", "summarized": "O"},
    "P": {"detailed": "", "summarized": ""}, 
    "C, 1B, OF": {"detailed": "C1O", "summarized": "C"},
    "SS": {"detailed": "S", "summarized": "MI"},
    "SS, OF": {"detailed": "SO", "summarized": "MI"},
    "UT": {"detailed": "O", "summarized": "O"},
    "UT, P": {"detailed": "O", "summarized": "O"},
    "1B, 2B, SS": {"detailed": "12S", "summarized": "MI"},
    "2B, 3B, OF": {"detailed": "23O", "summarized": "CI"},
    "SP": {"detailed": "SP", "summarized": "SP"},
    "RP": {"detailed": "RP", "summarized": "RP"},
    "IF": {"detailed": "IF", "summarized": "MI"},
}


# if needed, use these to adjust positional importance in roto calculations
    # Higher value => increase importance of position to salary calculation
positional_adjustments = {
    "C": 0.75,
    "CI": 1.0,
    "MI": 1.0,
    "O": 1.0
}

# Use this to adjust importance of various hitter stats in roto calculations
    # Higher value => increase importance of stat to salary calculation
sgp_hitter_stat_map = {
    "avg": 1.0,
    "obp": 1.0,
    "r": 1.0,
    "homerun": 1.0,
    "rbi": 1.0,
    "sb": 1.3, # boosted because they wanted elly to be more valuable
    'slg': 1.0,
    'ops': 1.0,
    'ab': 1.0,
    'bb': 1.0,
    'k': 1.0,
    'tb': 1.0,
    "hit": 1.0,
    "bb_per_k": 1.0,
    "cs": 1.0,
    "pa": 1.0,
    "single": 1.0,
    "double": 1.0,
    "triple": 1.0
}


sgp_pitcher_stat_map = {
    "win": 1.01,
    "era": 1.03,
    "save": 2.96,
    "k_allowed": 1.01,
    "whip": 1.06,
    'qs': 1.01,
    'hold': 1.05,
    'bb_allowed': 1.0,
    'hit_allowed': 1.0,
    'homerun_allowed': 1.0,
    'k_per_9': 1.01,
    'loss': 1.01,
    'ip': 1.0,
    'k_per_bb': 1.0,
    'out_allowed': 1.0,
    'sold': 2.96
}


if __name__ == '__main__':
    print(summarized_position_map())