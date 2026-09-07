# analyze.py
# Key finding: km_since_service (r=0.40), avg_daily_km (r=0.25), and load_factor (r=0.22)
# separate cars that broke down from those that did not. Total odometer and age_years have
# near-zero correlation (r~0.002 and r~-0.001) -- high-mileage and old cars are NOT more
# likely to break down in this data.

import pandas as pd


# ---------------------------------------------------------------------------
# Step 1 — Load and explore
# ---------------------------------------------------------------------------

df = pd.read_csv("fleet_history.csv")

broke = df[df["broke_down"] == 1]
ok    = df[df["broke_down"] == 0]

print("=" * 62)
print(f"Dataset: {len(df)} cars  |  broke_down=1: {len(broke)}  |  broke_down=0: {len(ok)}")
print()

# ---------------------------------------------------------------------------
# Step 2 — Compare groups column by column
# ---------------------------------------------------------------------------
# For each feature, print the mean for each group and its correlation with
# broke_down. A column is a genuine predictor when:
#   (a) the means differ visibly between groups, AND
#   (b) the correlation is clearly above zero.
#
# We deliberately CHECK odometer_km and age_years — the "obvious" answers —
# rather than assume them.

FEATURES = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]

print(f"  {'Column':<20}  {'Broke mean':>10}  {'OK mean':>10}  {'r with broke_down':>18}")
print("  " + "-" * 65)
for col in FEATURES:
    r = df[col].corr(df["broke_down"])
    print(
        f"  {col:<20}  {broke[col].mean():>10.2f}  {ok[col].mean():>10.2f}  {r:>+18.3f}"
    )

print()
print("Conclusion:")
print("  odometer_km      : r~0.002  -- total mileage does NOT predict breakdown")
print("  age_years        : r~-0.001 -- age does NOT predict breakdown")
print("  km_since_service : r=+0.40  -- cars close to/past service interval break")
print("  avg_daily_km     : r=+0.25  -- harder daily use raises risk")
print("  load_factor      : r=+0.22  -- higher load raises risk")

# ---------------------------------------------------------------------------
# Step 3 — Build a 0-to-100 risk score
# ---------------------------------------------------------------------------
# Method: min-max normalise each predictive feature to [0, 1], then take a
# weighted average scaled to 100.  Weights reflect the correlation magnitude.
#
#   km_since_service : weight 0.50  (strongest signal)
#   avg_daily_km     : weight 0.30
#   load_factor      : weight 0.20

def minmax(series: pd.Series) -> pd.Series:
    """Scale a series to [0, 1] using the observed min/max."""
    lo, hi = series.min(), series.max()
    return (series - lo) / (hi - lo)


df = df.copy()
df["norm_km_since_service"] = minmax(df["km_since_service"])
df["norm_avg_daily_km"]     = minmax(df["avg_daily_km"])
df["norm_load_factor"]      = minmax(df["load_factor"])

df["risk_score"] = (
    0.50 * df["norm_km_since_service"]
    + 0.30 * df["norm_avg_daily_km"]
    + 0.20 * df["norm_load_factor"]
) * 100

# ---------------------------------------------------------------------------
# Step 4 — Rank by risk and print the top 10
# ---------------------------------------------------------------------------

ranked = (
    df[["car_id", "km_since_service", "avg_daily_km", "load_factor", "risk_score", "broke_down"]]
    .sort_values("risk_score", ascending=False)
    .reset_index(drop=True)
)
ranked.index += 1   # rank starts at 1

print()
print("=" * 62)
print("Top 10 cars by breakdown risk")
print("=" * 62)
print(
    f"  {'Rank':<5}  {'Car':>10}  {'km_since_svc':>13}  "
    f"{'daily_km':>9}  {'load':>6}  {'risk':>6}  {'broke?':>7}"
)
print("  " + "-" * 60)
for rank, row in ranked.head(10).iterrows():
    broke_flag = "YES" if row["broke_down"] == 1 else "-"
    print(
        f"  {rank:<5}  {row['car_id']:>10}  {row['km_since_service']:>13.0f}  "
        f"{row['avg_daily_km']:>9.0f}  {row['load_factor']:>6.2f}  "
        f"{row['risk_score']:>6.1f}  {broke_flag:>7}"
    )

# How well does the score rank actual failures into the top quartile?
top_quartile = ranked.head(30)
precision = top_quartile["broke_down"].sum() / 30
print()
print(f"Of the top-30 highest-risk cars, {top_quartile['broke_down'].sum()} actually broke down")
print(f"  (precision in top quartile: {precision:.0%} vs {len(broke)/len(df):.0%} base rate)")
