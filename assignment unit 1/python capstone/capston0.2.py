
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import sys
from typing import Optional, Dict, List

# Configuration
DATA_FOLDER = Path("data")
CLEANED_OUTPUT = Path("cleaned_energy_data.csv")
BUILDING_SUMMARY_OUTPUT = Path("building_summary.csv")
DASHBOARD_PNG = Path("dashboard.png")
SUMMARY_TXT = Path("summary.txt")


def load_and_combine_data(data_folder: Path = DATA_FOLDER) -> Optional[pd.DataFrame]:
    """
    Reads all CSV files in `data_folder` and combines them into a single DataFrame.
    Each file's stem is added as a 'building' column.
    Returns combined DataFrame or None if no valid files found.
    """
    if not data_folder.exists() or not data_folder.is_dir():
        print(f"[ERROR] Data folder not found: {data_folder.resolve()}")
        return None

    csv_files = sorted(list(data_folder.glob("*.csv")))
    if not csv_files:
        print(f"[WARN] No CSV files found in {data_folder.resolve()}")
        return None

    frames = []
    for f in csv_files:
        try:
            temp = pd.read_csv(f)
            # Basic validation: required columns
            if "timestamp" not in temp.columns or "kwh" not in temp.columns:
                print(f"[WARN] File {f.name} missing required columns ('timestamp','kwh'). Skipping.")
                continue

            temp = temp.copy()
            temp["building"] = f.stem
            frames.append(temp)
            print(f"[INFO] Loaded: {f.name} ({len(temp)} rows)")

        except pd.errors.EmptyDataError:
            print(f"[WARN] Empty file: {f.name}. Skipping.")
        except Exception as e:
            print(f"[ERROR] Failed to read {f.name}: {e}")

    if not frames:
        print("[ERROR] No valid CSV data was loaded.")
        return None

    df = pd.concat(frames, ignore_index=True)
    # Normalize columns: convert timestamp to datetime, kwh to numeric
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["kwh"] = pd.to_numeric(df["kwh"], errors="coerce")

    # Drop rows where timestamp or kwh is NaN after conversion
    before = len(df)
    df = df.dropna(subset=["timestamp", "kwh"])
    after = len(df)
    dropped = before - after
    if dropped:
        print(f"[INFO] Dropped {dropped} rows with invalid timestamps or kwh values.")

    # Sort by timestamp for convenience
    df = df.sort_values("timestamp").reset_index(drop=True)
    print(f"[INFO] Combined DataFrame shape: {df.shape}")

    return df


def collect_user_input() -> pd.DataFrame:
    """
    Interactively collect building meter entries from the user.
    Returns a DataFrame with columns: timestamp, kwh, building
    """

    rows = []
    print("\n=== USER DATA ENTRY MODE ===")
    print("Enter building data manually. Type 'done' anytime to stop.")

    while True:
        building = input("Enter building name (or 'done'): ").strip()
        if building.lower() == "done":
            break

        timestamp = input("Enter timestamp (YYYY-MM-DD HH:MM) [or 'done']: ").strip()
        if timestamp.lower() == "done":
            break

        kwh = input("Enter kWh value: ").strip()
        if kwh.lower() == "done":
            break

        # validate kwh
        try:
            kwh_val = float(kwh)
        except ValueError:
            print("[WARN] kWh must be a numeric value (e.g. 123.45). Row skipped.")
            print("-----------------------")
            continue

        # parse timestamp if possible
        try:
            ts = pd.to_datetime(timestamp)
        except Exception:
            ts = timestamp

        rows.append({"timestamp": ts, "kwh": kwh_val, "building": building})
        print("[Added]")
        print("-----------------------")

    if rows:
        df_user = pd.DataFrame(rows)
        try:
            df_user["timestamp"] = pd.to_datetime(df_user["timestamp"])
        except Exception:
            pass
        print(f"\n[INFO] User entered {len(df_user)} rows.")
        return df_user

    print("[INFO] No user data entered.")
    return pd.DataFrame(columns=["timestamp", "kwh", "building"])


