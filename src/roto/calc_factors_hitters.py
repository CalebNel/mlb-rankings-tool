import pandas as pd
import numpy as np
from src.util.constants import sgp_hitter_stat_map, positional_adjustments, MARGINAL_VALUE_FACTOR

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
    c_cutoff = num_c * num_teams
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
    
def get_rostered_players_df(projections_df, position_cutoff_map):
    # first rank players by proj pts grouped by their summarized position
    # next filter out players below the position cutoff
    # lastly return only the rostered players dataframe
    df = projections_df.copy()

    # when calculating league averages, increase the cutoffs by 10% to account for variability
    position_cutoff_map_with_increase = {k: round(v * 1.1,0) for k, v in position_cutoff_map.items()}
    
    # rank points
    df['points_rank'] = df.groupby('summarized_pos')['pa'].rank(ascending=False)
    
    # join position_cutoff_map 
    df['summarized_pos_cut_rank'] = df['summarized_pos'].map(lambda x: position_cutoff_map_with_increase.get(x, {}))

    # filter out players below cutline rank threshold
    try:
        rostered_players = df[df['points_rank'] <= df['summarized_pos_cut_rank']]
    except Exception as e:
        raise ValueError(e)
    
    rostered_players = rostered_players.drop(columns=['points_rank', 'summarized_pos_cut_rank']).reset_index(drop=True)
    return rostered_players


def get_league_weighted_avg_hitters(rostered_players):
    # first rank players by proj pts grouped by their summarized position
    # next filter out players below the position cutoff
    # lastly take the average stats of these players weighted by pa
    
    # calc league averages for rostered players
    ab = rostered_players['ab'].mean()
    total_hits = (rostered_players['avg']*rostered_players['ab']).sum()
    total_onbase = (rostered_players['obp']*rostered_players['pa']).sum()
    total_bases = (rostered_players['slg']*rostered_players['ab']).sum()
    total_ab = rostered_players['ab'].sum()    
    total_pa = rostered_players['pa'].sum()
    avg = total_hits/total_ab # need to weight avg by total ab, it's not just the mean of all batting averages
    obp = total_onbase/total_pa # need to weight avg by total pa, it's not just the mean of all batting averages
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

    # calc league standard deviations for rostered players
    #   calc'ing stand dev basically lets you assign "1 unit of roto value" for each stat
    #   so if league average hr for rosterable players is 16, and std hr is 8, then a player hitting 32 homeruns is "2 units of value" for HR stat.
    ab_std = rostered_players['ab'].std()
    total_hits_std = (rostered_players['avg']*rostered_players['ab']).std()
    total_onbase_std = (rostered_players['obp']*rostered_players['ab']).std()
    total_bases_std = (rostered_players['slg']*rostered_players['ab']).std()
    total_ab_std = rostered_players['ab'].std()
    # have to calculate stanDev of averages differently.
    #   avg and obp can be treated as binomials (yes or no hit/on-base), so use std = sqrt(p(1-p)/n) for those
    #   should really be weighting by ab/pa and calc'ing for each player, but use median for now to keep it simpler
    #   slg/ops are more complicated but use same formula for now
    avg_std = np.sqrt(avg * (1 - avg) / rostered_players["ab"].median())
    obp_std = np.sqrt(obp * (1 - obp) / rostered_players["pa"].median())
    slg_std = np.sqrt(slg / np.median(rostered_players["ab"])) # appx slg stddev by doing league average slugging / median rosterable ab. 
    ops_std = np.sqrt(obp_std**2 + slg_std**2)
    # normal std dev for counting stats
    r_std = rostered_players['run'].std()
    hr_std = rostered_players['homerun'].std()
    rbi_std = rostered_players['rbi'].std()
    sb_std = rostered_players['sb'].std()
    k_std = rostered_players['k'].std()
    tb_std = rostered_players['tb'].std()
    single_std = rostered_players['single'].std()
    double_std = rostered_players['double'].std()
    triple_std = rostered_players['triple'].std()
    hit_std = rostered_players['hit'].std()
    cs_std = rostered_players['cs'].std()
    pa_std = rostered_players['pa'].std()
    bb_std = rostered_players['bb'].std()
    tb_std = rostered_players['tb'].std()
    # bb_per_k calc:
    n = np.median(rostered_players['bb'] + rostered_players['k'])
    bb_per_k_std = np.sqrt(bb_per_k * (1 - bb_per_k) / n)
    

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

    rostered_players_std = {
        'ab_std': ab_std,
        'avg_std': avg_std,
        'obp_std': obp_std,
        'run_std': r_std,
        'homerun_std': hr_std,
        'rbi_std': rbi_std,
        'sb_std': sb_std,
        'slg_std': slg_std,
        'ops_std': ops_std,
        'bb_std': bb_std,
        'k_std': k_std,
        'tb_std': tb_std,
        "hit_std": hit_std,
        "bb_per_k_std": bb_per_k_std,
        "cs_std": cs_std,
        "pa_std": pa_std,
        "single_std": single_std,
        "double_std": double_std,
        "triple_std": triple_std
    }
    
    return rostered_players_avgs, rostered_players_std


