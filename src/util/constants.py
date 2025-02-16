# Hardcoded factors used in calculations. Probably static but who knows

    
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
    "SP": {"detailed": "SP", "summarized": "P"},
    "RP": {"detailed": "RP", "summarized": "P"}
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
    "sb": 2.2
}

# idk why this is in there. factors that are multiplied by raw stat-adjustment (BE4 and down)
sgp_hitter_stat_adjustment = {
    "avg": 5,
    "obp": 5,
    "r": 1.6,
    "homerun": 1.0,
    "rbi": 1.4,
    "sb": 0.6
}


# These are used to calc pitcher vdp. They are where "league average for rostered players" should be but they are just hardcoded so idk
#   I think it's just a normalization, so subtract league average divided by the standard dev. but not sure
#   sheet: `Pitcher VDP$` columns AT:AX
#
pitcher_hardcoded_factors = {
    "win": {
        "avg": 9.168625,
        "denom": 4.088213
    },
    "save": {
        "avg": 6.518400,
        "denom": 11.789446
    },
    "era": {
        "avg": 3.543764,
        "denom": 0.998204
    },
    "k": {
        "avg": 147.802828,
        "denom": 61.052144
    },
    "whip": {
        "avg": 1.171002,
        "denom": 0.314449
    },
    "ip": {
        "avg": 138.4
    }
}



if __name__ == '__main__':
    print(summarized_position_map())