"""
Exploratory Data Analysis for LeniGuide cave records using pandas.
Analyzes site distribution, religious traditions, and visit duration patterns.
"""

import sys
from pathlib import Path
import pandas as pd
import json

# Ensure project root is in path
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def load_records_as_dataframe() -> pd.DataFrame:
    """
    Load cave records into a pandas DataFrame.
    
    Returns:
        DataFrame with all cave records
    """
    # Try loading from records.json first, fallback to sample_records.json
    records_path = project_root / "data" / "records.json"
    sample_path = project_root / "data" / "sample_records.json"
    
    if records_path.exists():
        print(f"✓ Loading from: {records_path.name}")
        df = pd.read_json(records_path)
    elif sample_path.exists():
        print(f"✓ Loading from: {sample_path.name}")
        df = pd.read_json(sample_path)
    else:
        raise FileNotFoundError("No records file found (records.json or sample_records.json)")
    
    return df


def analyze_site_distribution(df: pd.DataFrame) -> None:
    """
    Analyze and print cave distribution by site (Ajanta vs Ellora).
    
    Args:
        df: DataFrame with cave records
    """
    print("\n" + "=" * 80)
    print("FACT 1: SITE DISTRIBUTION")
    print("=" * 80)
    
    # Count caves by site
    site_counts = df["site"].value_counts()
    total_caves = len(df)
    
    print(f"\nTotal Caves: {total_caves}")
    print("-" * 80)
    
    for site, count in site_counts.items():
        percentage = (count / total_caves) * 100
        print(f"  {site:.<20} {count:>3} caves ({percentage:>5.1f}%)")
    
    # Additional insights
    print(f"\n📊 Analysis:")
    ajanta_count = site_counts.get("Ajanta", 0)
    ellora_count = site_counts.get("Ellora", 0)
    
    if ellora_count > ajanta_count:
        ratio = ellora_count / ajanta_count if ajanta_count > 0 else 0
        print(f"  • Ellora has {ellora_count - ajanta_count} more caves than Ajanta")
        print(f"  • Ellora-to-Ajanta ratio: {ratio:.2f}:1")
    
    print(f"  • Ajanta represents {(ajanta_count/total_caves)*100:.0f}% of documented caves")
    print(f"  • Ellora represents {(ellora_count/total_caves)*100:.0f}% of documented caves")


def analyze_religious_traditions(df: pd.DataFrame) -> None:
    """
    Analyze religious tradition breakdown across sites.
    
    Args:
        df: DataFrame with cave records
    """
    print("\n" + "=" * 80)
    print("FACT 2: RELIGIOUS TRADITION BREAKDOWN")
    print("=" * 80)
    
    # Extract primary religion from religion_period field
    def extract_religion(religion_period: str) -> str:
        """Extract main religion from religion_period string."""
        if pd.isna(religion_period):
            return "Unknown"
        
        religion_period = str(religion_period)
        if "Buddhist" in religion_period:
            return "Buddhist"
        elif "Hindu" in religion_period:
            return "Hindu"
        elif "Jain" in religion_period:
            return "Jain"
        else:
            return "Other"
    
    # Create tradition column
    df["tradition"] = df["religion_period"].apply(extract_religion)
    
    # Overall tradition counts
    print("\n🕉️  Overall Religious Distribution:")
    print("-" * 80)
    tradition_counts = df["tradition"].value_counts()
    total = len(df)
    
    for tradition, count in tradition_counts.items():
        percentage = (count / total) * 100
        print(f"  {tradition:.<20} {count:>3} caves ({percentage:>5.1f}%)")
    
    # Tradition by site (cross-tabulation)
    print("\n🏛️  Religious Traditions by Site:")
    print("-" * 80)
    
    site_tradition = df.groupby(["site", "tradition"]).size().unstack(fill_value=0)
    print(site_tradition.to_string())
    
    # Insights
    print(f"\n📊 Analysis:")
    
    # Buddhist caves
    buddhist_by_site = df[df["tradition"] == "Buddhist"].groupby("site").size()
    if "Ajanta" in buddhist_by_site.index:
        print(f"  • Ajanta has {buddhist_by_site['Ajanta']} Buddhist caves (primary focus)")
    
    # Hindu caves
    hindu_by_site = df[df["tradition"] == "Hindu"].groupby("site").size()
    if "Ellora" in hindu_by_site.index:
        print(f"  • Ellora has {hindu_by_site['Ellora']} Hindu caves (including Kailasa Temple)")
    
    # Jain caves
    jain_by_site = df[df["tradition"] == "Jain"].groupby("site").size()
    if "Ellora" in jain_by_site.index:
        print(f"  • Ellora has {jain_by_site['Ellora']} Jain caves (later period)")
    
    # Diversity
    ellora_traditions = df[df["site"] == "Ellora"]["tradition"].nunique()
    print(f"  • Ellora showcases {ellora_traditions} different religious traditions")
    print(f"  • This demonstrates religious harmony in ancient India")


