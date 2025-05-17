import pandas as pd
import numpy as np
import random

# Load dataset
df = pd.read_csv("data/zomato_cleaned.csv")
CUISINE_COL = "primary_cuisine" if "primary_cuisine" in df.columns else "cuisines"

# ------------------------
def simple_filter_rank(data, cuisines, city, budget, top_n=10):
    filtered = data.copy()

    if cuisines:
        filtered = filtered[filtered[CUISINE_COL].isin(cuisines)]
    if city:
        filtered = filtered[filtered["city"] == city]
    if budget:
        filtered = filtered[filtered["cost_bucket"] == budget]

    if filtered.empty:
        return filtered

    filtered = filtered.assign(
        score=lambda x: x["rating"] * (x["votes"] + 1).pow(0.25)
    ).sort_values("score", ascending=False)

    return filtered.head(top_n)[
        ["restaurant_name", CUISINE_COL, "cost", "rating", "votes", "city"]
    ]
# ------------------------

# Dynamically create test cases from real data
sampled_rows = df[[CUISINE_COL, "city", "cost_bucket"]].dropna().drop_duplicates().sample(n=3, random_state=42)
test_cases = [
    {
        "cuisines": [row[CUISINE_COL]],
        "city": row["city"],
        "budget": row["cost_bucket"]
    }
    for _, row in sampled_rows.iterrows()
]

# Evaluation metrics
total_possible = len(df)
total_returned = 0
precision_scores = []

for i, test in enumerate(test_cases):
    result = simple_filter_rank(df, test["cuisines"], test["city"], test["budget"], top_n=10)
    total_returned += len(result)

    if not result.empty:
        precision = np.mean(result["rating"] >= 4.0)
        precision_scores.append(precision)

    print(f"\nTest Case {i+1}:")
    print(f"Cuisine: {test['cuisines']}, City: {test['city']}, Budget: {test['budget']}")
    print(result[["restaurant_name", CUISINE_COL, "rating", "votes"]])

# Final evaluation
avg_precision = np.mean(precision_scores) if precision_scores else 0
coverage = total_returned / total_possible

print("\n------ Final Evaluation ------")
print(f"Average Precision@10: {avg_precision:.2f}")
print(f"Recommendation Coverage: {coverage:.2%}")
