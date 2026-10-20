"""
eda_analysis.py — Exploratory Data Analysis of Retail Sales (2023–2024)

Loads a synthetic retail sales dataset (5,000 orders), computes a full
statistical summary, prints the key numbers used in EDA_Report.md, and
generates the report charts (navy/gold matplotlib style) in ./charts/.

Run:  python3 eda_analysis.py
Input: ../retail_sales.csv
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless-safe backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths and shared chart style
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "retail_sales.csv"
CHARTS_DIR = BASE_DIR / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

NAVY = "#1a2f5a"
GOLD = "#d4a017"
LIGHT = "#e8ecf3"
GREY = "#666666"

plt.rcParams.update(
    {
        "figure.figsize": (11, 6.2),
        "figure.dpi": 150,
        "axes.facecolor": "white",
        "axes.edgecolor": GREY,
        "axes.labelcolor": NAVY,
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "axes.titlecolor": NAVY,
        "axes.labelsize": 12,
        "xtick.color": GREY,
        "ytick.color": GREY,
        "font.size": 11,
    }
)


def style_ax(ax):
    """Apply the shared navy/gold look to an axis."""
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=LIGHT, linewidth=0.8)
    ax.set_axisbelow(True)
    return ax


def save(fig, name):
    path = CHARTS_DIR / name
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  chart saved: charts/{name}")


def money(x):
    return f"${x:,.0f}"


# ---------------------------------------------------------------------------
# 1. Load and basic overview
# ---------------------------------------------------------------------------
df = pd.read_csv(DATA_PATH, parse_dates=["OrderDate"])

print("=" * 72)
print("DATASET OVERVIEW")
print("=" * 72)
print(f"Rows: {len(df):,}   Columns: {df.shape[1]}")
print(f"Date range: {df['OrderDate'].min().date()} to {df['OrderDate'].max().date()}")
print(f"Columns: {', '.join(df.columns)}")
print(f"\nTotal Sales:  {money(df['Sales'].sum())}")
print(f"Total Profit: {money(df['Profit'].sum())}")
print(f"Overall profit margin: {df['Profit'].sum() / df['Sales'].sum() * 100:.1f}%")

# ---------------------------------------------------------------------------
# 2. Data quality checks
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("DATA QUALITY")
print("=" * 72)
missing = df.isna().sum()
print("Missing values per column:")
print(missing.to_string())
print(f"Duplicate OrderIDs: {df['OrderID'].duplicated().sum()}")
print(f"Duplicate full rows: {df.duplicated().sum()}")
print(f"Negative Sales rows: {(df['Sales'] < 0).sum()}")
print(f"Negative Profit rows: {(df['Profit'] < 0).sum()} "
      f"({(df['Profit'] < 0).mean() * 100:.2f}% of orders — loss-making orders)")
print(f"Discount range: {df['Discount'].min():.2f} – {df['Discount'].max():.2f}")
print(f"Quantity range: {df['Quantity'].min()} – {df['Quantity'].max()}")
# Consistency check: Sales should equal Quantity * UnitPrice * (1 - Discount)
expected = df["Quantity"] * df["UnitPrice"] * (1 - df["Discount"])
mismatch = (np.abs(expected - df["Sales"]) > 0.05).sum()
print(f"Rows where Sales != Qty x Price x (1-Discount): {mismatch}")

for col in ["Category", "Region", "Channel", "Segment"]:
    print(f"\n{col} values ({df[col].nunique()}): {sorted(df[col].unique())}")

# ---------------------------------------------------------------------------
# 3. Descriptive statistics
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("DESCRIPTIVE STATISTICS")
print("=" * 72)
stats_cols = ["Sales", "Profit", "Quantity", "UnitPrice", "Discount"]
desc = df[stats_cols].describe(percentiles=[0.25, 0.5, 0.75]).T
desc = desc[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
print(desc.round(2).to_string())

# ---------------------------------------------------------------------------
# 4. Group summaries (used by charts and insights)
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("GROUP SUMMARIES")
print("=" * 72)

cat = df.groupby("Category").agg(
    orders=("OrderID", "count"), sales=("Sales", "sum"), profit=("Profit", "sum")
)
cat["margin_%"] = cat["profit"] / cat["sales"] * 100
print("\nBy Category:")
print(cat.sort_values("sales", ascending=False).round(1).to_string())

chan = df.groupby("Channel").agg(
    orders=("OrderID", "count"), sales=("Sales", "sum"),
    profit=("Profit", "sum"), avg_order=("Sales", "mean"),
)
chan["margin_%"] = chan["profit"] / chan["sales"] * 100
print("\nBy Channel:")
print(chan.sort_values("sales", ascending=False).round(1).to_string())

reg = df.groupby("Region").agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
reg["margin_%"] = reg["profit"] / reg["sales"] * 100
print("\nBy Region:")
print(reg.sort_values("sales", ascending=False).round(1).to_string())

seg = df.groupby("Segment").agg(
    orders=("OrderID", "count"), sales=("Sales", "sum"), profit=("Profit", "sum")
)
print("\nBy Segment:")
print(seg.sort_values("sales", ascending=False).round(1).to_string())

top_products = (
    df.groupby("Product")["Sales"].sum().sort_values(ascending=False).head(5)
)
print("\nTop 5 products by sales:")
print(top_products.round(0).to_string())

# Monthly trend
monthly = df.set_index("OrderDate").resample("M")[["Sales", "Profit"]].sum()
monthly["margin_%"] = monthly["Profit"] / monthly["Sales"] * 100
print("\nMonthly sales (first / last / min / max):")
print(f"  First month: {monthly.index[0].strftime('%b %Y')}  {money(monthly['Sales'].iloc[0])}")
print(f"  Last month:  {monthly.index[-1].strftime('%b %Y')}  {money(monthly['Sales'].iloc[-1])}")
print(f"  Lowest:      {monthly['Sales'].idxmin().strftime('%b %Y')}  {money(monthly['Sales'].min())}")
print(f"  Highest:     {monthly['Sales'].idxmax().strftime('%b %Y')}  {money(monthly['Sales'].max())}")

h1_2023 = df[(df["OrderDate"] >= "2023-01-01") & (df["OrderDate"] < "2023-07-01")]["Sales"].sum()
h2_2024 = df[(df["OrderDate"] >= "2024-07-01") & (df["OrderDate"] < "2025-01-01")]["Sales"].sum()
print(f"  H1 2023 sales: {money(h1_2023)}   H2 2024 sales: {money(h2_2024)}   "
      f"change: {(h2_2024 / h1_2023 - 1) * 100:+.1f}%")

# Discount analysis — bin orders by discount level
bins = [-0.001, 0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 1.0]
labels = ["0%", "1–5%", "6–10%", "11–15%", "16–20%", "21–25%", "26%+"]
df["DiscountBand"] = pd.cut(df["Discount"], bins=bins, labels=labels)
disc = df.groupby("DiscountBand", observed=True).agg(
    orders=("OrderID", "count"), avg_profit=("Profit", "mean"),
    margin=("Profit", "sum"), sales=("Sales", "sum"),
)
disc["margin_%"] = disc["margin"] / disc["sales"] * 100
print("\nProfit by discount band:")
print(disc.round(1).to_string())
corr = df["Discount"].corr(df["Profit"])
print(f"\nCorrelation between Discount and Profit: {corr:.3f}")

high_disc = df[df["Discount"] >= 0.20]
print(f"Orders with discount >= 20%: {len(high_disc)} ({len(high_disc) / len(df) * 100:.1f}%)")
print(f"  their avg profit per order: ${high_disc['Profit'].mean():.2f}  |  "
      f"overall avg: ${df['Profit'].mean():.2f}")
print(f"  loss-making share among them: {(high_disc['Profit'] < 0).mean() * 100:.1f}%  |  "
      f"overall: {(df['Profit'] < 0).mean() * 100:.2f}%")

# ---------------------------------------------------------------------------
# 5. Charts
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("CHARTS")
print("=" * 72)

# 5.1 Sales distribution histogram
fig, ax = plt.subplots()
ax.hist(df["Sales"], bins=40, color=NAVY, edgecolor="white", linewidth=0.4)
ax.axvline(df["Sales"].mean(), color=GOLD, linewidth=2.2,
           label=f"Mean ${df['Sales'].mean():,.0f}")
ax.axvline(df["Sales"].median(), color=GREY, linestyle="--", linewidth=1.6,
           label=f"Median ${df['Sales'].median():,.0f}")
ax.set_title("Distribution of Order Sales")
ax.set_xlabel("Order value (USD)")
ax.set_ylabel("Number of orders")
ax.legend(frameon=False)
style_ax(ax)
save(fig, "sales_distribution.png")

# 5.2 Monthly sales trend
fig, ax = plt.subplots()
ax.plot(monthly.index, monthly["Sales"], color=NAVY, linewidth=2.4, marker="o",
        markersize=4, markerfacecolor=GOLD, markeredgecolor=NAVY)
ax.fill_between(monthly.index, monthly["Sales"], color=LIGHT)
ax.set_title("Monthly Sales Trend (Jan 2023 – Dec 2024)")
ax.set_xlabel("Month")
ax.set_ylabel("Sales (USD)")
ax.yaxis.set_major_formatter(lambda x, _: f"${x:,.0f}")
style_ax(ax)
save(fig, "monthly_trend.png")

# 5.3 Category comparison (sales + profit, sorted)
cat_sorted = cat.sort_values("sales")
fig, ax = plt.subplots()
y = np.arange(len(cat_sorted))
ax.barh(y - 0.2, cat_sorted["sales"], height=0.4, color=NAVY, label="Sales")
ax.barh(y + 0.2, cat_sorted["profit"], height=0.4, color=GOLD, label="Profit")
ax.set_yticks(y, cat_sorted.index)
ax.set_title("Sales vs Profit by Category")
ax.set_xlabel("USD")
ax.xaxis.set_major_formatter(lambda x, _: f"${x:,.0f}")
ax.legend(frameon=False)
style_ax(ax)
ax.grid(axis="x", color=LIGHT, linewidth=0.8)
ax.grid(axis="y", visible=False)
save(fig, "category_comparison.png")

# 5.4 Discount vs Profit scatter
fig, ax = plt.subplots()
ax.scatter(df["Discount"] * 100, df["Profit"], s=9, color=NAVY, alpha=0.35)
ax.axhline(0, color=GOLD, linewidth=1.8)
ax.set_title("Discount vs Profit per Order — deeper discounts, thinner profit")
ax.set_xlabel("Discount (%)")
ax.set_ylabel("Profit per order (USD)")
style_ax(ax)
save(fig, "discount_vs_profit.png")

# 5.5 Channel comparison (bonus chart)
chan_sorted = chan.sort_values("sales")
fig, ax = plt.subplots()
bars = ax.bar(chan_sorted.index, chan_sorted["sales"], color=[NAVY, GOLD, "#7f96c4"][: len(chan_sorted)], width=0.55)
ax.set_title("Total Sales by Channel")
ax.set_ylabel("Sales (USD)")
ax.yaxis.set_major_formatter(lambda x, _: f"${x:,.0f}")
for bar, val in zip(bars, chan_sorted["sales"]):
    ax.annotate(money(val), (bar.get_x() + bar.get_width() / 2, val),
                ha="center", va="bottom", fontsize=11, color=NAVY, fontweight="bold")
style_ax(ax)
save(fig, "channel_comparison.png")

print("\nDone. All statistics printed above feed EDA_Report.md.")