def analyze_visit_duration(df: pd.DataFrame) -> None:
    """
    Analyze visit duration and must-see cave patterns.
    
    Args:
        df: DataFrame with cave records
    """
    print("\n" + "=" * 80)
    print("FACT 3: VISIT DURATION & MUST-SEE ROUTE ANALYSIS")
    print("=" * 80)
    
    # Extract visit duration from visit_info field
    # Pattern: "Estimated time: 45 minutes" or "45 minutes"
    df["duration_mins"] = df["visit_info"].str.extract(r'(\d+)\s*min', expand=False).astype(float)
    
    # Identify must-see caves
    df["is_must_see"] = df["visit_info"].str.contains("Must-see", case=False, na=False)
    
    # Duration statistics by site
    print("\n⏱️  Visit Duration Statistics by Site:")
    print("-" * 80)
    
    duration_stats = df.groupby("site")["duration_mins"].agg([
        ("count", "count"),
        ("total_mins", "sum"),
        ("avg_mins", "mean"),
        ("min_mins", "min"),
        ("max_mins", "max")
    ])
    
    for site in duration_stats.index:
        stats = duration_stats.loc[site]
        print(f"\n  {site}:")
        print(f"    Caves with timing data:  {int(stats['count'])}")
        print(f"    Total visit time:        {int(stats['total_mins'])} minutes ({stats['total_mins']/60:.1f} hours)")
        print(f"    Average per cave:        {stats['avg_mins']:.0f} minutes")
        print(f"    Quickest cave:           {int(stats['min_mins'])} minutes")
        print(f"    Longest cave:            {int(stats['max_mins'])} minutes")
    
    # Must-see caves analysis
    print("\n⭐ Must-See (Top 5) Caves:")
    print("-" * 80)
    
    must_see_caves = df[df["is_must_see"] == True]
    must_see_by_site = must_see_caves.groupby("site").size()
    
    print(f"  Total Must-See caves: {len(must_see_caves)}")
    for site, count in must_see_by_site.items():
        print(f"    {site}: {count} caves")
    
    # List must-see caves with durations
    print(f"\n  Must-See Cave Details:")
    for idx, row in must_see_caves.iterrows():
        duration = int(row["duration_mins"]) if pd.notna(row["duration_mins"]) else "N/A"
        print(f"    • {row['site']} Cave {row['cave_no']:>3} - {duration} mins - {row['religion_period']}")
    
    # Route planning insights
    print(f"\n📊 Route Planning Analysis:")
    
    total_duration = df["duration_mins"].sum()
    must_see_duration = must_see_caves["duration_mins"].sum()
    
    print(f"  • Total time for all 20 caves: {int(total_duration)} mins ({total_duration/60:.1f} hours)")
    print(f"  • Total time for Top 5 must-see: {int(must_see_duration)} mins ({must_see_duration/60:.1f} hours)")
    print(f"  • Time saved by focusing on must-see: {int(total_duration - must_see_duration)} mins")
    
    # Per-site must-see duration
    for site in must_see_by_site.index:
        site_must_see = must_see_caves[must_see_caves["site"] == site]
        site_duration = site_must_see["duration_mins"].sum()
        print(f"  • {site} must-see caves: {int(site_duration)} mins ({site_duration/60:.1f} hours)")
    
    # Recommendations
    print(f"\n💡 Recommendation for Teachers:")
    print(f"  • For a 2-day tour with 40 students:")
    print(f"    - Day 1: Ajanta (closed Mondays) - Focus on {int(must_see_by_site.get('Ajanta', 0))} must-see caves")
    print(f"    - Day 2: Ellora (closed Tuesdays) - Focus on {int(must_see_by_site.get('Ellora', 0))} must-see caves")
    print(f"  • Budget time: {must_see_duration/60:.1f} hours for must-see caves + breaks")


def main():
    """Main entry point for exploratory data analysis."""
    print("=" * 80)
    print("LENIGUIDE - EXPLORATORY DATA ANALYSIS WITH PANDAS")
    print("Student: Tanmay Subhash Gawali (SJ-52)")
    print("=" * 80)
    
    try:
        # Load data
        df = load_records_as_dataframe()
        print(f"✓ Loaded {len(df)} cave records")
        print(f"✓ Columns: {', '.join(df.columns)}")
        
        # Run analyses
        analyze_site_distribution(df)
        analyze_religious_traditions(df)
        analyze_visit_duration(df)
        
        print("\n" + "=" * 80)
        print("EXPLORATORY ANALYSIS COMPLETE")
        print("=" * 80)
        print("\n📊 Key Takeaways:")
        print("  1. Ellora has more documented caves (60%) than Ajanta (40%)")
        print("  2. Ellora showcases 3 religions; Ajanta is primarily Buddhist")
        print("  3. Must-see caves require ~3-4 hours total, ideal for school tours")
        print("\n" + "=" * 80)
    
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("  Run 'python -m app.ingest' first to generate records.json")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
