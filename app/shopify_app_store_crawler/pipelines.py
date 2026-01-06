import pandas as pd
import os
import sqlite3
import json
from .items import (
    App,
    KeyBenefit,
    PricingPlan,
    PricingPlanFeature,
    Category,
    AppCategory,
    AppReview,
)


class SqliteRelationalPipeline(object):
    APP_BATCH_SIZE = 10
    DB_NAME = "shopify_app_data.db"
    OUTPUT_DIR = "../data"

    def open_spider(self, spider):
        if not os.path.exists(self.OUTPUT_DIR):
            os.makedirs(self.OUTPUT_DIR)

        self.db_path = os.path.join(self.OUTPUT_DIR, self.DB_NAME)
        self.conn = sqlite3.connect(self.db_path)
        # WAL mode improves concurrent writing speed
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")

        spider.logger.info(f"Connected to SQLite: {self.db_path}")

        self.buffers = {
            "apps": [],
            "key_benefits": [],
            "pricing_plans": [],
            "pricing_plan_features": [],
            "categories": [],
            "apps_categories": [],
            "reviews": [],
        }

    def process_item(self, item, spider):
        table_name = None
        if isinstance(item, App):
            table_name = "apps"
        elif isinstance(item, KeyBenefit):
            table_name = "key_benefits"
        elif isinstance(item, PricingPlan):
            table_name = "pricing_plans"
        elif isinstance(item, PricingPlanFeature):
            table_name = "pricing_plan_features"
        elif isinstance(item, Category):
            table_name = "categories"
        elif isinstance(item, AppCategory):
            table_name = "apps_categories"
        elif isinstance(item, AppReview):
            table_name = "reviews"

        if table_name:
            data = dict(item)

            # Convert Lists and Dicts to JSON strings for SQLite
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    data[key] = json.dumps(value) if value is not None else "[]"

            self.buffers[table_name].append(data)

            # Flush everything when we hit 10 Apps
            if (
                table_name == "apps"
                and len(self.buffers["apps"]) >= self.APP_BATCH_SIZE
            ):
                spider.logger.info(
                    f"Batch limit reached ({self.APP_BATCH_SIZE} Apps). Flushing to DB..."
                )
                self.flush_all_tables(spider)

        return item

    def flush_all_tables(self, spider):
        for table in self.buffers:
            data = self.buffers[table]
            if data:
                try:
                    df = pd.DataFrame(data)
                    # 'append' adds to the existing table
                    df.to_sql(table, self.conn, if_exists="append", index=False)
                    self.buffers[table] = []  # Clear memory buffer
                except Exception as e:
                    spider.logger.error(f"DB Error on table '{table}': {e}")

    def close_spider(self, spider):
        spider.logger.info("Spider closing. Flushing remaining data...")
        self.flush_all_tables(spider)

        # Deduplication (cleaning up potential duplicates from restarts)
        self.remove_duplicates_sql("apps", "url")
        self.remove_duplicates_sql("categories", "id")
        # Removing duplicates for reviews based on composite key
        self.remove_duplicates_sql("reviews", "app_id, author, posted_at")

        self.conn.close()

    def remove_duplicates_sql(self, table, unique_cols):
        try:
            # Check if table exists first to avoid errors on fresh runs
            cursor = self.conn.cursor()
            cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';"
            )
            if cursor.fetchone():
                sql = f"DELETE FROM {table} WHERE rowid NOT IN (SELECT MAX(rowid) FROM {table} GROUP BY {unique_cols});"
                self.conn.execute(sql)
                self.conn.commit()
        except Exception:
            pass
