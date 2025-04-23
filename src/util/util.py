import pandas as pd
import requests
from src.util.constants import summarized_position_map, eligible_cats, sgp_hitter_stat_map, sgp_hitter_stat_adjustment, sgp_pitcher_stat_map


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

# def add_positions(projections_df):
#     # add mapping of summarized positions
    
#     projections_df['position'] = projections_df['position'].str.strip()
#     # summarized_position_map_strip = {
#     #     k.strip(): v for k, v in summarized_position_map.items()
#     # }
#     # summarized_position_map_ = dict((k.strip(), v) for k, v in summarized_position_map.items())
#     summarized_position_map_strip = {
#         k.replace(" ", ""): v for k, v in summarized_position_map.items()
#     }
#     # for k in summarized_position_map_strip:
#     #     print(repr(k))
#     print(summarized_position_map_strip)
#     projections_df['summarized_pos'] = projections_df['position'].map(
#         lambda x: summarized_position_map_strip.get(x, {}).get('summarized')
#     )
    
#     print(projections_df.head(20))
#     stop()
    
#     # projections_df['summarized_pos'] = projections_df['position'].map(lambda x: summarized_position_map.get(x, {}).get('summarized'))
    
#     return projections_df

def add_positions(projections_df):
    # add mapping of summarized positions
    projections_df['position'] = projections_df['position'].str.strip()
    
    summarized_position_map_strip = {
        k.replace(" ", ""): v for k, v in summarized_position_map.items()
    }

    projections_df['summarized_pos'] = projections_df['position'].map(
        lambda x: summarized_position_map_strip.get(x.replace(" ", ""), {}).get('summarized')
        if isinstance(x, str) else None
    )

    # id bad mappings
    bad_rows = projections_df[projections_df['summarized_pos'].isna()]

    if not bad_rows.empty:
        error_msg = (
            "Some player positions could not be mapped.\n\n"
            + bad_rows[['name', 'position']].to_string(index=False)
        )
        raise ValueError(error_msg)

    return projections_df


def fetch_and_flatten_json():
    
    projections_df_url = 'https://models.ftntools.com/api/fantasy/season_projections?season=2025&season_type=PRE&source=VLAD&league=MLB&key=6c9ceb8378934e24abb81011d777cf10'
    response = requests.get(projections_df_url)
    if response.status_code == 200:
            data = response.json()

            flattened_data = []
            for player in data:
                flat_player = {key: value for key, value in player.items() if key not in ["projections", "team"]}
                
                # Extract the stats from projections and add them as new keys
                if "projections" in player:
                    for stat in player["projections"]:
                        flat_player[stat["stat"]] = stat["value"]
                
                # team name and team id        
                if "team" in player and isinstance(player["team"], dict):
                    flat_player["team"] = player["team"].get("name", None)
                    flat_player["team_id"] = player["team"].get("id", None)
                else:
                    flat_player["team"] = None
                    flat_player["team_id"] = None
                    
                flattened_data.append(flat_player)        
                
            return flattened_data  # List of flattened dictionaries
    else:
        raise ValueError(f"Error: Unable to fetch data. Status Code: {response.status_code}")


def get_projections_df_api():
    
    projections_df_url = 'https://models.ftntools.com/api/fantasy/season_projections?season=2025&season_type=PRE&source=VLAD&league=MLB&key=6c9ceb8378934e24abb81011d777cf10'
    response = requests.get(projections_df_url)
    
    # if status=good return data
    if response.status_code == 200:
        data = response.json()
        # projections_df = pd.DataFrame(data)
        projections_df = pd.json_normalize(data)
    else:
        print(f"Error: Unable to fetch data. Status Code: {response.status_code}")
        
    return projections_df