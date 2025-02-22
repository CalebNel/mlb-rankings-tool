# Hardcoded factors used in calculations. Probably static but who knows

eligible_cats = {
    'hitter': ["run", "homerun", "rbi", "sb", "avg", "obp", "slg", "ops", "bb", "k", "tb", "hit", "bb_per_k", "cs", "pa", "ab", "single", "double", "triple"],
    'pitcher': ["win", "save", "era", "k_allowed", "whip", "qs", "hold", "bb_allowed", "hit_allowed", "homerun_allowed", "k_per_9", "loss", "ip", "k_per_bb", "out_allowed"]
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
    "RP": {"detailed": "RP", "summarized": "RP"}
}



# final vdp scores get adjusted by these relative position scores. not sure where hardcoded numbers come from
vdp_positional_discount_map = {
    "C": -2.17,
    "CI": -1.57,
    "MI": -1.26,
    "O": -2.01
}

# these are used as a stat-importance adjustment (so high SB guys don't get nerfed) - don't really understand why though because in roto high SB guys should be getting nerfed
sgp_hitter_stat_map = {
    "avg": 1.11,
    "obp": 1.11,
    "r": 1.05,
    "homerun": 1.0,
    "rbi": 1.02,
    "sb": 2.2,
    'slg': 1.11,
    'ops': 1.11,
    'ab': 0.8,
    'bb': 1,
    'k': 1,
    'tb': 1,
    "hit": 1,
    "bb_per_k": 1,
    "cs": 0.8,
    "pa": 0.8,
    "single": 1,
    "double": 1.1,
    "triple": 1.2
}

# idk why this is in there. factors that are multiplied by raw stat-adjustment (BE4 and down)
sgp_hitter_stat_adjustment = {
    "avg": 5,
    "obp": 5,
    "r": 1.6,
    "homerun": 1.0,
    "rbi": 1.4,
    "sb": 0.6,
    'slg': 5,
    'ops': 5,
    'ab': 1,
    'bb': 1,
    'k': 1,
    'tb': 1,
    "hit": 1,
    "bb_per_k": 1,
    "cs": 1,
    "pa": 1,
    "single": 1,
    "double": 1,
    "triple": 1,
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
    'out_allowed': 1.0
}


if __name__ == '__main__':
    print(summarized_position_map())