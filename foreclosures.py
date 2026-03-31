"""
Maryland Foreclosure Notice Analysis (2021-2026)
Usage: python maryland_foreclosure_analysis.py
Requires: pandas matplotlib seaborn
"""
 
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
 
#config
DATA_FILE = "Maryland_Foreclosure_Notice_Data_by_County.csv"
 
INTENT = "Notice of Intent to Foreclose"
FC     = "Notice of Foreclosure"
REG    = "Foreclosure Property Registration"
 
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#f8f8f8",
    "axes.grid": True,
    "grid.color": "#e0e0e0",
    "grid.linewidth": 0.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
})
 
 
# Load data
df = pd.read_csv(DATA_FILE)
 
county_cols = [c for c in df.columns if c not in ["Date", "Type", "(blank)"]]
for col in county_cols:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")
 
df["Date"]  = pd.to_datetime(df["Date"], format="%Y %b %d %I:%M:%S %p", errors="coerce")
df["Year"]  = df["Date"].dt.year
df["Month"] = df["Date"].dt.to_period("M")
df["Total"] = df[county_cols].sum(axis=1)
 
intent = df[df["Type"] == INTENT].copy()
fc     = df[df["Type"] == FC].copy()
reg    = df[df["Type"] == REG].copy()
 
intent_m = intent.groupby("Month")["Total"].sum()
fc_m     = fc.groupby("Month")["Total"].sum()
reg_m    = reg.groupby("Month")["Total"].sum()
 
print("=" * 55)
print("MARYLAND FORECLOSURE NOTICE ANALYSIS")
print("=" * 55)
print(f"Period: {df['Date'].min().date()} to {df['Date'].max().date()}")
print(f"\nTotal intent filings:   {intent['Total'].sum():>10,.0f}")
print(f"Total foreclosures:     {fc['Total'].sum():>10,.0f}")
print(f"Total registrations:    {reg['Total'].sum():>10,.0f}")
print(f"Overall conversion rate:{fc['Total'].sum()/intent['Total'].sum()*100:>9.1f}%")
 
annual = intent[intent["Year"] < 2026].groupby("Year")["Total"].sum()
print("\nAnnual intent filings:")
for year, total in annual.items():
    yoy = f"  (+{(total/annual.get(year-1,total)-1)*100:.1f}%)" if year > annual.index[0] else ""
    print(f"  {year}: {total:>7,.0f}{yoy}")
 
print(f"\nPeak month (intent):     {intent_m.idxmax()} — {int(intent_m.max()):,}")
print(f"Peak month (FC notice):  {fc_m.idxmax()} — {int(fc_m.max()):,}")
 
county_totals = intent[county_cols].sum().sort_values(ascending=False)
print("\nTop 5 counties (intent filings):")
for county, val in county_totals.head(5).items():
    print(f"  {county:<30} {val:>8,.0f}  ({val/intent['Total'].sum()*100:.1f}%)")
print("=" * 55)
 
 
#Plot 1: Monthly trends 
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
fig.suptitle("Maryland Foreclosure Filings — Monthly (Jul 2021 – Feb 2026)",
             fontsize=14, fontweight="bold", y=1.01)
 
for ax, (series, color, label) in zip(axes, [
    (intent_m, "#1f6fad", INTENT),
    (fc_m,     "#c04e28", FC),
    (reg_m,    "#1a7a57", REG),
]):
    x = range(len(series))
    ax.fill_between(x, series.values, alpha=0.15, color=color)
    ax.plot(x, series.values, color=color, linewidth=2)
    ax.set_title(label, fontsize=11, color=color)
    ax.set_ylabel("Filings", fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ticks = list(range(0, len(series), 6))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(series.index[i]) for i in ticks], rotation=30, ha="right", fontsize=9)
 
plt.tight_layout()
plt.savefig("monthly_trends.png", dpi=150, bbox_inches="tight")
print("\nSaved: monthly_trends.png")
 
 
# Annual bar chart
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(annual.index, annual.values, color="#1f6fad", width=0.6, zorder=3)
 
for bar, val in zip(bars, annual.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 800,
            f"{int(val):,}", ha="center", va="bottom", fontsize=11,
            fontweight="bold", color="#1f6fad")
 
for year, pct in annual.pct_change().iloc[1:].items():
    ax.text(year, annual[year] / 2, f"+{pct*100:.1f}%",
            ha="center", va="center", fontsize=10, color="white", fontweight="bold")
 
ax.set_title("Annual notice of intent filings (full years only)")
ax.set_ylabel("Total filings")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.set_ylim(0, annual.max() * 1.15)
plt.tight_layout()
plt.savefig("annual_intent.png", dpi=150, bbox_inches="tight")
print("Saved: annual_intent.png")
 
 
#Conversion rate
combined = pd.DataFrame({"intent": intent_m, "fc": fc_m}).dropna()
combined["rate"] = combined["fc"] / combined["intent"] * 100
 
fig, ax = plt.subplots(figsize=(14, 5))
x = range(len(combined))
ax.fill_between(x, combined["rate"].values, alpha=0.15, color="#8e44ad")
ax.plot(x, combined["rate"].values, color="#8e44ad", linewidth=2)
ax.axhline(combined["rate"].mean(), color="#555", linewidth=1, linestyle="--",
           label=f"Mean: {combined['rate'].mean():.1f}%")
ticks = list(range(0, len(combined), 6))
ax.set_xticks(ticks)
ax.set_xticklabels([str(combined.index[i]) for i in ticks], rotation=30, ha="right", fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
ax.set_title("Monthly conversion rate: foreclosure notice / intent to foreclose")
ax.set_ylabel("Conversion rate")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig("conversion_rate.png", dpi=150, bbox_inches="tight")
print("Saved: conversion_rate.png")
 
 
#County horizontal bar
county_asc = county_totals.sort_values(ascending=True)
short = [n.replace(" County", "") for n in county_asc.index]
 
fig, ax = plt.subplots(figsize=(10, 9))
colors = ["#c04e28" if v == county_asc.max() else "#1f6fad" for v in county_asc.values]
ax.barh(short, county_asc.values, color=colors, height=0.7, zorder=3)
 
for i, val in enumerate(county_asc.values):
    ax.text(val + 400, i, f"{int(val):,}", va="center", fontsize=9)
 
ax.set_title("Total intent-to-foreclose filings by county (Jul 2021 – Feb 2026)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.set_xlabel("Total filings")
plt.tight_layout()
plt.savefig("county_totals.png", dpi=150, bbox_inches="tight")
print("Saved: county_totals.png")
 
 
#Heatmap top 10 counties
top10 = intent[county_cols].sum().nlargest(10).index.tolist()
pivot = intent.pivot_table(index="Month", values=top10, aggfunc="sum")
pivot.index = pivot.index.astype(str)
pivot.columns = [c.replace(" County", "") for c in pivot.columns]
 
fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(pivot.T, ax=ax, cmap="YlOrRd", linewidths=0.3, linecolor="#eee",
            cbar_kws={"label": "Monthly filings"})
ax.set_title("Monthly intent filings — top 10 counties")
ax.set_xlabel("Month")
ax.set_ylabel("")
step = max(1, len(pivot) // 10)
ticks = list(range(0, len(pivot), step))
ax.set_xticks(ticks)
ax.set_xticklabels([pivot.index[i] for i in ticks], rotation=45, ha="right", fontsize=9)
plt.tight_layout()
plt.savefig("county_heatmap.png", dpi=150, bbox_inches="tight")
print("Saved: county_heatmap.png")
