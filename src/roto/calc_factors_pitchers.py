import pandas as pd
# from src.util.constants import summarized_position_map, vdp_positional_discount_map, pitcher_hardcoded_factors
from src.util.constants import sgp_pitcher_stat_map

    
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
    

def get_league_weighted_avg_pitchers(projections_df, position_cutoff_map):
    # first rank players by proj pts grouped by their summarized position
    # next filter out players below the position cutoff
    # lastly take the average stats of these players weighted by pa
    
    # rank points
    projections_df['points_rank'] = projections_df.groupby('position')['fpts'].rank(ascending=False)
    
    # join position_cutoff_map 
    projections_df['summarized_pos_cut_rank'] = projections_df['position'].map(lambda x: position_cutoff_map.get(x, {}))
    
    # filter out players below cutline rank threshold
    rostered_players = projections_df[projections_df['points_rank'] <= projections_df['summarized_pos_cut_rank']]
    
    ip = rostered_players['ip'].mean()
    win = rostered_players['win'].mean()
    save = rostered_players['save'].mean()
    k_allowed = rostered_players['k_allowed'].mean()
    era = rostered_players['er'].mean()/rostered_players['ip'].mean() * 9
    walks_and_hits = (rostered_players['whip'] * rostered_players['ip']).mean()
    whip = walks_and_hits/rostered_players['ip'].mean()
    qs = rostered_players['qs'].mean()
    hold = rostered_players['hold'].mean()
    
    
    rostered_players_avgs = {
        'ip': ip,
        'win': win,
        'save': save,
        'k_allowed': k_allowed,
        'era': era,
        'whip': whip,
        'qs': qs,
        'hold': hold
    }
    
    return rostered_players_avgs, projections_df


def calc_vdp_pitchers(projections_df, league_weighted_avg, total_pitcher_sal, user_inputs, position_cutoff_map):
    # calc vdp
    
    # get pitcher cats for roto league
    pitcher_cats = user_inputs.get('pitcher_cats')
    
    # unpack league averages
    league_avg_ip = league_weighted_avg.get('ip')
    league_avg_win = league_weighted_avg.get('win')
    league_avg_save = league_weighted_avg.get('save')
    league_avg_k_allowed = league_weighted_avg.get('k_allowed')
    league_avg_era = league_weighted_avg.get('era')
    league_avg_whip = league_weighted_avg.get('whip')
    league_avg_qs = league_weighted_avg.get('qs')
    league_avg_hold = league_weighted_avg.get('hold')
    
    # get raw scores that go into vdp - these get adjusted by some hardcoded values down the line
    raw_score_win = (projections_df['win'] - league_avg_win) / league_avg_win
    raw_score_save = (projections_df['save'] - league_avg_save) / league_avg_save
    raw_score_era = (projections_df['era'] - league_avg_era) / league_avg_era * (-projections_df['ip']/league_avg_ip)
    raw_score_k = (projections_df['k_allowed'] - league_avg_k_allowed) / league_avg_k_allowed
    raw_score_whip = (projections_df['whip'] - league_avg_whip) / league_avg_whip * (-projections_df['ip']/league_avg_whip)
    raw_score_qs = (projections_df['qs'] - league_avg_qs) / league_avg_qs
    raw_score_hold = (projections_df['qs'] - league_avg_hold) / league_avg_hold
    
    # max raw scores
    league_max_vdp_win = max(raw_score_win)
    league_max_vdp_save = max(raw_score_save)
    league_max_vdp_era = max(raw_score_era)
    league_max_vdp_k = max(raw_score_k)
    league_max_vdp_whip = max(raw_score_whip)
    league_max_vdp_qs = max(raw_score_qs)
    league_max_vdp_hold = max(raw_score_hold)
    
    # harcoded mult factors
    mult_fact_win = sgp_pitcher_stat_map.get('win')
    mult_fact_save = sgp_pitcher_stat_map.get('save')
    mult_fact_era = sgp_pitcher_stat_map.get('era')
    mult_fact_k = sgp_pitcher_stat_map.get('k_allowed')
    mult_fact_whip = sgp_pitcher_stat_map.get('whip')
    mult_fact_qs = sgp_pitcher_stat_map.get('qs')
    mult_fact_hold = sgp_pitcher_stat_map.get('hold')
    
    # adjusted vdp scores - get them for all stats, then only add the relevant ones in next step
    #   use dict to make things dynamic
    vdp_score_map = {
        "win": raw_score_win * mult_fact_win / league_max_vdp_win,
        "save": raw_score_save * mult_fact_save / league_max_vdp_save,
        "era": raw_score_era * mult_fact_era / league_max_vdp_era,
        "k_allowed": raw_score_k * mult_fact_k / league_max_vdp_k,
        "whip": raw_score_whip * mult_fact_whip / league_max_vdp_whip,
        "qs": raw_score_qs * mult_fact_qs / league_max_vdp_qs,
        "hold": raw_score_hold * mult_fact_hold / league_max_vdp_hold
    }
    
    # vdp score
    for cat in pitcher_cats:
        if cat in vdp_score_map:
            projections_df[f'vdp_score_{cat}'] = vdp_score_map[cat]

    # Calculate total vdp_score
    projections_df['vdp_score'] = sum(projections_df[f'vdp_score_{cat}'] for cat in pitcher_cats if f'vdp_score_{cat}' in projections_df)
    
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
    
    # Sum of all positive VDP (i wouldn't do it this way but following the workbook)
    total_normalized_vdp = projections_df[projections_df['vdp_score_norm_initial'] >= 0]['vdp_score_norm_initial'].sum()
    
    # calc value
    projections_df['value'] = round(projections_df['vdp_score_norm_initial']/total_normalized_vdp * total_pitcher_sal + 1, 1)
    
    return projections_df
    
    


