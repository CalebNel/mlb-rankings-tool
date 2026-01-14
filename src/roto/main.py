import pandas as pd
import json

from src.roto import calc_factors_hitters as hitters
from src.roto import calc_factors_pitchers as pitchers
from src.util import util as util

def get_hitter_rankings(projections_df, user_inputs, debug=False):
    
    # filter only hitters - drop pitchers unless it's a UT,P type position because of shohei
    projections_df = projections_df[
        ~(
            projections_df["position"].str.contains(r"(^|,\s*)(SP|RP|P)(\s*,|$)", regex=True, na=False)
            & ~projections_df["position"].str.contains(r"(^|,\s*)UT(\s*,|$)", regex=True, na=False)
        )
    ].reset_index(drop=True)
    if user_inputs.get('season_type', 'preseason') == 'in-season':
        # if in-season projections, filter out dumb positions
        projections_df = projections_df[~projections_df['position'].str.contains('WR', na=False)].reset_index(drop=True)

    # add positions - both reg position and summarized positions should be with projections in prod
    projections_df = util.add_positions(projections_df)

    # get total "free money" spent on hitters
    total_hitter_free_sal = hitters.calc_total_hitter_budget(user_inputs)
    # print(total_hitter_sal)
    # stop()

    # get position rank cutoffs - cols AN:AU in workbook
    position_cutoff_map = hitters.get_position_cutoff_map_hitters(user_inputs)
    # print(position_cutoff_map)
    # stop()

    rostered_players = hitters.get_rostered_players_df(projections_df, position_cutoff_map)
    

    # get league average stats & standard dev of rostered players
    #   get average stats and stanDev for each stat across rostered players at all positions
    #   (rostered players for now just top N players by plate appearances - could dial in more but results wouldn't change materially)
    league_weighted_avg, rostered_players_std = hitters.get_league_weighted_avg_hitters(rostered_players)
    # print(league_weighted_avg)
    # stop()
    
    # get sgp from stats + league weighted average + rostered players stddev
    projections_df = hitters.calc_vdp(projections_df, league_weighted_avg, rostered_players_std, user_inputs)

    # marginal value calculation grouped by position
    projections_df[['marg_value_pos', 'marg_value_pos_unclipped']] = hitters.add_marginal_value_positional(projections_df, position_cutoff_map, percentiles=(0.10, 0.25, 0.50, 1.0))

    # marginal value calculation across all players
    projections_df[['marg_value_all', 'marg_value_all_unclipped']] = hitters.add_marginal_value_overall(projections_df, position_cutoff_map, percentiles=(0.10, 0.25, 0.50, 1.0))

    # combine weighted marginal values and calculate auction values for rostered hitters
    projections_df = hitters.calc_auction_values(projections_df, total_hitter_free_sal, position_cutoff_map, marginal_weight_all=0.7)

    # combine weighted marginal values and calculate auction values for NON-rostered hitters
    projections_df = hitters.calc_auction_values_unrostered(projections_df, position_cutoff_map, marginal_weight_all=0.7, neg_floor=-30.0, anchor_pos_key=None)

    # combine rostered and unrostered auction values
    projections_df["value"] = projections_df["value"].where(projections_df["value"] > 0, projections_df["dummy_value"])
    if debug:
        # print(league_weighted_avg)
        projections_df.to_csv('./data/projections_debug_hitter.csv', index=False)

    return projections_df[['id', 'position', 'value']]

def get_pitcher_rankings(projections_df, user_inputs, debug=False):
    
    # delete once out_allowed is added to event.json
    projections_df = pitchers.add_fields(projections_df)
    
    # filter only pitchers
    projections_df = projections_df[projections_df['position'].str.contains('SP|RP|PP|P', na=False)].reset_index(drop=True)
    projections_df = projections_df[~projections_df['position'].str.contains('UT, SP', na=False)].reset_index(drop=True) # take out shohei's hitter slot
    if user_inputs.get('season_type', 'preseason') == 'in-season':
        # if in-season projections, filter out relief pitchers/closers
        projections_df = projections_df[~projections_df['position'].str.contains('RP', na=False)].reset_index(drop=True)
        projections_df = projections_df[~projections_df['position'].str.contains('UT,P', na=False)].reset_index(drop=True)
        projections_df = projections_df[~projections_df['position'].str.contains('P,UT', na=False)].reset_index(drop=True)
        projections_df = projections_df[~projections_df['position'].str.contains('UT, P', na=False)].reset_index(drop=True)
        projections_df = projections_df[~projections_df['position'].str.contains('WR', na=False)].reset_index(drop=True)
    
    
    # print(projections_df.head(500))
    # stop()

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
    
