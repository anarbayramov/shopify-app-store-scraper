# -*- coding: utf-8 -*-
from scrapy.spiders import SitemapSpider
from scrapy import Request
import re
import uuid
import hashlib
from ..items import (
    App,
    KeyBenefit,
    PricingPlan,
    PricingPlanFeature,
    Category,
    AppCategory,
    AppReview,
)


class RelationalAppSpider(SitemapSpider):
    name = "app_store"
    allowed_domains = ["apps.shopify.com"]
    sitemap_urls = ["https://apps.shopify.com/sitemap.xml"]

    # Only scrape app pages
    sitemap_rules = [(r"https://apps\.shopify\.com/([^/]+)$", "parse_app")]

    def parse_app(self, response):
        app_id = str(uuid.uuid4())
        url = response.url
        lastmod = response.meta.get("lastmod", "")

        # --- 1. Basic Info ---
        title = response.css("h1::text").get(default="").strip()
        developer = (
            response.css(".tw-text-body-sm.tw-text-fg-tertiary a::text")
            .get(default="")
            .strip()
        )
        developer_link_raw = response.css(
            ".tw-text-body-sm.tw-text-fg-tertiary a::attr(href)"
        ).get()
        developer_link = (
            f"https://apps.shopify.com{developer_link_raw}"
            if developer_link_raw
            else ""
        )

        icon = response.css("img[src*='/app_store/app_images/']::attr(src)").get()

        rating_raw = response.css("[data-test-rating-star-row]::attr(aria-label)").get()
        rating = rating_raw.split(" ")[0] if rating_raw else "0"

        reviews_count_raw = response.css("[data-test-reviews-link]::text").get()
        reviews_count = (
            int("".join(re.findall(r"\d+", reviews_count_raw)))
            if reviews_count_raw
            else 0
        )

        description_raw = response.css("#app-details").get()
        description = " ".join(response.css("#app-details ::text").getall()).strip()

        pricing_hint = (
            response.css("[data-test-pricing-description]::text")
            .get(default="")
            .strip()
        )

        # Yield Main App
        yield App(
            id=app_id,
            url=url,
            title=title,
            developer=developer,
            developer_link=developer_link,
            icon=icon,
            rating=rating,
            reviews_count=reviews_count,
            description_raw=description_raw,
            description=description,
            tagline=None,
            pricing_hint=pricing_hint,
            lastmod=lastmod,
        )

        # --- 2. Key Benefits ---
        for benefit in response.css(".tw-list-disc li"):
            yield KeyBenefit(
                app_id=app_id,
                title=None,
                description=benefit.css("::text").get(default="").strip(),
            )

        # --- 3. Categories (Many-to-Many) ---
        for cat_link in response.css('a[href*="/categories/"]'):
            cat_title = cat_link.css("::text").get(default="").strip()
            if cat_title:
                # Create deterministic ID for category so we can deduplicate later
                cat_id = hashlib.md5(cat_title.lower().encode()).hexdigest()

                yield Category(id=cat_id, title=cat_title)
                yield AppCategory(app_id=app_id, category_id=cat_id)

        # --- 4. Pricing Plans & Features ---
        for plan in response.css("[data-test-pricing-plan-card]"):
            plan_id = str(uuid.uuid4())

            yield PricingPlan(
                id=plan_id,
                app_id=app_id,
                title=plan.css("h3::text").get(default="").strip(),
                price=plan.css("h4::text").get(default="").strip(),
            )

            for feature in plan.css("ul li span::text").getall():
                f_text = feature.strip()
                if f_text:
                    yield PricingPlanFeature(
                        app_id=app_id, pricing_plan_id=plan_id, feature=f_text
                    )

        # --- 5. Request Reviews ---
        yield Request(
            url=f"{url}/reviews", callback=self.parse_reviews, meta={"app_id": app_id}
        )

    def parse_reviews(self, response):
        app_id = response.meta["app_id"]

        for review in response.css("[data-merchant-review]"):
            rating_raw = review.css(
                "[data-test-rating-star-row]::attr(aria-label)"
            ).get()

            helpful_count = review.css('button[type="submit"] span::text').get()
            if helpful_count:
                helpful_count = helpful_count.replace("(", "").replace(")", "").strip()

            yield AppReview(
                app_id=app_id,
                author=review.css(".tw-text-heading-xs::text").get(default="").strip(),
                rating=rating_raw.split(" ")[0] if rating_raw else "0",
                posted_at=review.css(".tw-text-fg-tertiary::text")
                .get(default="")
                .strip(),
                body=" ".join(
                    review.css("[data-truncate-content-copy] ::text").getall()
                ).strip(),
                helpful_count=helpful_count,
                developer_reply=None,  # Complex to extract in new layout
                developer_reply_posted_at=None,
            )

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(
                next_page, callback=self.parse_reviews, meta={"app_id": app_id}
            )
