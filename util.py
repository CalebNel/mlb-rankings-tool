import pandas as pd
import requests
from constants import summarized_position_map

def get_projections_df():
    # get raw projections (from api in prod, csv in this workbook) - cols I:Y in workbook
    projections_df = pd.read_csv('./data/mlb_projections.csv')
    projections_df['ab'] = projections_df['pa'] - projections_df['bb']    
    
    return projections_df

def add_positions(projections_df):
    # add mapping of summarized positions
    
    projections_df['summarized_pos'] = projections_df['position'].map(lambda x: summarized_position_map.get(x, {}).get('summarized'))
    
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