def calculate_daily_totals(df: pd.DataFrame) -> pd.Series:
    df_local = df.copy()
    df_local["timestamp"] = pd.to_datetime(df_local["timestamp"])
    df_local = df_local.set_index("timestamp")
    daily = df_local["kwh"].resample("D").sum()
    return daily


def calculate_weekly_aggregates(df: pd.DataFrame) -> pd.Series:
    df_local = df.copy()
    df_local["timestamp"] = pd.to_datetime(df_local["timestamp"])
    df_local = df_local.set_index("timestamp")
    weekly = df_local["kwh"].resample("W").sum()
    return weekly


def building_wise_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby("building")["kwh"].agg(
        mean="mean", min="min", max="max", total_kwh="sum"
    ).sort_values("total_kwh", ascending=False)
    return summary


class MeterReading:
    def __init__(self, timestamp, kwh: float):
        self.timestamp = pd.to_datetime(timestamp)
        self.kwh = float(kwh)

    def __repr__(self):
        return f"MeterReading({self.timestamp}, {self.kwh})"


class Building:
    def __init__(self, name: str):
        self.name = name
        self.meter_readings: List[MeterReading] = []

    def add_reading(self, reading: MeterReading):
        self.meter_readings.append(reading)

    def calculate_total_consumption(self) -> float:
        return sum(r.kwh for r in self.meter_readings)

    def to_report(self) -> str:
        total = self.calculate_total_consumption()
        count = len(self.meter_readings)
        return f"Building {self.name}: {total:.2f} kWh over {count} readings"


class BuildingManager:
    def __init__(self):
        self.buildings: Dict[str, Building] = {}

    def load_from_dataframe(self, df: pd.DataFrame):
        for _, row in df.iterrows():
            bname = row["building"]
            if bname not in self.buildings:
                self.buildings[bname] = Building(bname)
            self.buildings[bname].add_reading(MeterReading(row["timestamp"], row["kwh"]))

    def summary_totals(self) -> Dict[str, float]:
        return {name: b.calculate_total_consumption() for name, b in self.buildings.items()}


def plot_line(ax, daily_series: pd.Series):
    ax.plot(daily_series.index, daily_series.values)
    ax.set_title("Daily Electricity Consumption")
    ax.set_xlabel("Date")
    ax.set_ylabel("kWh")


def plot_bar(ax, building_summary: pd.DataFrame):
    ax.bar(building_summary.index, building_summary["total_kwh"])
    ax.set_title("Total Consumption per Building")
    ax.set_xlabel("Building")
    ax.set_ylabel("kWh")
    ax.tick_params(axis="x", rotation=45)


def plot_scatter(ax, df: pd.DataFrame):
    # Make sure timestamp is datetime
    df_local = df.copy()
    df_local["timestamp"] = pd.to_datetime(df_local["timestamp"])
    ax.scatter(df_local["timestamp"], df_local["kwh"], s=6)
    ax.set_title("Individual Meter Readings (kWh over time)")
    ax.set_xlabel("Time")
    ax.set_ylabel("kWh")


def create_dashboard(daily: pd.Series, building_summary: pd.DataFrame, df: pd.DataFrame, out_png: Path = DASHBOARD_PNG):
    fig, axs = plt.subplots(2, 2, figsize=(14, 9))

    # Top-left: Line (daily)
    plot_line(axs[0, 0], daily)
    # Top-right: empty or summary text
    axs[0, 1].axis("off")
    txt = f"Total buildings: {len(building_summary)}\nStart: {daily.index.min().date() if len(daily)>0 else 'N/A'}\nEnd: {daily.index.max().date() if len(daily)>0 else 'N/A'}"
    axs[0, 1].text(0.05, 0.5, txt, fontsize=12, va="center")

    # Bottom-left: Bar
    plot_bar(axs[1, 0], building_summary)

    # Bottom-right: Scatter
    plot_scatter(axs[1, 1], df)

    plt.tight_layout()
    plt.savefig(out_png)
    plt.close(fig)
    print(f"[INFO] Dashboard saved to {out_png.resolve()}")


