import pandas as pd
import sqlite3

conn = sqlite3.connect("data/shopify_app_data.db")

df_apps = pd.read_sql("SELECT * FROM apps", conn)
df_app_categories = pd.read_sql("SELECT * FROM apps_categories", conn)
df_categories = pd.read_sql("SELECT * FROM categories", conn)
df_key_benefits = pd.read_sql("SELECT * FROM key_benefits", conn)
df_pricing_plans = pd.read_sql("SELECT * FROM pricing_plans", conn)
df_pricing_plan_features = pd.read_sql("SELECT * FROM pricing_plan_features", conn)
df_reviews = pd.read_sql("SELECT * FROM reviews", conn)

# Manipulate Data

# --- Apps DataFrame ---
# Convert Launch Date and Scraped At to Datetime
df_apps["launch_date"] = pd.to_datetime(df_apps["launch_date"])
df_apps["scraped_at"] = pd.to_datetime(df_apps["scraped_at"])

# Convert Rating to Float
df_apps["rating"] = pd.to_numeric(df_apps["rating"])

# --- Reviews DataFrame ---
# Convert Rating to Integer
df_reviews["rating"] = df_reviews["rating"].astype(int)

# Clean Posted At with "Edited" prefix and convert to Datetime
df_reviews["posted_at"] = (
    df_reviews["posted_at"].str.replace("Edited ", "", case=False).str.strip()
)
df_reviews["posted_at"] = pd.to_datetime(df_reviews["posted_at"])
df_reviews.sort_values(by="posted_at", ascending=True, inplace=True)

# --- Joins ---
df_apps_with_reviews = pd.merge(
    df_reviews, df_apps, left_on="app_id", right_on="id", how="left"
)
# Rename body column to review_body to avoid confusion
df_apps_with_reviews.rename(columns={"body": "review_body"}, inplace=True)


class ShopifyAppAnalyzerService:
    def data(self):
        return {
            "df_apps": df_apps,
            "df_app_categories": df_app_categories,
            "df_categories": df_categories,
            "df_key_benefits": df_key_benefits,
            "df_pricing_plan_features": df_pricing_plan_features,
            "df_reviews": df_reviews[df_reviews["rating"] < 3],
        }
