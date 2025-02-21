import pandas as pd
from src.util.constants import sgp_hitter_stat_adjustment, vdp_positional_discount_map, sgp_hitter_stat_map

def add_fields(projections_df):
    # slg, ops, tb, bb/k
    projections_df['tb'] = projections_df['single'] + projections_df['double']*2 + projections_df['triple']*3 + projections_df['homerun']*4
    projections_df['slg'] = projections_df['tb']/projections_df['ab']
    projections_df['ops'] = (projections_df['tb'] + projections_df['hit'] + projections_df['bb'] + projections_df['hbp'])/projections_df['pa']
    projections_df['bb_per_k'] = projections_df['bb']/projections_df['k']
    
    return projections_df

def calc_total_hitter_budget(inputs):
    # total "free money" spent on hitters
    #   e.g. total budget minus the number of players selected (since the min price of drafted players is $1)
    
    position_slots = inputs.get('num_slots')
    
    total_hitter_sal_raw = inputs.get('teams')*inputs.get('budget')*inputs.get('hitting_budget_pct')
    total_hitters = position_slots.get('c') + position_slots.get('1b') + position_slots.get('2b') + position_slots.get('ss') + position_slots.get('3b') + position_slots.get('ci') + position_slots.get('mi') + position_slots.get('o') + position_slots.get('u')
    
    total_hitter_sal = total_hitter_sal_raw - total_hitters*inputs.get('teams')
    
    return total_hitter_sal


def get_position_cutoff_map_hitters(inputs):
    
    # num teams
    num_teams = inputs.get('teams')
    
    # utility spot distribution - assume outfielders will occupy this spot 60% of the time
    util_ci = inputs.get('num_slots').get('u') * 0.2
    util_mi = inputs.get('num_slots').get('u') * 0.2
    util_o = inputs.get('num_slots').get('u') * 0.6
    
    # number of players rostered at each summarized position per team
    num_c = inputs.get('num_slots').get('c') 
    num_ci = inputs.get('num_slots').get('1b') + inputs.get('num_slots').get('3b') + inputs.get('num_slots').get('ci') + util_ci
    num_mi = inputs.get('num_slots').get('ss') + inputs.get('num_slots').get('2b') + inputs.get('num_slots').get('mi') + util_mi
    num_o = inputs.get('num_slots').get('o') + util_o
    
    # number of rostered players league wide 
    c_cutoff = num_c * num_teams * 2/3 # catchers are inexplicably dropped by 33% in the google workbook
    ci_cutoff = num_ci * num_teams
    mi_cutoff = num_mi * num_teams
    o_cutoff = num_o * num_teams
    
    position_cutoff_map = {
        "C": c_cutoff,
        "CI": ci_cutoff,
        "MI": mi_cutoff,
        "O": o_cutoff
    }
    
    # print(position_cutoff_map)
    return(position_cutoff_map)
    

