import pandas as pd
import json

from src.points import calc_value as value
from src.util import util as util


# TODO: figure out fuckery with multiple positions 
#       add logic for league type (mixed/al/nl)

def get_points_league_rankings(projections_df, user_inputs, debug=False):
    
    # add positions - both reg position and summarized positions should be with projections in prod
    projections_df = util.add_positions(projections_df)
    
    # calc raw points - comment out once connected to FE
    projections_df = value.get_raw_points(projections_df)
    
    # return the ranks for each position (and total rostered player) groupings that we calculate marginal value at
    position_rank_dict, total_rank_dict = value.get_value_ranks(user_inputs)
    
    # get actual marginal value for each rank
    marginal_value_dict = value.get_threshold_values(projections_df, position_rank_dict, total_rank_dict)
    
    # calculate marginal value
    projections_df = value.calculate_marginal_value(projections_df, user_inputs, marginal_value_dict)
    
    # calculate salary
    projections_df = value.calculate_salary(projections_df, user_inputs)
    
    if debug:
        projections_df.to_csv('./data/projections_debug_hitter.csv', index=False)

    return projections_df[['id', 'position', 'value']]


if __name__ == '__main__':
    
    # from util.inputs import user_inputs
    # from util.example_post_requests import event as event
    
    file_path = "./src/util/example_post_requests/event.json"
    with open(file_path, "r") as file:
        event = json.load(file)
    
    user_inputs = event.get('user_inputs')
    projections_json = event.get('projections')
    print(user_inputs)
    
    # mimic how projections will be returned from FE
    # projections_flattened_json = util.fetch_and_flatten_json()
    # projections_flattened_json = event.get('projections')
    projections_df = pd.DataFrame(projections_json)
    # print(projections_json)
    # stop()
    
    # get auction value points leagues
    get_points_league_rankings(projections_df, user_inputs, debug = True)
    
    # get hitter vdp $
    # hitter_rankings_df = get_hitter_rankings(projections_df)
    # hitter_rankings_json = hitter_rankings_df.to_json(orient="records")
    # hitter_rankings_json_pretty = json.dumps(json.loads(hitter_rankings_json), indent=4)
    
    # # get pitcher vdp $
    # pitcher_rankings_df = get_pitcher_rankings(projections_df)
    # pitcher_rankings_json = pitcher_rankings_df.to_json(orient="records")
    # pitcher_rankings_json_pretty = json.dumps(json.loads(pitcher_rankings_json), indent=4)
    
    # rankings_all = hitter_rankings_json+pitcher_rankings_json
    
    # print(rankings_all)
    
