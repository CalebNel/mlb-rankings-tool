import pandas as pd

import calc_factors as factors
import util
from inputs import user_inputs

print(user_inputs)


def get_rankings():

    # get raw projections - cols I:Y in workbook
    projections_df = util.get_projections_df()

    # add positions
    projections_df = util.add_positions(projections_df)

    # get cutline score (gotta do more fuckery here with multiple positions) - col AE in workbook
    projections_df = factors.calc_cutline_xp(projections_df)

    # get position rank cutoffs - cols AN:AU in workbook
    position_cutoff_map = factors.get_position_cutoff_map(user_inputs)

    # get league weighted average stats of rostered players
    league_weighted_avg = factors.get_league_weighted_avg(projections_df, position_cutoff_map)

    return projections_df




if __name__ == '__main__':
    print(get_rankings())