def calc_vdp(projections_df, league_weighted_avg, league_weighted_std, user_inputs):
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

    league_std_ab = league_weighted_std.get('ab_std')
    league_std_avg = league_weighted_std.get('avg_std')
    league_std_obp = league_weighted_std.get('obp_std')
    league_std_r = league_weighted_std.get('run_std')
    league_std_hr = league_weighted_std.get('homerun_std')
    league_std_rbi = league_weighted_std.get('rbi_std')
    league_std_sb = league_weighted_std.get('sb_std')
    league_std_bb = league_weighted_std.get('bb_std')
    league_std_k = league_weighted_std.get('k_std')
    league_std_tb = league_weighted_std.get('tb_std')
    league_std_hit = league_weighted_std.get('hit_std')
    league_std_cs = league_weighted_std.get('cs_std')
    league_std_pa = league_weighted_std.get('pa_std')
    league_std_single = league_weighted_std.get('single_std')
    league_std_double = league_weighted_std.get('double_std')
    league_std_triple = league_weighted_std.get('triple_std')
    league_std_bb_per_k = league_weighted_std.get('bb_per_k_std')
    league_std_slg = league_weighted_std.get('slg_std')
    league_std_ops = league_weighted_std.get('ops_std')
    # get raw scores that go into calc:
    #   player stat - league avg / league stddev = raw score
    #   multiply by stat weight from sgp_hitter_stat_map (1.0 is default for all stats)
    #       Need to generalize these steps but faster to just list them all out for now
    # print(projections_df['avg'])
    # print(league_avg_avg)
    # print(league_std_avg)
    # print(projections_df['ab'])
    # print(league_avg_ab)
    # stop()
    sgp_score_avg = (projections_df['avg'] - league_avg_avg) / league_std_avg * projections_df['ab'] / league_avg_ab * sgp_hitter_stat_map.get('avg')
    sgp_score_obp = (projections_df['obp'] - league_avg_obp) / league_std_obp * projections_df['pa'] / league_avg_pa * sgp_hitter_stat_map.get('obp')
    sgp_score_r = (projections_df['run'] - league_avg_r) / league_std_r * sgp_hitter_stat_map.get('r')
    sgp_score_hr = (projections_df['homerun'] - league_avg_hr) / league_std_hr * sgp_hitter_stat_map.get('homerun')
    sgp_score_rbi = (projections_df['rbi'] - league_avg_rbi) / league_std_rbi * sgp_hitter_stat_map.get('rbi')
    sgp_score_sb = (projections_df['sb'] - league_avg_sb) / league_std_sb * sgp_hitter_stat_map.get('sb')
    sgp_score_bb = (projections_df['bb'] - league_avg_bb) / league_std_bb * sgp_hitter_stat_map.get('bb')
    sgp_score_k = (-1) * (projections_df['k'] - league_avg_k) / league_std_k * sgp_hitter_stat_map.get('k')
    sgp_score_tb = (projections_df['tb'] - league_avg_tb) / league_std_tb * sgp_hitter_stat_map.get('tb')
    sgp_score_hit = (projections_df['hit'] - league_avg_hit) / league_std_hit * sgp_hitter_stat_map.get('hit')
    sgp_score_cs = (-1) * (projections_df['cs'] - league_avg_cs) / league_std_cs * sgp_hitter_stat_map.get('cs')
    sgp_score_pa = (projections_df['pa'] - league_avg_pa) / league_std_pa * sgp_hitter_stat_map.get('pa')
    sgp_score_single = (projections_df['single'] - league_avg_single) / league_std_single * sgp_hitter_stat_map.get('single')
    sgp_score_double = (projections_df['double'] - league_avg_double) / league_std_double * sgp_hitter_stat_map.get('double')
    sgp_score_triple = (projections_df['triple'] - league_avg_triple) / league_std_triple * sgp_hitter_stat_map.get('triple')
    sgp_score_ab = (projections_df['ab'] - league_avg_ab) / league_std_ab * sgp_hitter_stat_map.get('ab')
    sgp_score_bb_per_k = (projections_df['bb_per_k'] - league_avg_bb_per_k) / league_std_bb_per_k * sgp_hitter_stat_map.get('bb_per_k')
    sgp_score_slg = (projections_df['slg'] - league_avg_slg) / league_std_slg * projections_df['ab'] / league_avg_ab * sgp_hitter_stat_map.get('slg')
    sgp_score_ops = (projections_df['ops'] - league_avg_ops) / league_std_ops * projections_df['pa'] / league_avg_pa * sgp_hitter_stat_map.get('ops')
    
    
    # adjusted vdp scores - get them for all stats, then only add the relevant ones in next step
    #   use dict to make things dynamic
    sgp_score_map = {
        "avg": sgp_score_avg,
        "obp": sgp_score_obp,
        "run": sgp_score_r,
        "homerun": sgp_score_hr,
        "rbi": sgp_score_rbi,
        "sb": sgp_score_sb,
        "ab": sgp_score_ab,
        "bb": sgp_score_bb,
        "k": sgp_score_k,
        "tb": sgp_score_tb,
        "hit": sgp_score_hit,
        "cs": sgp_score_cs,
        "pa": sgp_score_pa,
        "single": sgp_score_single,
        "double": sgp_score_double,
        "triple": sgp_score_triple,
        "bb_per_k": sgp_score_bb_per_k,
        "slg": sgp_score_slg,
        "ops": sgp_score_ops
    }

    # take sum of SGP score for the given roto categories
    missing_cats = [cat for cat in hitter_cats if cat not in sgp_score_map]

    # break if missing cats
    if missing_cats:
        raise ValueError(f"Missing categories in sgp_score_map: {missing_cats}")

    # create a separate column for each category's SGP score
    for cat in hitter_cats:
        col_name = f"sgp_{cat}"
        projections_df[col_name] = sgp_score_map[cat]

    # keep the summarized SGP score as well
    projections_df['sgp_score'] = sum(projections_df[f"sgp_{cat}"] for cat in hitter_cats)

    return projections_df
    
    
