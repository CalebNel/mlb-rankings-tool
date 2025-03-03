import json
import pandas as pd

from src.roto import main
from src.points import main_pts
from src.util import util

def lambda_handler(event, context):
    
    # unpack event
    projections_json = event.get('projections')
    user_inputs = event.get('user_inputs')
    league_type = user_inputs.get('league_type')
    projections_df = pd.DataFrame(projections_json)
    
    # route to different logic depending on if it's a points or a roto league
    if league_type == 'points':
        rankings = main_pts.get_points_league_rankings(projections_df, user_inputs)
        payload = json.loads(rankings.to_json(orient="records"))
    elif league_type == 'roto':
        # break script if the hit/pitch cats don't match
        util.check_stat_inputs(user_inputs)
        
        hitter_rankings = main.get_hitter_rankings(projections_df, user_inputs)
        pitcher_rankings = main.get_pitcher_rankings(projections_df, user_inputs)
        
        hitter_payload = json.loads(hitter_rankings.to_json(orient="records"))
        pitcher_payload = json.loads(pitcher_rankings.to_json(orient="records"))
        
        payload = hitter_payload + pitcher_payload
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Invalid league_type. Must be 'points' or 'roto'."})
        }

    return {
        'statusCode': 200,
        'body': payload
    }


if __name__ == '__main__':
    
    file_path = "./src/util/example_post_requests/event.json"
    # file_path = "./src/util/example_post_requests/full_tuna.json"
    with open(file_path, "r") as file:
        event = json.load(file)
        
    pd.set_option("display.max_rows", 1000)
    print(lambda_handler(event, context=None))
    