def get_league_weighted_avg_hitters(projections_df, position_cutoff_map):
    # first rank players by proj pts grouped by their summarized position
    # next filter out players below the position cutoff
    # lastly take the average stats of these players weighted by pa
    
    # rank points
    projections_df['points_rank'] = projections_df.groupby('summarized_pos')['fpts'].rank(ascending=False)
    
    # join position_cutoff_map 
    projections_df['summarized_pos_cut_rank'] = projections_df['summarized_pos'].map(lambda x: position_cutoff_map.get(x, {}))
    
    # filter out players below cutline rank threshold
    rostered_players = projections_df[projections_df['points_rank'] <= projections_df['summarized_pos_cut_rank']]
    
    # calc league averages for rostered players
    ab = rostered_players['ab'].mean()
    total_hits = (rostered_players['avg']*rostered_players['ab']).sum()
    total_onbase = (rostered_players['obp']*rostered_players['ab']).sum()
    total_bases = (rostered_players['slg']*rostered_players['ab']).sum()
    total_ab = rostered_players['ab'].sum()    
    avg = total_hits/total_ab # need to weight avg by total ab, it's not just the mean of all batting averages
    obp = total_onbase/total_ab # need to weight avg by total ab, it's not just the mean of all batting averages
    slg = total_bases/total_ab # need to weight avg by total ab, it's not just the mean of all batting averages
    ops = (total_bases + total_onbase)/total_ab # need to weight avg by total ab, it's not just the mean of all batting averages
    r = rostered_players['run'].mean()
    hr = rostered_players['homerun'].mean()
    rbi = rostered_players['rbi'].mean()
    sb = rostered_players['sb'].mean()
    k = rostered_players['k'].mean()
    tb = rostered_players['tb'].mean()
    single = rostered_players['single'].mean()
    double = rostered_players['double'].mean()
    triple = rostered_players['triple'].mean()
    hit = single + double + triple + hr
    cs = rostered_players['cs'].mean()
    pa = rostered_players['pa'].mean()
    bb = rostered_players['bb'].mean()
    bb_per_k = bb/k
    tb = rostered_players['tb'].mean()
    bb = rostered_players['bb'].mean()
    
    rostered_players_avgs = {
        'ab': ab,
        'avg': avg,
        'obp': obp,
        'run': r,
        'homerun': hr,
        'rbi': rbi,
        'sb': sb,
        'slg': slg,
        'ops': ops,
        'bb': bb,
        'k': k,
        'tb': tb,
        "hit": hit,
        "bb_per_k": bb_per_k,
        "cs": cs,
        "pa": pa,
        "single": single,
        "double": double,
        "triple": triple,
    }
    
    return rostered_players_avgs, projections_df


