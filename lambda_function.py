import json
import pandas as pd
import os

from src import main
from src import inputs
from src import util

def lambda_handler(event, context):
    
    print(event)
    
    projections_json = event.get('projections')
    user_inputs = event.get('user_inputs')
    
    projections_df = pd.DataFrame(projections_json)
    
    hitter_rankings = main.get_hitter_rankings(projections_df, user_inputs)
    pitcher_rankings = main.get_pitcher_rankings(projections_df, user_inputs)
    
    hitter_payload = json.loads(hitter_rankings.to_json(orient="records"))
    pitcher_payload = json.loads(pitcher_rankings.to_json(orient="records"))
    
    payload = hitter_payload + pitcher_payload
    

    return {
        'statusCode': 200,
        'body': payload
    }


# if __name__ == '__main__':
    
#     user_inputs = inputs.user_inputs
    
#     # mimic how projections will be returned from FE
#     projections_flattened_json = util.fetch_and_flatten_json()
#     event = {
#         "projections": projections_flattened_json,
#         "user_inputs": user_inputs
#     }
#     print(event)
    
#     # Define the file path for the Downloads folder
#     downloads_path = os.path.expanduser("~/Downloads/event.json")

#     # Save the event to a JSON file
#     with open(downloads_path, "w") as f:
#         json.dump(event, f, indent=4)
    
#     print(lambda_handler(event, context=None))

    
    