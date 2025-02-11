import pandas as pd
from constants import summarized_position_map, vdp_positional_discount_map, pitcher_hardcoded_factors

    
def calc_total_pitcher_budget(inputs):
    # total "free money" spent on hitters
    #   e.g. total budget minus the number of players selected (since the min price of drafted players is $1)
    
    position_slots = inputs.get('num_slots')
    
    total_pitcher_sal_raw = inputs.get('teams')*inputs.get('budget')*(1-inputs.get('hitting_budget_pct'))
    total_pitchers = position_slots.get('p')
    
    total_pitcher_sal = total_pitcher_sal_raw - total_pitchers*inputs.get('teams')
    
    return total_pitcher_sal


def get_position_cutoff_map_pitchers(inputs):
    
    # num teams
    num_teams = inputs.get('teams')
    
    # num_SP - assume 2 closers per team
    num_sp = num_teams * (inputs.get('num_slots').get('p') - 2)
    num_rp = num_teams * 2
    
    position_cutoff_map = {
        "SP": num_sp,
        "RP": num_rp
    }
    
    # print(position_cutoff_map)
    return(position_cutoff_map)
    

def calc_projected_points_pitcher(projections_df, inputs):
    # comes from user inputs
    ip_fact = inputs.get('pitcher_scoring_coef').get('ip')
    win_fact = inputs.get('pitcher_scoring_coef').get('win')
    save_fact = inputs.get('pitcher_scoring_coef').get('save')
    er_fact = inputs.get('pitcher_scoring_coef').get('er')
    k_fact = inputs.get('pitcher_scoring_coef').get('k_allowed')
    bb_fact = inputs.get('pitcher_scoring_coef').get('bb_allowed')
    hit_fact = inputs.get('pitcher_scoring_coef').get('hit_allowed')
    
    # get scores for each component of points then sum aggregate
    ip_score = projections_df['ip'] * ip_fact
    win_score = projections_df['win'] * win_fact
    save_score = projections_df['save'] * save_fact
    er_score = projections_df['er'] * er_fact
    k_score = projections_df['k_allowed'] * k_fact
    bb_score = projections_df['bb_allowed'] * bb_fact
    hit_score = projections_df['hit_allowed'] * hit_fact
    projections_df['points_raw'] = ip_score + win_score + save_score + er_score + k_score + bb_score + hit_score
    
    # points then gets adjusted by some league-setting factors - docks for multiple positions
    # points_adjustments
    
    return projections_df
    

def get_league_weighted_avg_pitchers(projections_df, position_cutoff_map):
    # first rank players by proj pts grouped by their summarized position
    # next filter out players below the position cutoff
    # lastly take the average stats of these players weighted by pa
    
    # rank points
    projections_df['points_rank'] = projections_df.groupby('position')['points_raw'].rank(ascending=False)
    
    # join position_cutoff_map 
    projections_df['summarized_pos_cut_rank'] = projections_df['position'].map(lambda x: position_cutoff_map.get(x, {}))
    
    # filter out players below cutline rank threshold
    rostered_players = projections_df[projections_df['points_rank'] <= projections_df['summarized_pos_cut_rank']]
    
    # calc league averages for rostered players
    ab = rostered_players['ab'].mean()
    total_hits = (rostered_players['avg']*rostered_players['ab']).sum()
    total_ab = rostered_players['ab'].sum()
    avg = total_hits/total_ab # need to weight avg by total ab, it's not just the mean of all batting averages
    r = rostered_players['run'].mean()
    hr = rostered_players['homerun'].mean()
    rbi = rostered_players['rbi'].mean()
    sb = rostered_players['sb'].mean()
    
    rostered_players_avgs = {
        'ab': ab,
        'avg': avg,
        'run': r,
        'homerun': hr,
        'rbi': rbi,
        'sb': sb
    }
    
    return rostered_players_avgs, projections_df


