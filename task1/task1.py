"""
British Airways Data Science (Forage) - Task 1
Builds a lounge eligibility lookup table (% of passengers per tier) by flight grouping.
"""

from pathlib import Path

import pandas as pd


HERE = Path(__file__).parent
DATA_FILE = next(HERE.glob("British*Schedule*.xlsx"))  
OUTPUT_FILE = HERE / "lounge_eligibility_lookup.xlsx"

TIERS = ["TIER1_ELIGIBLE_PAX", "TIER2_ELIGIBLE_PAX", "TIER3_ELIGIBLE_PAX"]
FINAL_GROUPING = ["HAUL", "ARRIVAL_REGION"]  

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)
    print(f"Loaded {len(df):,} flights, {df.shape[1]} columns\n")
    print(df.head(), "\n")
    for col in ["TIME_OF_DAY", "HAUL", "ARRIVAL_REGION", "ARRIVAL_STATION_CD"]:
        print(df[col].value_counts(), "\n")
    return df

# Assumes flights are full (no load factor in the data)
def add_total_seats(df: pd.DataFrame) -> pd.DataFrame:
    df["TOTAL_SEATS"] = (
        df["FIRST_CLASS_SEATS"] + df["BUSINESS_CLASS_SEATS"] + df["ECONOMY_SEATS"]
    )
    return df

def eligibility(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    g = df.groupby(group_cols)[TIERS + ["TOTAL_SEATS"]].sum()
    pct = g[TIERS].div(g["TOTAL_SEATS"], axis=0) * 100
    pct.columns = ["Tier 1 %", "Tier 2 %", "Tier 3 %"]
    pct["Flights"] = df.groupby(group_cols).size()
    return pct.round(1)

def compare_groupings(df: pd.DataFrame) -> None:
    candidates = [
        ["HAUL"],
        ["HAUL", "ARRIVAL_REGION"],
        ["HAUL", "TIME_OF_DAY"],
        ["HAUL", "ARRIVAL_REGION", "TIME_OF_DAY"],
    ]
    for cols in candidates:
        print(f"=== Grouping: {' + '.join(cols)} ===")
        print(eligibility(df, cols), "\n")


def build_lookup(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    table = eligibility(df, group_cols)
    destinations = df.groupby(group_cols)["ARRIVAL_STATION_CD"].apply(
        lambda s: ", ".join(sorted(s.unique()))
    )
    table.insert(0, "Example Destinations", destinations)
    table = table.reset_index()
    table.insert(0, "Grouping", table[group_cols].astype(str).agg(" - ".join, axis=1))
    return table.drop(columns=group_cols)


def main() -> None:
    df = load_data(DATA_FILE)
    df = add_total_seats(df)
    compare_groupings(df)

    lookup = build_lookup(df, FINAL_GROUPING)
    print("=== FINAL LOOKUP TABLE ===")
    print(lookup.to_string(index=False))
    lookup.to_excel(OUTPUT_FILE, index=False)
    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()