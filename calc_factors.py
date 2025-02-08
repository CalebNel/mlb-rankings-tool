import pandas as pd
from constants import summarized_position_map, vdp_positional_discount_map


def calc_total_hitter_budget(inputs):
    # total "free money" spent on hitters
    #   e.g. total budget minus the number of players selected (since the min price of drafted players is $1)
    
    position_slots = inputs.get('num_slots')
    
    total_hitter_sal_raw = inputs.get('teams')*inputs.get('budget')*inputs.get('hitting_budget_pct')
    total_hitters = position_slots.get('c') + position_slots.get('1b') + position_slots.get('2b') + position_slots.get('ss') + position_slots.get('3b') + position_slots.get('ci') + position_slots.get('mi') + position_slots.get('o') + position_slots.get('u')
    
    total_hitter_sal = total_hitter_sal_raw - total_hitters*inputs.get('teams')
    
    return total_hitter_sal
    
    


def get_position_cutoff_map(inputs):
    
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
    
    print(position_cutoff_map)
    return(position_cutoff_map)
    

def calc_projected_points(projections_df, inputs):
    # comes from user inputs
    sb_fact = inputs.get('scoring_coef').get('sb')
    rbi_fact = inputs.get('scoring_coef').get('rbi')
    hr_fact = inputs.get('scoring_coef').get('homerun')
    r_fact = inputs.get('scoring_coef').get('run')
    hit_fact = inputs.get('scoring_coef').get('hit')
    ab_fact = inputs.get('scoring_coef').get('ab')
    
    # get scores for each component of points then sum aggregate
    ab_score = projections_df['ab'] * ab_fact
    hits_score = round(projections_df['ab'] * projections_df['avg'] * hit_fact, 0)
    runs_score = projections_df['run'] * r_fact
    hr_score = projections_df['homerun'] * hr_fact
    rbi_score = projections_df['rbi'] * rbi_fact
    sb_score = projections_df['sb'] * sb_fact
    projections_df['points_raw'] = ab_score + hits_score + runs_score + hr_score + rbi_score + sb_score
    
    # points then gets adjusted by some league-setting factors - docks for multiple positions
    # points_adjustments
    
    return projections_df
    
    

def get_league_weighted_avg(projections_df, position_cutoff_map):
    # first rank players by proj pts grouped by their summarized position
    # next filter out players below the position cutoff
    # lastly take the average stats of these players weighted by pa
    
    # rank points
    projections_df['points_rank'] = projections_df.groupby('summarized_pos')['points_raw'].rank(ascending=False)
    
    # join position_cutoff_map 
    projections_df['summarized_pos_cut_rank'] = projections_df['summarized_pos'].map(lambda x: position_cutoff_map.get(x, {}))
    
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


def calc_vdp(projections_df, league_weighted_avg, total_hitter_sal):
    # calc vdp
    #   can't just take the `rostered_players_df` because the goofy stuff that goes on with catchers
    
    # unpack league averages
    league_avg_ab = league_weighted_avg.get('ab')
    league_avg_avg = league_weighted_avg.get('avg')
    league_avg_r = league_weighted_avg.get('run')
    league_avg_hr = league_weighted_avg.get('homerun')
    league_avg_rbi = league_weighted_avg.get('rbi')
    league_avg_sb = league_weighted_avg.get('sb')
    
    # get raw scores that go into vdp - these get adjusted by some hardcoded values down the line
    raw_score_avg = (projections_df['avg'] - league_avg_avg) / league_avg_avg * projections_df['ab'] / league_avg_ab * 5
    raw_score_r = (projections_df['run'] - league_avg_r) / league_avg_r * 1.6
    raw_score_hr = (projections_df['homerun'] - league_avg_hr) / league_avg_hr * 1
    raw_score_rbi = (projections_df['rbi'] - league_avg_rbi) / league_avg_rbi * 1.4
    raw_score_sb = (projections_df['sb'] - league_avg_sb) / league_avg_sb * 0.6
    
    # max raw scores
    league_max_vdp_avg = max(raw_score_avg)
    league_max_vdp_r = max(raw_score_r)
    league_max_vdp_hr = max(raw_score_hr)
    league_max_vdp_rbi = max(raw_score_rbi)
    league_max_vdp_sb = max(raw_score_sb)
    
    # harcoded mult factors - pulled from the goog workbook BE:BI row 2, but no idea how they are calc'd
    mult_fact_avg = 1.11
    mult_fact_r = 1.05
    mult_fact_hr = 1
    mult_fact_rbi = 1.02
    mult_fact_sb = 2.2
    
    # adjusted vdp scores
    vdp_score_avg = raw_score_avg * mult_fact_avg / league_max_vdp_avg 
    vdp_score_r = raw_score_r * mult_fact_r / league_max_vdp_r
    vdp_score_hr = raw_score_hr * mult_fact_hr / league_max_vdp_hr
    vdp_score_rbi = raw_score_rbi * mult_fact_rbi / league_max_vdp_rbi
    vdp_score_sb = raw_score_sb * mult_fact_sb / league_max_vdp_sb
    
    # vdp score
    vdp_score = vdp_score_avg + vdp_score_r + vdp_score_hr + vdp_score_rbi + vdp_score_sb
    projections_df['vdp_score'] = vdp_score
    
    # adjust by position (col BP)
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
    
    projections_df['vdp_dollars'] = round(projections_df['vdp_score_norm']/total_normalized_vdp * total_hitter_sal + 1, 1)
        
    return projections_df
    
    
