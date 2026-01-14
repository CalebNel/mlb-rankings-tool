import pandas as pd
import requests
from src.util.constants import summarized_position_map, eligible_cats, sgp_hitter_stat_map, sgp_pitcher_stat_map

POSITION_ORDER = {
    "C": 1,
    "1B": 2,
    "2B": 3,
    "3B": 4,
    "SS": 5,
    "OF": 6,
    "SP": 7,
    "RP": 8,
    "P": 9,
    "IF": 10,
    "UT": 11,
    "CI": 12,
    "MI": 13,
}

DROP_POSITIONS = {"CI", "MI", "UT"}  # remove these when they appear alongside real positions

def check_stat_inputs(user_inputs):
    # check the event inputs against the sgp stat maps
    hitter_cats = user_inputs.get('hitter_cats')
    pitcher_cats = user_inputs.get('pitcher_cats')
    
    # take sum of VDP score for the given roto categories
    missing_cats_hitter = [cat for cat in hitter_cats if cat not in eligible_cats.get('hitter')]
    missing_cats_pitcher = [cat for cat in pitcher_cats if cat not in eligible_cats.get('pitcher')]

    # Raise an error if either list has missing categories
    if missing_cats_hitter or missing_cats_pitcher:
        error_message = []
        
        if missing_cats_hitter:
            error_message.append(f"No mapping for the selected hitter categories: {missing_cats_hitter}")
        
        if missing_cats_pitcher:
            error_message.append(f"No mapping for the selected pitcher categories: {missing_cats_pitcher}")

        raise ValueError("\n".join(error_message))


def get_projections_df():
    # get raw projections (from api in prod, csv in this workbook) - cols I:Y in workbook
    projections_df = pd.read_csv('./data/mlb_projections.csv')
    projections_df['ab'] = projections_df['pa'] - projections_df['bb']    
    
    return projections_df

def add_positions(projections_df):
    projections_df = projections_df.copy()
    projections_df["position"] = projections_df["position"].astype(str).str.strip()

    DROP_TOKENS = {"CI", "MI", "UT"}

    POSITION_ORDER = {
        "C": 1,
        "1B": 2,
        "2B": 3,
        "3B": 4,
        "SS": 5,
        "OF": 6,
        "SP": 7,
        "RP": 8,
        "P": 9,
        "IF": 10,
        "UT": 11,
        "CI": 12,
        "MI": 13,
    }

    def normalize_position(pos: str):
        if not isinstance(pos, str):
            return None

        parts = [p.strip() for p in pos.split(",") if p and p.strip()]
        if not parts:
            return None

        parts_set = set(parts)

        # if ONLY CI/MI/UT, keep (per your rule)
        if parts_set.issubset(DROP_TOKENS):
            unique = list(dict.fromkeys(parts))
            unique.sort(key=lambda x: POSITION_ORDER.get(x, 99))
            return ", ".join(unique)

        # otherwise drop CI/MI/UT
        cleaned = [p for p in parts if p not in DROP_TOKENS]
        cleaned = list(dict.fromkeys(cleaned))
        cleaned.sort(key=lambda x: POSITION_ORDER.get(x, 99))

        return ", ".join(cleaned) if cleaned else None

    # build canonical key
    projections_df["position_norm"] = projections_df["position"].map(normalize_position)

    # strip-space key map
    summarized_position_map_strip = {
        k.replace(" ", ""): v for k, v in summarized_position_map.items()
    }

    def lookup_summarized(pos_norm):
        if not isinstance(pos_norm, str):
            return None

        key = pos_norm.replace(" ", "")
        entry = summarized_position_map_strip.get(key)

        # HARD GUARANTEE: return ONLY a string or None
        if entry is None:
            return None
        if isinstance(entry, dict):
            val = entry.get("summarized")
        else:
            # if someone accidentally put a non-dict value in the map
            val = entry

        if val is None:
            return None
        if isinstance(val, dict):
            # this is the critical guard against your exact error class
            raise TypeError(f"Mapping returned a dict for position_norm={pos_norm!r}: {val!r}")

        return str(val)

    projections_df["summarized_pos"] = projections_df["position_norm"].map(lookup_summarized)

    bad_rows = projections_df[projections_df["summarized_pos"].isna()]
    if not bad_rows.empty:
        raise ValueError(
            "Some player positions could not be mapped.\n\n"
            + bad_rows[["name", "position", "position_norm"]].to_string(index=False)
        )

    projections_df.drop(columns=["position_norm"], inplace=True)
    return projections_df




# def fetch_and_flatten_json():
    
#     projections_df_url = 'https://models.ftntools.com/api/fantasy/season_projections?season=2025&season_type=PRE&source=VLAD&league=MLB&key=6c9ceb8378934e24abb81011d777cf10'
#     response = requests.get(projections_df_url)
#     if response.status_code == 200:
#             data = response.json()

#             flattened_data = []
#             for player in data:
#                 flat_player = {key: value for key, value in player.items() if key not in ["projections", "team"]}
                
#                 # Extract the stats from projections and add them as new keys
#                 if "projections" in player:
#                     for stat in player["projections"]:
#                         flat_player[stat["stat"]] = stat["value"]
                
#                 # team name and team id        
#                 if "team" in player and isinstance(player["team"], dict):
#                     flat_player["team"] = player["team"].get("name", None)
#                     flat_player["team_id"] = player["team"].get("id", None)
#                 else:
#                     flat_player["team"] = None
#                     flat_player["team_id"] = None
                    
#                 flattened_data.append(flat_player)        
                
#             return flattened_data  # List of flattened dictionaries
#     else:
#         raise ValueError(f"Error: Unable to fetch data. Status Code: {response.status_code}")


# def get_projections_df_api():
    
#     projections_df_url = 'https://models.ftntools.com/api/fantasy/season_projections?season=2025&season_type=PRE&source=VLAD&league=MLB&key=6c9ceb8378934e24abb81011d777cf10'
#     response = requests.get(projections_df_url)
    
#     # if status=good return data
#     if response.status_code == 200:
#         data = response.json()
#         # projections_df = pd.DataFrame(data)
#         projections_df = pd.json_normalize(data)
#     else:
#         print(f"Error: Unable to fetch data. Status Code: {response.status_code}")
        
#     return projections_df