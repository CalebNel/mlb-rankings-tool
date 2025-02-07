import pandas as pd

import calc_factors as factors
import util
from inputs import user_inputs

print(user_inputs)

# TODO: figure out the fuckery with multiple positions
#       add logic for league type (mixed/al/nl)

def get_hitter_rankings(projections_df, debug=False):
    
    # get total "free money" spent on hitters
    total_hitter_sal = factors.calc_total_hitter_budget(user_inputs)

    # get cutline score - col AE in workbook
    projections_df = factors.calc_projected_points(projections_df, user_inputs)

    # get position rank cutoffs - cols AN:AU in workbook
    position_cutoff_map = factors.get_position_cutoff_map(user_inputs)
    
    # get league weighted average stats of rostered players
    league_weighted_avg, projections_df = factors.get_league_weighted_avg(projections_df, position_cutoff_map)
    
    # get vdp from stats + league weighted average
    projections_df = factors.calc_vdp(projections_df, league_weighted_avg, total_hitter_sal)
    
    if debug:
        projections_df.to_csv('./data/projections_debug.csv', index=False)

    return projections_df[['mlb_id', 'name', 'vdp_dollars']]




if __name__ == '__main__':
    
    # get raw projections - cols I:Y in workbook - will be fed from API in prod
    projections_df = util.get_projections_df()

    # add positions - both reg position and summarized positions should be with projections in prod
    projections_df = util.add_positions(projections_df)
    
    print(get_hitter_rankings(projections_df))
    