def save_outputs(df: pd.DataFrame, building_summary: pd.DataFrame):
    df.to_csv(CLEANED_OUTPUT, index=False)
    building_summary.to_csv(BUILDING_SUMMARY_OUTPUT)
    print(f"[INFO] Cleaned data saved to {CLEANED_OUTPUT.resolve()}")
    print(f"[INFO] Building summary saved to {BUILDING_SUMMARY_OUTPUT.resolve()}")


def create_summary_file(df: pd.DataFrame, building_summary: pd.DataFrame, out_txt: Path = SUMMARY_TXT):
    total_consumption = float(df["kwh"].sum())
    if not building_summary.empty:
        top_building = building_summary["total_kwh"].idxmax()
        top_value = float(building_summary["total_kwh"].max())
    else:
        top_building = "N/A"
        top_value = 0.0

    if not df.empty:
        peak_idx = df["kwh"].idxmax()
        peak_time = pd.to_datetime(df.loc[peak_idx, "timestamp"])
        peak_value = float(df.loc[peak_idx, "kwh"])
    else:
        peak_time = "N/A"
        peak_value = 0.0

    daily = calculate_daily_totals(df) if not df.empty else pd.Series(dtype=float)
    weekly = calculate_weekly_aggregates(df) if not df.empty else pd.Series(dtype=float)

    insights = []
    if not daily.empty:
        largest_day = daily.idxmax().date()
        insights.append(f"Day with highest consumption: {largest_day} ({daily.max():.2f} kWh)")
    if not weekly.empty:
        largest_week = weekly.idxmax().date()
        insights.append(f"Week with highest consumption ending on: {largest_week} ({weekly.max():.2f} kWh)")

    report_lines = [
        "Campus Energy Consumption Report",
        "----------------------------------------",
        f"Total Campus Consumption: {total_consumption:.2f} kWh",
        "",
        "Highest Consuming Building:",
        f"- {top_building}: {top_value:.2f} kWh",
        "",
        "Peak Load:",
        f"- Timestamp: {peak_time}",
        f"- kWh: {peak_value:.2f}",
        "",
        "Insights:",
    ]
    report_lines.extend([f"- {s}" for s in insights])
    report_lines.append("")
    report_lines.append(f"Dashboard file: {DASHBOARD_PNG.resolve()}")
    report_lines.append(f"Cleaned data file: {CLEANED_OUTPUT.resolve()}")
    report_lines.append(f"Building summary file: {BUILDING_SUMMARY_OUTPUT.resolve()}")

    out_txt.write_text("\n".join(report_lines))
    print(f"[INFO] Summary report written to {out_txt.resolve()}")


def main(data_folder: Path = DATA_FOLDER):
    print("[START] Campus Energy Dashboard pipeline")

    # 1) CSV ingestion
    df_csv = load_and_combine_data(data_folder)

    # 2) Optionally collect user-entered rows and merge
    add_manual = input("Would you like to add manual entries? (y/N): ").strip().lower()
    if add_manual == "y":
        df_user = collect_user_input()
    else:
        df_user = pd.DataFrame(columns=["timestamp", "kwh", "building"])

    # Combine both sources (CSV + user entries)
    if df_csv is not None and not df_csv.empty:
        if not df_user.empty:
            df = pd.concat([df_csv, df_user], ignore_index=True)
        else:
            df = df_csv
    else:
        df = df_user

    if df is None or df.empty:
        print("[ERROR] No data to process (CSV and/or user input). Exiting.")
        return

    print(f"[INFO] Final dataset size after merging: {df.shape}\n")

    # Aggregations
    daily = calculate_daily_totals(df)
    weekly = calculate_weekly_aggregates(df)
    summary = building_wise_summary(df)

    # OOP (optional)
    manager = BuildingManager()
    manager.load_from_dataframe(df)

    # Save outputs
    save_outputs(df, summary)

    # Create dashboard
    create_dashboard(daily, summary, df)

    # Create text summary
    create_summary_file(df, summary)

    print("[DONE] All outputs created successfully.")


if __name__ == "__main__":
    folder_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_FOLDER
    main(folder_arg)
