import pandas as pd
from constants import summarized_position_map


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
    

def calc_cutline_xp(projections_df):
    # no idea why these factors are the way they are - hardcoded into vlad's workbook
    sb_fact = 5
    rbi_fact = 2
    hr_fact = 6
    r_fact = 2
    hit_fact = 4
    ab_fact = -1
    
    # get scores for each component of cutline then sum aggregate
    ab_score = projections_df['ab'] * ab_fact
    hits_score = round(projections_df['ab'] * projections_df['avg'] * hit_fact, 0)
    runs_score = projections_df['r'] * r_fact
    hr_score = projections_df['hr'] * hr_fact
    rbi_score = projections_df['rbi'] * rbi_fact
    sb_score = projections_df['sb'] * sb_fact
    projections_df['cutline_raw'] = ab_score + hits_score + runs_score + hr_score + rbi_score + sb_score
    
    # cutline then gets adjusted by some league-setting factors - docks for multiple positions
    # cutline_adjustments
    
    return projections_df
    
    

def get_league_weighted_avg(projections_df, position_cutoff_map):
    # first rank players by cutline grouped by their summarized position
    # next filter out players below the position cutoff
    # lastly take the average stats of these players weighted by pa
    
    # rank cutline
    projections_df['cutline_rank'] = projections_df.groupby('summarized_pos')['cutline_raw'].rank(ascending=False)
    
    # join position_cutoff_map 
    projections_df['summarized_pos_cut_rank'] = projections_df['summarized_pos'].map(lambda x: position_cutoff_map.get(x, {}))
    
    # filter out players below cutline rank threshold
    rostered_players = projections_df[projections_df['cutline_rank'] <= projections_df['summarized_pos_cut_rank']]
    
    projections_df.to_csv('./data/projections_debug.csv', index=False)
    rostered_players.to_csv('./data/rosteredplayers_debug.csv', index=False)
    
    # calc league averages for rostered players
    ab = rostered_players['ab'].mean()
    total_hits = (rostered_players['avg']*rostered_players['ab']).sum()
    total_ab = rostered_players['ab'].sum()
    avg = total_hits/total_ab # need to weight avg by total ab, it's not just the mean of all batting averages
    r = rostered_players['r'].mean()
    hr = rostered_players['hr'].mean()
    rbi = rostered_players['rbi'].mean()
    sb = rostered_players['sb'].mean()
    
    rostered_players_avgs = {
        'ab': ab,
        'avg': avg,
        'r': r,
        'hr': hr,
        'rbi': rbi,
        'sb': sb
    }
    
    return rostered_players_avgs