def calc_vdp(projections_df, league_weighted_avg, total_hitter_sal, user_inputs):
    # calc vdp
    #   can't just take the `rostered_players_df` because the goofy stuff that goes on with catchers
    
    # get hitter cats for roto league
    hitter_cats = user_inputs.get('hitter_cats')
    
    # unpack league averages
    league_avg_ab = league_weighted_avg.get('ab')
    league_avg_avg = league_weighted_avg.get('avg')
    league_avg_obp = league_weighted_avg.get('obp')
    league_avg_r = league_weighted_avg.get('run')
    league_avg_hr = league_weighted_avg.get('homerun')
    league_avg_rbi = league_weighted_avg.get('rbi')
    league_avg_sb = league_weighted_avg.get('sb')
    league_avg_bb = league_weighted_avg.get('bb')
    league_avg_k = league_weighted_avg.get('k')
    league_avg_tb = league_weighted_avg.get('tb')
    league_avg_hit = league_weighted_avg.get('hit')
    league_avg_cs = league_weighted_avg.get('cs')
    league_avg_pa = league_weighted_avg.get('pa')
    league_avg_single = league_weighted_avg.get('single')
    league_avg_double = league_weighted_avg.get('double')
    league_avg_triple = league_weighted_avg.get('triple')
    league_avg_bb_per_k = league_weighted_avg.get('bb_per_k')
    league_avg_slg = league_weighted_avg.get('slg')
    league_avg_ops = league_weighted_avg.get('ops')
    
    # get raw scores that go into vdp - these get adjusted by some hardcoded values down the line
    #       Need to generalize these steps but faster to just list them all out for now
    raw_score_avg = (projections_df['avg'] - league_avg_avg) / league_avg_avg * projections_df['ab'] / league_avg_ab * sgp_hitter_stat_adjustment.get('avg')
    raw_score_obp = (projections_df['obp'] - league_avg_obp) / league_avg_obp * projections_df['ab'] / league_avg_ab * sgp_hitter_stat_adjustment.get('obp')
    raw_score_r = (projections_df['run'] - league_avg_r) / league_avg_r * sgp_hitter_stat_adjustment.get('r')
    raw_score_hr = (projections_df['homerun'] - league_avg_hr) / league_avg_hr * sgp_hitter_stat_adjustment.get('homerun')
    raw_score_rbi = (projections_df['rbi'] - league_avg_rbi) / league_avg_rbi * sgp_hitter_stat_adjustment.get('rbi')
    raw_score_sb = (projections_df['sb'] - league_avg_sb) / league_avg_sb * sgp_hitter_stat_adjustment.get('sb')
    raw_score_bb = (projections_df['bb'] - league_avg_bb) / league_avg_bb * sgp_hitter_stat_adjustment.get('bb')
    raw_score_k = (-1) * (projections_df['k'] - league_avg_k) / league_avg_k * sgp_hitter_stat_adjustment.get('k')
    raw_score_tb = (projections_df['tb'] - league_avg_tb) / league_avg_tb * sgp_hitter_stat_adjustment.get('tb')
    raw_score_hit = (projections_df['hit'] - league_avg_hit) / league_avg_hit * sgp_hitter_stat_adjustment.get('hit')
    raw_score_cs = (-1) * (projections_df['cs'] - league_avg_cs) / league_avg_cs * sgp_hitter_stat_adjustment.get('cs')
    raw_score_pa = (projections_df['pa'] - league_avg_pa) / league_avg_pa * sgp_hitter_stat_adjustment.get('pa')
    raw_score_single = (projections_df['single'] - league_avg_single) / league_avg_single * sgp_hitter_stat_adjustment.get('single')
    raw_score_double = (projections_df['double'] - league_avg_double) / league_avg_double * sgp_hitter_stat_adjustment.get('double')
    raw_score_triple = (projections_df['triple'] - league_avg_triple) / league_avg_triple * sgp_hitter_stat_adjustment.get('triple')
    raw_score_ab = (projections_df['ab'] - league_avg_ab) / league_avg_ab * sgp_hitter_stat_adjustment.get('ab')
    raw_score_bb_per_k = (projections_df['bb_per_k'] - league_avg_bb_per_k) / league_avg_bb_per_k * sgp_hitter_stat_adjustment.get('bb_per_k')
    raw_score_slg = (projections_df['slg'] - league_avg_slg) / league_avg_slg * projections_df['ab'] / league_avg_ab * sgp_hitter_stat_adjustment.get('slg')
    raw_score_ops = (projections_df['ops'] - league_avg_ops) / league_avg_ops * projections_df['ab'] / league_avg_ab * sgp_hitter_stat_adjustment.get('ops')
    
    
    # max raw scores
    league_max_vdp_avg = max(raw_score_avg)
    league_max_vdp_obp = max(raw_score_obp)
    league_max_vdp_r = max(raw_score_r)
    league_max_vdp_hr = max(raw_score_hr)
    league_max_vdp_rbi = max(raw_score_rbi)
    league_max_vdp_sb = max(raw_score_sb)
    league_max_vdp_ab = max(raw_score_ab)
    league_max_vdp_bb = max(raw_score_bb)
    league_max_vdp_k = max(raw_score_k)
    league_max_vdp_tb = max(raw_score_tb)
    league_max_vdp_hit = max(raw_score_hit)
    league_max_vdp_cs = max(raw_score_cs)
    league_max_vdp_pa = max(raw_score_pa)
    league_max_vdp_single = max(raw_score_single)
    league_max_vdp_double = max(raw_score_double)
    league_max_vdp_triple = max(raw_score_triple)
    league_max_vdp_bb_per_k = max(raw_score_bb_per_k)
    league_max_vdp_slg = max(raw_score_slg)
    league_max_vdp_ops = max(raw_score_ops)
    
    # harcoded mult factors - couldn't get a good answer for how these are calc'd
    mult_fact_avg = sgp_hitter_stat_map.get('avg')
    mult_fact_obp = sgp_hitter_stat_map.get('obp')
    mult_fact_r = sgp_hitter_stat_map.get('r')
    mult_fact_hr = sgp_hitter_stat_map.get('homerun')
    mult_fact_rbi = sgp_hitter_stat_map.get('rbi')
    mult_fact_sb = sgp_hitter_stat_map.get('sb')
    mult_fact_ab = sgp_hitter_stat_map.get('ab')
    mult_fact_bb = sgp_hitter_stat_map.get('bb')
    mult_fact_k = sgp_hitter_stat_map.get('k')
    mult_fact_tb = sgp_hitter_stat_map.get('tb')
    mult_fact_hit = sgp_hitter_stat_map.get('hit')
    mult_fact_cs = sgp_hitter_stat_map.get('cs')
    mult_fact_pa = sgp_hitter_stat_map.get('pa')
    mult_fact_single = sgp_hitter_stat_map.get('single')
    mult_fact_double = sgp_hitter_stat_map.get('double')
    mult_fact_triple = sgp_hitter_stat_map.get('triple')
    mult_fact_bb_per_k = sgp_hitter_stat_map.get('bb_per_k')
    mult_fact_slg = sgp_hitter_stat_map.get('slg')
    mult_fact_ops = sgp_hitter_stat_map.get('ops')
    
    # adjusted vdp scores - get them for all stats, then only add the relevant ones in next step
    #   use dict to make things dynamic
    vdp_score_map = {
        "avg": raw_score_avg * mult_fact_avg / league_max_vdp_avg,
        "obp": raw_score_obp * mult_fact_obp / league_max_vdp_obp,
        "run": raw_score_r * mult_fact_r / league_max_vdp_r,
        "homerun": raw_score_hr * mult_fact_hr / league_max_vdp_hr,
        "rbi": raw_score_rbi * mult_fact_rbi / league_max_vdp_rbi,
        "sb": raw_score_sb * mult_fact_sb / league_max_vdp_sb,
        "ab": raw_score_ab * mult_fact_ab / league_max_vdp_ab,
        "bb": raw_score_bb * mult_fact_bb / league_max_vdp_bb,
        "k": raw_score_k * mult_fact_k / league_max_vdp_k,
        "tb": raw_score_tb * mult_fact_tb / league_max_vdp_tb,
        "hit": raw_score_hit * mult_fact_hit / league_max_vdp_hit,
        "cs": raw_score_cs * mult_fact_cs / league_max_vdp_cs,
        "pa": raw_score_pa * mult_fact_pa / league_max_vdp_pa,
        "single": raw_score_single * mult_fact_single / league_max_vdp_single,
        "double": raw_score_double * mult_fact_double / league_max_vdp_double,
        "triple": raw_score_triple * mult_fact_triple / league_max_vdp_triple,
        "bb_per_k": raw_score_bb_per_k * mult_fact_bb_per_k / league_max_vdp_bb_per_k,
        "slg": raw_score_slg * mult_fact_slg / league_max_vdp_slg,
        "ops": raw_score_ops * mult_fact_ops / league_max_vdp_ops
    }
    
    # take sum of VDP score for the given roto categories
    missing_cats = [cat for cat in hitter_cats if cat not in vdp_score_map]
    
    # break if missing cats
    if missing_cats:
        raise ValueError(f"Missing categories in vdp_score_map: {missing_cats}")

    # Compute vdp_score only if all categories are valid
    vdp_score = sum(vdp_score_map[cat] for cat in hitter_cats)
    projections_df['vdp_score'] = vdp_score
    
    # adjust by position (col BP) - no explaination as to why this is done
    projections_df['vdp_position_discount'] = projections_df['summarized_pos'].map(lambda x: vdp_positional_discount_map.get(x, {})) 
    projections_df['vdp_score_adj'] = projections_df['vdp_score'] - projections_df['vdp_position_discount']
    
    # sum/avg vdp for only the rostered players
    avg_vdp_rostered_players = projections_df[projections_df['points_rank'] <= projections_df['summarized_pos_cut_rank']]['vdp_score_adj'].mean()
    
    # normalized(?) vdp score
    #   In their workbook one calc (BQ4) does an exponential, but the final calc (CQ4) is a multiple
    #   exponential makes more sense, but it doesn't work with negative numbers so maybe that's why they switched to multiplication? Nothing is clear
    #   regardless, the total exponential calc is needed for the `total_normalized_vdp`, but the multiplication is used for the final calc (prob so that the neg numbers flow through)
    projections_df['vdp_score_norm_initial'] = ((projections_df['vdp_score_adj']/avg_vdp_rostered_players)**(125/100)) # exponential - is used to calculate the total-score factor but not final number
    projections_df['vdp_score_norm'] = ((projections_df['vdp_score_adj']/avg_vdp_rostered_players)*(125/100)) # multiplication - is used for the final number
    
    total_normalized_vdp = projections_df[projections_df['vdp_score_norm_initial'] >= 0]['vdp_score_norm_initial'].sum()
    
    projections_df['value'] = round(projections_df['vdp_score_norm']/total_normalized_vdp * total_hitter_sal + 1, 1)
        
    return projections_df
    
    