def add_marginal_value_positional(projections_df, position_cutoff_map, percentiles=(0.10, 0.25, 0.50, 1.0)):
    df = projections_df.copy()
    if "summarized_pos" not in df.columns: raise ValueError("missing summarized_pos")
    if "sgp_score" not in df.columns: raise ValueError("missing sgp_score")
    if not isinstance(percentiles, (list, tuple)): raise TypeError("percentiles must be list/tuple")
    bad = [p for p in percentiles if not isinstance(p, (int, float, np.number))]; 
    if bad: raise TypeError(f"percentiles must be numeric; bad={bad!r}")

    df["sgp_rank"] = df.groupby("summarized_pos")["sgp_score"].rank(ascending=False, method="first")
    df["summarized_pos_cut_rank"] = pd.to_numeric(df["summarized_pos"].map(position_cutoff_map), errors="coerce")

    # basically this function gets the baseline sgp_score at each percentile for each position
    def f(g):
        pos = g.name; cut = pd.to_numeric(position_cutoff_map.get(pos, np.nan), errors="coerce")
        if pd.isna(cut): return pd.Series({**{f"baseline_{int(p*100)}": np.nan for p in percentiles}})
        cut = int(cut); n = len(g); out = {}
        for p in percentiles:
            r = int(np.ceil(float(p) * cut)); r = max(1, min(r, cut))
            s = g.loc[g["sgp_rank"] == r, "sgp_score"]; out[f"baseline_{int(p*100)}"] = (s.iloc[0] if len(s) else np.nan)
        return pd.Series(out)

    baselines = df.groupby("summarized_pos", group_keys=False).apply(f)
    df = df.merge(baselines, left_on="summarized_pos", right_index=True, how="left")
    # get sum of marginals across percentiles clipped at 0
    for p in percentiles: 
        df[f"marg_{int(p*100)}_clipped"] = (df["sgp_score"] - df[f"baseline_{int(p*100)}"]).clip(lower=0)
    # get sum of marginals across unclipped
    for p in percentiles: 
        df[f"marg_{int(p*100)}_unclipped"] = (df["sgp_score"] - df[f"baseline_{int(p*100)}"])
    df["marg_total"] = df[[f"marg_{int(p*100)}_clipped" for p in percentiles]].sum(axis=1)
    df["marg_total_unclipped"] = df[[f"marg_{int(p*100)}_unclipped" for p in percentiles]].sum(axis=1)

    # apply positional adjustments
    df['marg_total'] = df['marg_total'] * df['summarized_pos'].map(positional_adjustments)
    df['marg_total_unclipped'] = df['marg_total_unclipped'] * df['summarized_pos'].map(positional_adjustments)

    return df[['marg_total', 'marg_total_unclipped']]


