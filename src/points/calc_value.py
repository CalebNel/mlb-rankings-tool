import pandas as pd
# from util.constants import summarized_position_map, vdp_positional_discount_map

def get_number_players(inputs):
        # num teams
    num_teams = inputs.get('teams')
    
    # utility spot distribution - assume outfielders will occupy this spot 60% of the time
    util_ci = inputs.get('num_slots').get('u') * 0.2
    util_mi = inputs.get('num_slots').get('u') * 0.2
    util_o = inputs.get('num_slots').get('u') * 0.6
    
    num_c = inputs.get('num_slots').get('c') * num_teams
    num_ci = (inputs.get('num_slots').get('1b') + inputs.get('num_slots').get('3b') + inputs.get('num_slots').get('ci') + util_ci) * num_teams
    num_mi = (inputs.get('num_slots').get('ss') + inputs.get('num_slots').get('2b') + inputs.get('num_slots').get('mi') + util_mi) * num_teams
    num_o = (inputs.get('num_slots').get('o') + util_o) * num_teams
    num_p = inputs.get('num_slots').get('p') * num_teams
    num_b = inputs.get('num_slots').get('b') * num_teams
    num_starting = num_c + num_ci + num_mi + num_o + num_p
    
    # map positions to total rostered
    positions = {
        "C": num_c,
        "CI": num_ci,
        "MI": num_mi,
        "O": num_o,
        "P": num_p,
    }
    
    return positions

def get_value_ranks(inputs):
    
    # marginal value thresholds
    marginal_value_threshold = inputs.get('marginal_value_threshold')
    
    # num teams
    num_teams = inputs.get('teams')

    # map positions to total rostered
    positions = get_number_players(inputs)

    # create dict of value-cutoff
    position_rank_dict = {
        pos: [round(value * pct)+1 for pct in marginal_value_threshold] 
        for pos, value in positions.items()
    }
    
    # marginal value over total players (not specific to roster)
    num_starting = positions.get('C') + positions.get('CI') + positions.get('MI') + positions.get('O') + positions.get('P')
    num_b = inputs.get('num_slots').get('b') * num_teams
    
    total_rank_dict = [round((num_starting + num_b) * pct)+1 for pct in marginal_value_threshold]
    
    return position_rank_dict, total_rank_dict

def get_threshold_values(projections_df, position_rank_dict, total_rank_dict):
    
    # rank points
    projections_df['points_rank_pos'] = projections_df.groupby('summarized_pos')['fpts'].rank(ascending=False, method='first') # dense ties because we don't want any ranks skipped (1,2,3 not 1,1,3)
    projections_df['points_rank_total'] = projections_df['fpts'].rank(ascending=False, method='first') # dense ties because we don't want any ranks skipped (1,2,3 not 1,1,3)
    
   # Create value_thresh_dict for position-based cutoffs
    value_thresh_dict = {
        pos: get_points_for_rank(
            projections_df[projections_df['summarized_pos'] == pos], 
            'points_rank_pos', 
            position_rank_dict[pos]
        )
        for pos in position_rank_dict
    }

    # Add total rank thresholds
    value_thresh_dict['total'] = get_points_for_rank(projections_df, 'points_rank_total', total_rank_dict)
    
    return(value_thresh_dict)
    
    
    
def calculate_marginal_value(projections_df, user_inputs, marginal_value_dict):
    
    # value adjustment, to change things from being top heavy vs flat
    value_adjustor = user_inputs.get('value_adjustor')
    
    # map the thresholds to the correct position (or for all players for the total_thresh amount)
    position_thresh_df = projections_df['summarized_pos'].map(marginal_value_dict).apply(pd.Series)
    total_thresh_df = pd.DataFrame([marginal_value_dict['total']], index=projections_df.index)
    
    # change column names
    position_thresh_df.columns = [f'pos_thresh_{i+1}' for i in range(position_thresh_df.shape[1])]
    total_thresh_df.columns = [f'total_thresh_{i+1}' for i in range(total_thresh_df.shape[1])]

    # attach the threshold columns
    projections_df = pd.concat([projections_df, position_thresh_df, total_thresh_df], axis=1)

    # get the marginal value for each player at each threshold (so the minimum value is 0 - can't be negative)
    projections_df['fpts_diff_pos'] = position_thresh_df.apply(lambda col: (projections_df['fpts'] - col).clip(lower=0), axis=0).sum(axis=1)
    projections_df['fpts_diff_total'] = total_thresh_df.apply(lambda col: (projections_df['fpts'] - col).clip(lower=0), axis=0).sum(axis=1)
    
    # get total marginal value
    projections_df['marginal_value'] = (projections_df['fpts_diff_total'] + projections_df['fpts_diff_pos']) ** value_adjustor 
    
    return projections_df

    
    
def calculate_salary(projections_df, user_inputs):
    
    # get "free money" - total budget minus $1 for each rostered player since that's the minimum
    total_budget = user_inputs.get('budget') * user_inputs.get('teams')
    positions = get_number_players(user_inputs)
    num_starting = positions.get('C') + positions.get('CI') + positions.get('MI') + positions.get('O') + positions.get('P')
    num_b = user_inputs.get('num_slots').get('b') * user_inputs.get('teams')
    total_drafted_players = num_starting + num_b
    free_money = total_budget - (total_drafted_players)
    
    # get total marginal value
    total_marginal_value = projections_df['marginal_value'].sum()
    projections_df['pct_marg_value'] = projections_df['marginal_value'] / total_marginal_value
    
    # multiply players' percentage of total marginal value by total free money
    projections_df['value'] = projections_df['pct_marg_value']*free_money
    
    # add $1 for all drafted players
    projections_df.loc[projections_df['points_rank_total'] <= total_drafted_players, 'value'] += 1
    
    return projections_df
    
    
    
def get_points_for_rank(df, rank_col, rank_cutoffs):
    # helper function to extract the points for a given position/rank
    return [df.loc[df[rank_col] == cutoff, 'fpts'].max() for cutoff in rank_cutoffs]