def calc_vdp_pitchers(projections_df, position_cutoff_map, total_pitcher_sal):
    # calc vdp
    
    # unpack normilization factors
    win_fact_avg = pitcher_hardcoded_factors.get('win').get('avg')
    win_fact_denom = pitcher_hardcoded_factors.get('win').get('denom')
    save_fact_avg = pitcher_hardcoded_factors.get('save').get('avg')
    save_fact_denom = pitcher_hardcoded_factors.get('save').get('denom')
    era_fact_avg = pitcher_hardcoded_factors.get('era').get('avg')
    era_fact_denom = pitcher_hardcoded_factors.get('era').get('denom')
    k_fact_avg = pitcher_hardcoded_factors.get('k').get('avg')
    k_fact_denom = pitcher_hardcoded_factors.get('k').get('denom')
    whip_fact_avg = pitcher_hardcoded_factors.get('whip').get('avg')
    whip_fact_denom = pitcher_hardcoded_factors.get('whip').get('denom')
    ip_fact_avg = pitcher_hardcoded_factors.get('ip').get('avg') #only need the avg for ip
    
    
    # get raw scores that go into vdp - these get adjusted by some hardcoded values down the line
    raw_score_win = (projections_df['win'] - win_fact_avg) / win_fact_denom
    raw_score_save = (projections_df['save'] - save_fact_avg) / save_fact_denom
    raw_score_era = (projections_df['era'] - era_fact_avg) / era_fact_denom * (-projections_df['ip']/ip_fact_avg)
    raw_score_k = (projections_df['k_allowed'] - k_fact_avg) / k_fact_denom
    raw_score_whip = (projections_df['whip'] - whip_fact_avg) / whip_fact_denom * (-projections_df['ip']/ip_fact_avg)
    
    
    # max raw scores
    league_max_vdp_win = max(raw_score_win)
    league_max_vdp_save = max(raw_score_save)
    league_max_vdp_era = max(raw_score_era)
    league_max_vdp_k = max(raw_score_k)
    league_max_vdp_whip = max(raw_score_whip)
    
    
    # harcoded mult factors - pulled from the goog workbook BD:BH - technically circular logic so i think they just hardcoded to skirt around it
    mult_fact_win = 1.01
    mult_fact_save = 2.96
    mult_fact_era = 1.03
    mult_fact_k = 1.01
    mult_fact_whip = 1.06
    
    # adjusted vdp scores - columns BD:BH in the sheet
    vdp_score_win = raw_score_win / league_max_vdp_win * mult_fact_win
    vdp_score_save = raw_score_save / league_max_vdp_save * mult_fact_save
    vdp_score_era = raw_score_era / league_max_vdp_era * mult_fact_era
    vdp_score_k = raw_score_k / league_max_vdp_k * mult_fact_k
    vdp_score_whip = raw_score_whip / league_max_vdp_whip * mult_fact_whip
    
    # vdp score
    vdp_score = vdp_score_win + vdp_score_save + vdp_score_era + vdp_score_k + vdp_score_whip
    projections_df['vdp_score'] = vdp_score

    
    # position values - first rank players based on SP/RP
    projections_df['summarized_pos_cut_rank'] = projections_df['position'].map(lambda x: position_cutoff_map.get(x, {}))
    projections_df['vdp_rank'] = projections_df.groupby('position')['vdp_score'].rank(ascending=False)
    
    # Next get the min vdp score of rostered players - think "what's the value of the last rostered player at each position"
    score_thresholds = projections_df[projections_df['vdp_rank'] <= projections_df['summarized_pos_cut_rank']].groupby('position')['vdp_score'].min()
    sp_score_thresh = score_thresholds.get('SP')
    rp_score_thresh = score_thresholds.get('RP')
    
    # calc normalized vdp score based on position and positive/negative raw vdp_score
    projections_df['vdp_score_norm_initial'] = 0
    # ChatGPT'd this because python is dumb and creates copies of dfs
    projections_df.loc[(projections_df['vdp_score'] >= 0) & (projections_df['position'] == 'SP'), 'vdp_score_norm_initial'] = (
        (projections_df['vdp_score'] - sp_score_thresh) ** (125 / 100)
    )

    projections_df.loc[(projections_df['vdp_score'] < 0) & (projections_df['position'] == 'SP'), 'vdp_score_norm_initial'] = (
        projections_df['vdp_score'] - sp_score_thresh
    )

    projections_df.loc[(projections_df['vdp_score'] >= 0) & (projections_df['position'] == 'RP'), 'vdp_score_norm_initial'] = (
        (projections_df['vdp_score'] - rp_score_thresh) ** (125 / 100)
    )

    projections_df.loc[(projections_df['vdp_score'] < 0) & (projections_df['position'] == 'RP'), 'vdp_score_norm_initial'] = (
        projections_df['vdp_score'] - rp_score_thresh
    )
    # projections_df['vdp_score_norm_initial'][(projections_df['vdp_score'] >= 0) & (projections_df['position'] == 'SP')] = ((projections_df['vdp_score']-sp_score_thresh)**(125/100))
    # projections_df['vdp_score_norm_initial'][(projections_df['vdp_score'] < 0) & (projections_df['position'] == 'SP')] = ((projections_df['vdp_score']-sp_score_thresh))
    # projections_df['vdp_score_norm_initial'][(projections_df['vdp_score'] >= 0) & (projections_df['position'] == 'RP')] = ((projections_df['vdp_score']-rp_score_thresh)**(125/100))
    # projections_df['vdp_score_norm_initial'][(projections_df['vdp_score'] < 0) & (projections_df['position'] == 'RP')] = ((projections_df['vdp_score']-rp_score_thresh))
    
    
    # Sum of all positive VDP (i wouldn't do it this way but following the workbook)
    total_normalized_vdp = projections_df[projections_df['vdp_score_norm_initial'] >= 0]['vdp_score_norm_initial'].sum()
    
    projections_df['vdp_dollars'] = round(projections_df['vdp_score_norm_initial']/total_normalized_vdp * total_pitcher_sal + 1, 1)
    # print(projections_df)
    
    return projections_df
    
    


