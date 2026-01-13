import pandas as pd
from src.util.constants import sgp_pitcher_stat_map

def add_fields(projections_df):
    # slg, ops, tb, bb/k
    projections_df['out_allowed'] = projections_df['ip'] * 3
    projections_df['sold'] = projections_df['save'] + projections_df['hold']
    
    return projections_df
    
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
    # assume 75% of utility pitchers are SPs
    sp_fact = .75
    num_sp = num_teams * (inputs.get('num_slots').get('sp') + round(inputs.get('num_slots').get('p')*sp_fact, 0))
    num_rp = num_teams * (inputs.get('num_slots').get('rp') + round(inputs.get('num_slots').get('p')*(1-sp_fact), 0))
    
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
    bb_allowed = rostered_players['bb_allowed'].mean()
    hit_allowed = rostered_players['hit_allowed'].mean()
    homerun_allowed = rostered_players['homerun_allowed'].mean()
    k_per_9 = rostered_players['k_allowed'].mean()/rostered_players['ip'].mean() * 9
    loss = rostered_players['loss'].mean()
    k_per_bb = rostered_players['k_allowed'].mean()/rostered_players['bb_allowed'].mean()
    out_allowed = rostered_players['out_allowed'].mean()
    sold = rostered_players['sold'].mean()
    
    rostered_players_avgs = {
        'ip': ip,
        'win': win,
        'save': save,
        'k_allowed': k_allowed,
        'era': era,
        'whip': whip,
        'qs': qs,
        'hold': hold,
        'bb_allowed': bb_allowed,
        'hit_allowed': hit_allowed,
        'homerun_allowed': homerun_allowed,
        'k_per_9': k_per_9,
        'loss': loss,
        'k_per_bb': k_per_bb,
        'out_allowed': out_allowed,
        'sold': sold
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
    league_avg_bb_allowed = league_weighted_avg.get('bb_allowed')
    league_avg_hit_allowed = league_weighted_avg.get('hit_allowed')
    league_avg_homerun_allowed = league_weighted_avg.get('homerun_allowed')
    league_avg_k_per_9 = league_weighted_avg.get('k_per_9')
    league_avg_loss = league_weighted_avg.get('loss')
    league_avg_k_per_bb = league_weighted_avg.get('k_per_bb')
    league_avg_out_allowed = league_weighted_avg.get('out_allowed')
    league_avg_sold = league_weighted_avg.get('sold')
    
    
    # get raw scores that go into vdp - these get adjusted by some hardcoded values down the line
    #   negate raw scores for cats where low is good
    raw_score_win = (projections_df['win'] - league_avg_win) / league_avg_win
    raw_score_save = (projections_df['save'] - league_avg_save) / league_avg_save
    raw_score_era = (-1) * (projections_df['era'] - league_avg_era) / league_avg_era * (projections_df['ip']/league_avg_ip)
    raw_score_k = (projections_df['k_allowed'] - league_avg_k_allowed) / league_avg_k_allowed
    raw_score_whip = (-1) * (projections_df['whip'] - league_avg_whip) / league_avg_whip * (projections_df['ip']/league_avg_whip)
    raw_score_qs = (projections_df['qs'] - league_avg_qs) / league_avg_qs
    raw_score_hold = (projections_df['qs'] - league_avg_hold) / league_avg_hold
    raw_score_bb_allowed = (-1) * (projections_df['bb_allowed'] - league_avg_bb_allowed) / league_avg_bb_allowed
    raw_score_hit_allowed = (projections_df['hit_allowed'] - league_avg_hit_allowed) / league_avg_hit_allowed
    raw_score_homerun_allowed = (projections_df['homerun_allowed'] - league_avg_homerun_allowed) / league_avg_homerun_allowed
    raw_score_k_per_9 = (projections_df['k_per_9'] - league_avg_k_per_9) / league_avg_k_per_9
    raw_score_loss = (-1) * (projections_df['loss'] - league_avg_loss) / league_avg_loss
    raw_score_ip = (projections_df['ip'] - league_avg_ip) / league_avg_ip
    raw_score_k_per_bb = (projections_df['k_per_bb'] - league_avg_k_per_bb) / league_avg_k_per_bb
    raw_score_out_allowed = (projections_df['out_allowed'] - league_avg_out_allowed) / league_avg_out_allowed
    raw_score_sold = (projections_df['sold'] - league_avg_sold) / league_avg_sold
    
    # max raw scores
    league_max_vdp_win = max(raw_score_win)
    league_max_vdp_save = max(raw_score_save)
    league_max_vdp_era = max(raw_score_era)
    league_max_vdp_k = max(raw_score_k)
    league_max_vdp_whip = max(raw_score_whip)
    league_max_vdp_qs = max(raw_score_qs)
    league_max_vdp_hold = max(raw_score_hold)
    league_max_vdp_bb_allowed = max(raw_score_bb_allowed)
    league_max_vdp_hit_allowed = max(raw_score_hit_allowed)
    league_max_vdp_homerun_allowed = max(raw_score_homerun_allowed)
    league_max_vdp_k_per_9 = max(raw_score_k_per_9)
    league_max_vdp_loss = max(raw_score_loss)
    league_max_vdp_ip = max(raw_score_ip)
    league_max_vdp_k_per_bb = max(raw_score_k_per_bb)
    league_max_vdp_out_allowed = max(raw_score_out_allowed)
    league_max_vdp_sold = max(raw_score_sold)
    
    # harcoded mult factors
    mult_fact_win = sgp_pitcher_stat_map.get('win')
    mult_fact_save = sgp_pitcher_stat_map.get('save')
    mult_fact_era = sgp_pitcher_stat_map.get('era')
    mult_fact_k = sgp_pitcher_stat_map.get('k_allowed')
    mult_fact_whip = sgp_pitcher_stat_map.get('whip')
    mult_fact_qs = sgp_pitcher_stat_map.get('qs')
    mult_fact_hold = sgp_pitcher_stat_map.get('hold')
    mult_fact_bb_allowed = sgp_pitcher_stat_map.get('bb_allowed')
    mult_fact_hit_allowed = sgp_pitcher_stat_map.get('hit_allowed')
    mult_fact_homerun_allowed = sgp_pitcher_stat_map.get('homerun_allowed')
    mult_fact_k_per_9 = sgp_pitcher_stat_map.get('k_per_9')
    mult_fact_loss = sgp_pitcher_stat_map.get('loss')
    mult_fact_ip = sgp_pitcher_stat_map.get('ip')
    mult_fact_k_per_bb = sgp_pitcher_stat_map.get('k_per_bb')
    mult_fact_out_allowed = sgp_pitcher_stat_map.get('out_allowed')
    mult_fact_sold = sgp_pitcher_stat_map.get('sold')
    
    # adjusted vdp scores - get them for all stats, then only add the relevant ones in next step
    #   use dict to make things dynamic
    vdp_score_map = {
        "win": raw_score_win * mult_fact_win / league_max_vdp_win,
        "save": (raw_score_save * mult_fact_save / league_max_vdp_save).fillna(0), # fillna(0) for leagues where RP=0
        "era": raw_score_era * mult_fact_era / league_max_vdp_era,
        "k_allowed": raw_score_k * mult_fact_k / league_max_vdp_k,
        "whip": raw_score_whip * mult_fact_whip / league_max_vdp_whip,
        "qs": raw_score_qs * mult_fact_qs / league_max_vdp_qs,
        "hold": (raw_score_hold * mult_fact_hold / league_max_vdp_hold).fillna(0),
        "bb_allowed": raw_score_bb_allowed * mult_fact_bb_allowed / league_max_vdp_bb_allowed,
        "hit_allowed": raw_score_hit_allowed * mult_fact_hit_allowed / league_max_vdp_hit_allowed,
        "homerun_allowed": raw_score_homerun_allowed * mult_fact_homerun_allowed / league_max_vdp_homerun_allowed,
        "k_per_9": raw_score_k_per_9 * mult_fact_k_per_9 / league_max_vdp_k_per_9,
        "loss": raw_score_loss * mult_fact_loss / league_max_vdp_loss,
        "ip": raw_score_ip * mult_fact_ip / league_max_vdp_ip,
        "k_per_bb": raw_score_k_per_bb * mult_fact_k_per_bb / league_max_vdp_k_per_bb,
        "out_allowed": raw_score_out_allowed * mult_fact_out_allowed / league_max_vdp_out_allowed,
        "sold": (raw_score_sold * mult_fact_sold / league_max_vdp_sold).fillna(0)
    }
    
    
    # take sum of VDP score for the given roto categories
    missing_cats = [cat for cat in pitcher_cats if cat not in vdp_score_map]
    
    # break if missing cats
    if missing_cats:
        raise ValueError(f"Missing categories in vdp_score_map: {missing_cats}")

    # Compute vdp_score only if all categories are valid
    vdp_score = sum(vdp_score_map[cat] for cat in pitcher_cats)
    projections_df['vdp_score'] = vdp_score
    
    # position values - first rank players based on SP/RP
    projections_df['summarized_pos_cut_rank'] = projections_df['position'].map(lambda x: position_cutoff_map.get(x, {}))
    projections_df['vdp_rank'] = projections_df.groupby('position')['vdp_score'].rank(ascending=False)
    
    # Next get the min vdp score of rostered players - think "what's the value of the last rostered player at each position"
    score_thresholds = projections_df[projections_df['vdp_rank'] <= projections_df['summarized_pos_cut_rank']].groupby('position')['vdp_score'].min()
    
    sp_score_thresh = score_thresholds.get('SP', 0)
    rp_score_thresh = score_thresholds.get('RP', 0)
    
    # calc normalized vdp score based on position and positive/negative raw vdp_score
    projections_df['vdp_score_norm_initial'] = 0
    # ChatGPT'd this because python is dumb and creates copies of dfs
    projections_df.loc[(projections_df['vdp_score'] >= 0) & (projections_df['position'] == 'SP'), 'vdp_score_norm_initial'] = (
        (projections_df['vdp_score'] - sp_score_thresh) ** (118 / 100)
    )

    projections_df.loc[(projections_df['vdp_score'] < 0) & (projections_df['position'] == 'SP'), 'vdp_score_norm_initial'] = (
        projections_df['vdp_score'] - sp_score_thresh
    )

    projections_df.loc[(projections_df['vdp_score'] >= 0) & (projections_df['position'] == 'RP'), 'vdp_score_norm_initial'] = (
        (projections_df['vdp_score'] - rp_score_thresh) ** (118 / 100)
    )

    projections_df.loc[(projections_df['vdp_score'] < 0) & (projections_df['position'] == 'RP'), 'vdp_score_norm_initial'] = (
        projections_df['vdp_score'] - rp_score_thresh
    )
    
    # Sum of all positive VDP (i wouldn't do it this way but following the workbook)
    total_normalized_vdp = projections_df[projections_df['vdp_score_norm_initial'] >= 0]['vdp_score_norm_initial'].sum()
    
    # calc value
    projections_df['value'] = round(projections_df['vdp_score_norm_initial']/total_normalized_vdp * total_pitcher_sal + 1, 1)
    projections_df = projections_df.sort_values(by='value', ascending=False)
    
    
    return projections_df
    
    

# helper function to zero-out edge case cats, like saves/holds if no RPs
# def default_if_all_nan(value, default=0):
#     return default if pd.isna(value).all() else value