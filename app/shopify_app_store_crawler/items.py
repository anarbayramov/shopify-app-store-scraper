# items.py
import scrapy


class App(scrapy.Item):
    # IDs
    id = scrapy.Field()  # Generated UUID for relational DB
    internal_id = scrapy.Field()  # The Shopify ID (e.g., 8cada0f5...)
    url = scrapy.Field()
    handle = scrapy.Field()

    # Core Metadata
    title = scrapy.Field()
    description = scrapy.Field()
    description_raw = scrapy.Field()

    privacy_policy_url = scrapy.Field()
    launch_date = scrapy.Field()

    # Performance
    rating = scrapy.Field()
    reviews_count = scrapy.Field()
    rating_distribution = scrapy.Field()  # Stored as JSON string

    # Misc
    languages = scrapy.Field()
    works_with = scrapy.Field()  # Checkout, Flow, etc.
    pricing_hint = scrapy.Field()
    scraped_at = scrapy.Field()


class KeyBenefit(scrapy.Item):
    app_id = scrapy.Field()
    description = scrapy.Field()


class PricingPlan(scrapy.Item):
    id = scrapy.Field()
    app_id = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()


class PricingPlanFeature(scrapy.Item):
    app_id = scrapy.Field()
    pricing_plan_id = scrapy.Field()
    feature = scrapy.Field()


class Category(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()


class AppCategory(scrapy.Item):
    app_id = scrapy.Field()
    category_id = scrapy.Field()


class AppReview(scrapy.Item):
    app_id = scrapy.Field()
    location = scrapy.Field()
    time_using_app = scrapy.Field()
    rating = scrapy.Field()
    posted_at = scrapy.Field()
    body = scrapy.Field()
    helpful_count = scrapy.Field()
