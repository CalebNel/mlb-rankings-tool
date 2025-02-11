import pandas as pd

import calc_factors_hitters as hitters
import calc_factors_pitchers as pitchers
import util
import json
from inputs import user_inputs

print(user_inputs)

# TODO: figure out fuckery with multiple positions 
#       add logic for league type (mixed/al/nl)

def get_hitter_rankings(projections_df, debug=False):
    
    # filter only hitters
    projections_df = projections_df[pd.isna(projections_df['bf'])].reset_index(drop=True) # remove pitchers
    
    # add positions - both reg position and summarized positions should be with projections in prod
    projections_df = util.add_positions(projections_df)
    
    # get total "free money" spent on hitters
    total_hitter_sal = hitters.calc_total_hitter_budget(user_inputs)

    # get projectd points - col AE in workbook
    projections_df = hitters.calc_projected_points_hitter(projections_df, user_inputs)

    # get position rank cutoffs - cols AN:AU in workbook
    position_cutoff_map = hitters.get_position_cutoff_map_hitters(user_inputs)

    # get league weighted average stats of rostered players
    league_weighted_avg, projections_df = hitters.get_league_weighted_avg_hitters(projections_df, position_cutoff_map)
    
    # get vdp from stats + league weighted average
    projections_df = hitters.calc_vdp(projections_df, league_weighted_avg, total_hitter_sal)
    
    if debug:
        projections_df.to_csv('./data/projections_debug_hitter.csv', index=False)

    # return projections_df[['id', 'name', 'vdp_dollars']]
    return projections_df[['id', 'vdp_dollars']]

def get_pitcher_rankings(projections_df, debug=False):
    
    # filter only pitchers
    projections_df = projections_df[projections_df['position'].str.contains('P', na=False)].reset_index(drop=True)
    
    # get total "free money" spent on hitters
    total_pitcher_sal = pitchers.calc_total_pitcher_budget(user_inputs)

    # get projectd points - col AE in workbook
    #   the position adjustments are done later for pitchers
    projections_df = pitchers.calc_projected_points_pitcher(projections_df, user_inputs)

    # get position rank cutoffs
    position_cutoff_map = pitchers.get_position_cutoff_map_pitchers(user_inputs)
    
    # get vdp from stats + league weighted average
    projections_df = pitchers.calc_vdp_pitchers(projections_df, position_cutoff_map, total_pitcher_sal)
    
    if debug:
        projections_df.to_csv('./data/projections_debug_pitcher.csv', index=False)

    # return projections_df[['id', 'name', 'vdp_dollars']]
    return projections_df[['id', 'vdp_dollars']]




if __name__ == '__main__':
    
    # mimic how projections will be returned from FE
    projections_flattened_json = util.fetch_and_flatten_json()
    projections_df = pd.DataFrame(projections_flattened_json)
    
    # get hitter vdp $
    hitter_rankings_df = get_hitter_rankings(projections_df)
    hitter_rankings_json = hitter_rankings_df.to_json(orient="records")
    hitter_rankings_json_pretty = json.dumps(json.loads(hitter_rankings_json), indent=4)
    
    # get pitcher vdp $
    pitcher_rankings_df = get_pitcher_rankings(projections_df)
    pitcher_rankings_json = pitcher_rankings_df.to_json(orient="records")
    pitcher_rankings_json_pretty = json.dumps(json.loads(pitcher_rankings_json), indent=4)
    
    rankings_all = hitter_rankings_json+pitcher_rankings_json
    
    print(rankings_all)
    
