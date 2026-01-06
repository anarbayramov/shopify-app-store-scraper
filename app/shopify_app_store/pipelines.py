# -*- coding: utf-8 -*-
import pandas as pd
import os
from .items import (
    App,
    KeyBenefit,
    PricingPlan,
    PricingPlanFeature,
    Category,
    AppCategory,
    AppReview,
)


class PandasRelationalPipeline(object):
    def open_spider(self, spider):
        # Initialize lists for each table
        self.data = {
            "apps": [],
            "key_benefits": [],
            "pricing_plans": [],
            "pricing_plan_features": [],
            "categories": [],
            "apps_categories": [],
            "reviews": [],
        }

    def process_item(self, item, spider):
        # Route items to their specific list
        if isinstance(item, App):
            self.data["apps"].append(dict(item))
        elif isinstance(item, KeyBenefit):
            self.data["key_benefits"].append(dict(item))
        elif isinstance(item, PricingPlan):
            self.data["pricing_plans"].append(dict(item))
        elif isinstance(item, PricingPlanFeature):
            self.data["pricing_plan_features"].append(dict(item))
        elif isinstance(item, Category):
            self.data["categories"].append(dict(item))
        elif isinstance(item, AppCategory):
            self.data["apps_categories"].append(dict(item))
        elif isinstance(item, AppReview):
            self.data["reviews"].append(dict(item))
        return item

    def close_spider(self, spider):
        output_dir = "./output/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        spider.logger.info("Starting Pandas cleanup...")

        # 1. APPS
        if self.data["apps"]:
            df = pd.DataFrame(self.data["apps"])
            # Remove duplicate apps by URL (keep latest crawl)
            df.drop_duplicates(subset=["url"], keep="last", inplace=True)
            df.to_csv(output_dir + "apps.csv", index=False)

        # 2. CATEGORIES (Reference Table)
        if self.data["categories"]:
            df = pd.DataFrame(self.data["categories"])
            # Unique ID per category
            df.drop_duplicates(subset=["id"], keep="first", inplace=True)
            df.to_csv(output_dir + "categories.csv", index=False)

        # 3. APP_CATEGORIES (Linking Table)
        if self.data["apps_categories"]:
            df = pd.DataFrame(self.data["apps_categories"])
            df.drop_duplicates(inplace=True)
            df.to_csv(output_dir + "apps_categories.csv", index=False)

        # 4. REVIEWS
        if self.data["reviews"]:
            df = pd.DataFrame(self.data["reviews"])
            # Deduplicate exact same review content
            df.drop_duplicates(
                subset=["app_id", "author", "posted_at", "body"], inplace=True
            )
            df.to_csv(output_dir + "reviews.csv", index=False)

        # 5. PRICING PLANS
        if self.data["pricing_plans"]:
            df = pd.DataFrame(self.data["pricing_plans"])
            df.drop_duplicates(subset=["id"], inplace=True)
            df.to_csv(output_dir + "pricing_plans.csv", index=False)

        # 6. PRICING FEATURES
        if self.data["pricing_plan_features"]:
            df = pd.DataFrame(self.data["pricing_plan_features"])
            df.drop_duplicates(inplace=True)
            df.to_csv(output_dir + "pricing_plan_features.csv", index=False)

        # 7. KEY BENEFITS
        if self.data["key_benefits"]:
            df = pd.DataFrame(self.data["key_benefits"])
            df.drop_duplicates(inplace=True)
            df.to_csv(output_dir + "key_benefits.csv", index=False)

        spider.logger.info("All CSVs saved successfully.")
