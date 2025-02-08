import pandas as pd

import calc_factors as factors
import util
import json
from inputs import user_inputs

print(user_inputs)

# TODO: figure out fuckery with multiple positions 
#       add logic for league type (mixed/al/nl)

def get_hitter_rankings(projections_df, debug=False):
    
    # add positions - both reg position and summarized positions should be with projections in prod
    projections_df = util.add_positions(projections_df)
    
    # get total "free money" spent on hitters
    total_hitter_sal = factors.calc_total_hitter_budget(user_inputs)

    # get projectd points - col AE in workbook
    projections_df = factors.calc_projected_points(projections_df, user_inputs)

    # get position rank cutoffs - cols AN:AU in workbook
    position_cutoff_map = factors.get_position_cutoff_map(user_inputs)
    
    # get league weighted average stats of rostered players
    league_weighted_avg, projections_df = factors.get_league_weighted_avg(projections_df, position_cutoff_map)
    
    # get vdp from stats + league weighted average
    projections_df = factors.calc_vdp(projections_df, league_weighted_avg, total_hitter_sal)
    
    if debug:
        projections_df.to_csv('./data/projections_debug.csv', index=False)

    # return projections_df[['id', 'name', 'vdp_dollars']]
    return projections_df[['id', 'vdp_dollars']]




if __name__ == '__main__':
    
    # mimic how projections will be returned from FE
    projections_flattened_json = util.fetch_and_flatten_json()
    projections_df = pd.DataFrame(projections_flattened_json)
    projections_df = projections_df[pd.isna(projections_df['bf'])].reset_index(drop=True) # remove pitchers
    
    hitter_rankings_df = get_hitter_rankings(projections_df)
    hitter_rankings_json = hitter_rankings_df.to_json(orient="records")
    hitter_rankings_json_pretty = json.dumps(json.loads(hitter_rankings_json), indent=4)
    
    print(hitter_rankings_json)
    
