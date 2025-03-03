import pandas as pd
import json

from src.roto import calc_factors_hitters as hitters
from src.roto import calc_factors_pitchers as pitchers
from src.util import util as util

def get_hitter_rankings(projections_df, user_inputs, debug=False):
    
    # filter only hitters
    projections_df = projections_df[pd.isna(projections_df['bf'])].reset_index(drop=True) # remove pitchers
    
    # add positions - both reg position and summarized positions should be with projections in prod
    projections_df = util.add_positions(projections_df)
    
    # get total "free money" spent on hitters
    total_hitter_sal = hitters.calc_total_hitter_budget(user_inputs)

    # get position rank cutoffs - cols AN:AU in workbook
    position_cutoff_map = hitters.get_position_cutoff_map_hitters(user_inputs)

    # get league weighted average stats of rostered players
    league_weighted_avg, projections_df = hitters.get_league_weighted_avg_hitters(projections_df, position_cutoff_map)
    
    # get vdp from stats + league weighted average
    projections_df = hitters.calc_vdp(projections_df, league_weighted_avg, total_hitter_sal, user_inputs)
    
    if debug:
        print(league_weighted_avg)
        projections_df.to_csv('./data/projections_debug_hitter.csv', index=False)

    return projections_df[['id', 'position', 'value']]

def get_pitcher_rankings(projections_df, user_inputs, debug=False):
    
    # delete once out_allowed is added to event.json
    projections_df = pitchers.add_fields(projections_df)
    
    # filter only pitchers
    projections_df = projections_df[projections_df['position'].str.contains('P', na=False)].reset_index(drop=True)
    # projections_df = projections_df[projections_df['position'].str.contains('SP', na=False)].reset_index(drop=True)
    
    # get total "free money" spent on hitters
    total_pitcher_sal = pitchers.calc_total_pitcher_budget(user_inputs)

    # get position rank cutoffs
    position_cutoff_map = pitchers.get_position_cutoff_map_pitchers(user_inputs)
    
    # get league weighted average stats of rostered players
    league_weighted_avg, projections_df = pitchers.get_league_weighted_avg_pitchers(projections_df, position_cutoff_map)
    
    # get vdp from stats + league weighted average
    projections_df = pitchers.calc_vdp_pitchers(projections_df, league_weighted_avg, total_pitcher_sal, user_inputs, position_cutoff_map)
    
    if debug:
        print('\nleague weights')
        print(league_weighted_avg)
        projections_df.to_csv('./data/projections_debug_pitcher.csv', index=False)

    return projections_df[['id', 'position', 'value']]

if __name__ == '__main__':
    pd.set_option("display.max_rows", 1000)
    
    file_path = "./src/util/example_post_requests/event.json"
    with open(file_path, "r") as file:
        event = json.load(file)
        
    projections_json = event.get('projections')
    user_inputs = event.get('user_inputs')
    
    # mimic how projections will be returned from FE
    # projections_flattened_json = util.fetch_and_flatten_json()
    projections_df = pd.DataFrame(projections_json)
    
    # get hitter vdp $
    hitter_rankings_df = get_hitter_rankings(projections_df, user_inputs, debug=True)
    hitter_rankings_json = hitter_rankings_df.to_json(orient="records")
    hitter_rankings_json_pretty = json.dumps(json.loads(hitter_rankings_json), indent=4)
    
    # get pitcher vdp $
    pitcher_rankings_df = get_pitcher_rankings(projections_df, user_inputs, debug=True)
    pitcher_rankings_json = pitcher_rankings_df.to_json(orient="records")
    pitcher_rankings_json_pretty = json.dumps(json.loads(pitcher_rankings_json), indent=4)
    
    rankings_all = hitter_rankings_json+pitcher_rankings_json
    
    print(rankings_all)
    
