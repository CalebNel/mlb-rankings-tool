import pandas as pd
from constants import summarized_position_map

def get_projections_df():
    # get raw projections (from api in prod, csv in this workbook) - cols I:Y in workbook
    projections_df = pd.read_csv('./data/mlb_projections.csv')
    projections_df['ab'] = projections_df['pa'] - projections_df['bb']    
    
    return projections_df

def add_positions(projections_df):
    # first join on mlb_id, then for those that don't have a match join on name
    # should be cleaned up in prod

    position_map = pd.read_csv('./data/position_map.csv')
    
    # goog sheet is boinked and duped and not fun so gotta scrub
    projections_df['mlb_id'] = projections_df['mlb_id'].astype(str)
    position_map['mlb_id'] = position_map['mlb_id'].astype(str)
    position_map_mlb_id = position_map[['mlb_id', 'pos']].drop_duplicates()
    position_map_name = position_map[['name', 'pos']].drop_duplicates()
    
    # join by id then by name where id doesn't exist
    projections_df = pd.merge(projections_df, position_map_mlb_id, how='left', on='mlb_id')
    projections_df = pd.merge(projections_df, position_map_name, how='left', on='name', suffixes=('', '_name')) # call this one pos_name
    projections_df['pos'] = projections_df['pos'].fillna(projections_df['pos_name']) # if there's no match on mlb_id, fill in the pos_name
    projections_df.drop(columns=['pos_name'], inplace=True)
    
    projections_df = projections_df.dropna(subset=['pos']) # drop bros that don't have a position - shouldn't be an issue in prod
    
    # add summarized position - catcher, corner-infield, middle-infield, outfield
    #   chat gpt helped with dict mapping
    projections_df['summarized_pos'] = projections_df['pos'].map(lambda x: summarized_position_map.get(x, {}).get('summarized'))
    
    return projections_df