def add_marginal_value_overall(projections_df, position_cutoff_map, percentiles=(0.10, 0.25, 0.50, 1.0), roster_pos_keys=None):
    df = projections_df.copy()
    if "sgp_score" not in df.columns: raise ValueError("missing sgp_score")
    if not isinstance(percentiles, (list, tuple)): raise TypeError("percentiles must be list/tuple")
    bad = [p for p in percentiles if not isinstance(p, (int, float, np.number))]; 
    if bad: raise TypeError(f"percentiles must be numeric; bad={bad!r}")

    if roster_pos_keys is None: roster_pos_keys = list(position_cutoff_map.keys())
    total_cut = int(sum(float(position_cutoff_map.get(k, 0) or 0) for k in roster_pos_keys))
    if total_cut <= 0: raise ValueError("total roster cutoff must be > 0; check roster_pos_keys / position_cutoff_map")

    df["overall_rank"] = df["sgp_score"].rank(ascending=False, method="first")
    df["overall_cut_rank"] = total_cut

    out = {}
    for p in percentiles:
        r = int(np.ceil(float(p) * total_cut)); r = max(1, min(r, total_cut))
        out[f"baseline_{int(p*100)}"] = df.loc[df["overall_rank"].eq(r), "sgp_score"].iloc[0]

    for p in percentiles: 
        df[f"marg_{int(p*100)}_clipped"] = (df["sgp_score"] - out[f"baseline_{int(p*100)}"]).clip(lower=0)
    for p in percentiles: 
        df[f"marg_{int(p*100)}_unclipped"] = (df["sgp_score"] - out[f"baseline_{int(p*100)}"])  
    df["marg_total"] = df[[f"marg_{int(p*100)}_clipped" for p in percentiles]].sum(axis=1)
    df["marg_total_unclipped"] = df[[f"marg_{int(p*100)}_unclipped" for p in percentiles]].sum(axis=1)

    # apply positional adjustments
    df['marg_total'] = df['marg_total'] * df['summarized_pos'].map(positional_adjustments)
    df['marg_total_unclipped'] = df['marg_total_unclipped'] * df['summarized_pos'].map(positional_adjustments)

    return df[['marg_total', 'marg_total_unclipped']]


