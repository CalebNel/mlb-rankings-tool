import json
import pandas as pd

from src.roto import main
from src.points import main_pts
from src.util import util

def lambda_handler(event, context):
    
    # unpack event
    projections_json = event.get('projections')
    user_inputs = event.get('user_inputs')
    league_type = user_inputs.get('league_type')
    projections_df = pd.DataFrame(projections_json)
    
    # route to different logic depending on if it's a points or a roto league
    if league_type == 'points':
        rankings = main_pts.get_points_league_rankings(projections_df, user_inputs)
        payload = json.loads(rankings.to_json(orient="records"))
    elif league_type == 'roto':
        # break script if the hit/pitch cats don't match
        util.check_stat_inputs(user_inputs)
        
        hitter_rankings = main.get_hitter_rankings(projections_df, user_inputs, debug=False)
        pitcher_rankings = main.get_pitcher_rankings(projections_df, user_inputs)
        
        hitter_payload = json.loads(hitter_rankings.to_json(orient="records"))
        pitcher_payload = json.loads(pitcher_rankings.to_json(orient="records"))
        
        payload = hitter_payload + pitcher_payload
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Invalid league_type. Must be 'points' or 'roto'."})
        }

    return {
        'statusCode': 200,
        'body': payload
    }


if __name__ == '__main__':
    
    file_path = "./src/util/example_post_requests/event_2026.json"
    # file_path = "./src/util/example_post_requests/event_in_season.json"
    with open(file_path, "r") as file:
        event = json.load(file)
        
    pd.set_option("display.max_rows", 1000)
    data = lambda_handler(event, context=None)
    df = pd.DataFrame(data["body"])
    df = df.sort_values(by="value", ascending=False).reset_index(drop=True)
    print(df.head(50))
    

    rows = data["body"]

    from collections import Counter, defaultdict

    # Count of players with value > 0 by position
    pos_counts = Counter()

    # Sum of values > 0 (overall)
    total_value_sum = 0.0

    # Sum of values > 0 by position (optional but useful)
    pos_value_sum = defaultdict(float)

    for row in rows:
        val = row["value"]
        pos = row["position"]

        if val >= 1:
            # A player may have multiple positions like "2B,3B"
            positions = pos.split(",")
            for p in positions:
                p = p.strip()
                pos_counts[p] += 1
                pos_value_sum[p] += val

            total_value_sum += val

    print("Count > 0 by position:")
    for p, c in pos_counts.items():
        print(f"{p}: {c}")

    print("\nSum of values > 0 by position:")
    for p, s in pos_value_sum.items():
        print(f"{p}: {s:.1f}")

    print("\nTotal sum of all values > 0:", total_value_sum)
    

    rows = data["body"]

    count_c = 0
    sum_c = 0.0

    for row in rows:
        if row["position"] == "C":
            if row["value"] > 1:
                count_c += 1
                sum_c += row["value"]

    # print("Count of C with value > 0:", count_c)
    # print("Sum of C values > 0:", sum_c)
