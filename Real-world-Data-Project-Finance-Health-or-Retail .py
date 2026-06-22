import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set global plotting style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# ==========================================
# 1. GENERATE REALISTIC RETAIL TRANSACTION DATA
# ==========================================
print("--- Step 1: Generating Retail Transaction Dataset ---")
np.random.seed(42)
n_transactions = 5000
n_customers = 400

# Generate synthetic customer base
customer_ids = [f"CS-{i:04d}" for i in range(1, n_customers + 1)]

# Generate realistic transaction records
data = {
    "Invoice_ID": [f"INV-{i:05d}" for i in range(1, n_transactions + 1)],
    "Customer_ID": np.random.choice(customer_ids, size=n_transactions),
    "Invoice_Date": pd.date_range(
        start="2025-01-01", end="2026-06-01", periods=n_transactions
    ),
    "Product_Category": np.random.choice(
        ["Apparel", "Electronics", "Home & Kitchen", "Beauty"],
        size=n_transactions,
        p=[0.4, 0.2, 0.2, 0.2],
    ),
    "Quantity": np.random.choice(
        [1, 2, 3, 4, 5], size=n_transactions, p=[0.5, 0.3, 0.1, 0.06, 0.04]
    ),
    "Unit_Price": np.random.uniform(10.0, 250.0, size=n_transactions),
}

df = pd.DataFrame(data)
df["Total_Spend"] = df["Quantity"] * df["Unit_Price"]

print(f"Generated {df.shape[0]} retail transactions for {n_customers} unique customers.\n")


# ==========================================
# 2. RFM (RECENCY, FREQUENCY, MONETARY) ANALYSIS
# ==========================================
print("--- Step 2: Calculating RFM Metrics ---")

# Set the snapshot date to one day after the final invoice to calculate recency
snapshot_date = df["Invoice_Date"].max() + pd.Timedelta(days=1)

# Aggregate transaction data by customer
rfm = df.groupby("Customer_ID").agg(
    {
        "Invoice_Date": lambda x: (snapshot_date - x.max()).days,  # Recency
        "Invoice_ID": "count",  # Frequency
        "Total_Spend": "sum",  # Monetary Value
    }
)

# Rename the columns
rfm.rename(
    columns={
        "Invoice_Date": "Recency",
        "Invoice_ID": "Frequency",
        "Total_Spend": "Monetary",
    },
    inplace=True,
)


# ==========================================
# 3. CUSTOMER SEGMENTATION
# ==========================================
print("--- Step 3: Segmenting Customers ---")

# Create quintile scores (1 to 5) for RFM metrics
# For Recency, a lower number is better (more recent), so labels are inverted
rfm["R_Score"] = pd.qcut(rfm["Recency"], q=5, labels=[5, 4, 3, 2, 1])
rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]
)
rfm["M_Score"] = pd.qcut(rfm["Monetary"], q=5, labels=[1, 2, 3, 4, 5])


# Define a function to group customers based on their RFM scores
def segment_customer(df_row):
    r = df_row["R_Score"]
    f = df_row["F_Score"]
    m = df_row["M_Score"]

    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3:
        return "Loyal Customers"
    elif r >= 4 and f <= 2:
        return "Recent & New"
    elif r <= 2 and f >= 3:
        return "At Risk"
    elif r <= 2 and f <= 2:
        return "Lost / Hibernating"
    else:
        return "Average Regulars"


rfm["Customer_Segment"] = rfm.apply(segment_customer, axis=1)
print(rfm["Customer_Segment"].value_counts())
print("\n")


# ==========================================
# 4. VISUALIZATION & REPORTING
# ==========================================
print("--- Step 4: Generating Retail Insights Visualizations ---")

# Create output directory
os.makedirs("retail_plots", exist_ok=True)

# Plot 1: Customer Segment Distribution
plt.figure()
segment_counts = rfm["Customer_Segment"].value_counts().sort_values()
segment_counts.plot(kind="barh", color="indigo", edgecolor="black")
plt.title("Customer Base Distribution by Segment", fontsize=14, pad=15)
plt.xlabel("Number of Customers")
plt.ylabel("Segment")
plt.tight_layout()
plt.savefig("retail_plots/1_customer_segments.png")
plt.close()

# Plot 2: RFM Scatter Analysis (Value vs. Frequency Matrix)
plt.figure()
sns.scatterplot(
    data=rfm,
    x="Frequency",
    y="Monetary",
    hue="Customer_Segment",
    palette="Dark2",
    size="Recency",
    sizes=(20, 200),
    alpha=0.7,
)
plt.title("Customer Value Matrix (Frequency vs. Monetary)", fontsize=14, pad=15)
plt.xlabel("Purchase Frequency (Total Count)")
plt.ylabel("Total Monetary Value ($)")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", title="Segments")
plt.tight_layout()
plt.savefig("retail_plots/2_rfm_value_matrix.png")
plt.close()

# Plot 3: Monthly Revenue Trajectory
plt.figure()
df.set_index("Invoice_Date").resample("ME")["Total_Spend"].sum().plot(
    marker="o", color="crimson", linewidth=2.5
)
plt.title("Monthly Revenue Trajectory Trailing 18 Months", fontsize=14, pad=15)
plt.xlabel("Timeline")
plt.ylabel("Gross Sales Revenue ($)")
plt.tight_layout()
plt.savefig("retail_plots/3_monthly_sales_trend.png")
plt.close()

print(
    "🎉 Retail analytics complete! High-impact visual assets saved to '/retail_plots'."
)
