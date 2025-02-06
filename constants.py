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
    "2B, 3B, OF": {"detailed": "23O", "summarized": "CI"}
}



if __name__ == '__main__':
    print(summarized_position_map())