def calc_auction_values(projections_df, total_hitter_free_sal, position_cutoff_map, marginal_weight_all):
    df = projections_df.copy()
    marginal_weight_pos = 1 - marginal_weight_all

    # sanity check
    if "marg_value_all" not in df.columns: raise ValueError("missing marg_value_all")
    if "marg_value_pos" not in df.columns: raise ValueError("missing marg_value_pos")
    if "summarized_pos" not in df.columns: raise ValueError("missing summarized_pos")

    # combine weighted marginal values and calc final auction values and adj
    df["final_marginal_value"] = (df["marg_value_all"] * marginal_weight_all) + (df["marg_value_pos"] * marginal_weight_pos)
    df["final_marginal_value_adj"] = df["final_marginal_value"] ** MARGINAL_VALUE_FACTOR # squeeze sals closer to 0 a tad - accounts for imperfect projections

    # rank within position
    df["pos_rank"] = df.groupby("summarized_pos")["final_marginal_value_adj"].rank(ascending=False, method="first")

    # enforce position cutoffs
    df["pos_cutoff"] = df["summarized_pos"].map(position_cutoff_map)
    roster_mask = df["pos_rank"] <= df["pos_cutoff"]

    # zero out marginal value for non-rosterable players
    df.loc[~roster_mask, "final_marginal_value_adj"] = 0.0

    # get total marginal value plus sanity check
    total_marginal_value = df["final_marginal_value_adj"].sum()
    if total_marginal_value <= 0: raise ValueError("total marginal value must be > 0")

    # calc auction values - add $1 to all players since min bid is $1
    df["value"] = 0.0
    mask = df["pos_rank"] <= df["pos_cutoff"]
    df.loc[mask, "value"] = ((df.loc[mask, "final_marginal_value_adj"] / total_marginal_value) * total_hitter_free_sal) + 1.0

    return df


def calc_auction_values_unrostered(projections_df, position_cutoff_map, marginal_weight_all, neg_floor=-20.0, anchor_pos_key=None):

    # calc auction values for unrostered players to get their negative "auction values"

    df = projections_df.copy()
    marginal_weight_pos = 1 - marginal_weight_all
    if "summarized_pos" not in df.columns: raise ValueError("missing summarized_pos")
    if "marg_value_all_unclipped" not in df.columns: raise ValueError("missing marg_value_all_unclipped")
    if "marg_value_all" not in df.columns: raise ValueError("missing marg_value_all")
    if "marg_value_pos" not in df.columns: raise ValueError("missing marg_value_pos")

    df["final_marginal_value"] = (df["marg_value_all"] * marginal_weight_all) + (df["marg_value_pos"] * marginal_weight_pos)
    df["final_marginal_value_adj"] = df["final_marginal_value"] ** MARGINAL_VALUE_FACTOR
    df["pos_rank"] = df.groupby("summarized_pos")["final_marginal_value_adj"].rank(ascending=False, method="first")
    df["pos_cutoff"] = df["summarized_pos"].map(position_cutoff_map)
    roster_mask = df["pos_rank"] <= df["pos_cutoff"]

    df["dummy_value"] = np.nan

    if anchor_pos_key is None: anchor_pos_key = next(iter(position_cutoff_map.keys()))
    anchor_cut = int(position_cutoff_map.get(anchor_pos_key, 0))
    if anchor_cut <= 0: raise ValueError("anchor_pos_key cutoff must be > 0")

    anchor_baseline = df.loc[(df["summarized_pos"] == anchor_pos_key) & (df["pos_rank"] == anchor_cut), "marg_value_all_unclipped"]
    if anchor_baseline.empty: anchor_baseline = df.loc[(df["summarized_pos"] == anchor_pos_key), "marg_value_all_unclipped"].sort_values(ascending=False).iloc[anchor_cut - 1:anchor_cut]
    if anchor_baseline.empty: raise ValueError(f"could not find anchor baseline for {anchor_pos_key} at rank {anchor_cut}")
    anchor_baseline = float(anchor_baseline.iloc[0])

    unrostered = ~roster_mask
    df.loc[unrostered, "dummy_value"] = (df.loc[unrostered, "marg_value_all_unclipped"] - anchor_baseline).clip(upper=0)

    df.loc[unrostered, "dummy_value"] = df.loc[unrostered, "dummy_value"].clip(lower=neg_floor)

    return df