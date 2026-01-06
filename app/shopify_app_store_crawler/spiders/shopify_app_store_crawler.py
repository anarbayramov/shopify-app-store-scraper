# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import SitemapSpider
import re
import uuid
import hashlib
from datetime import date
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
    name = "shopify_app_store_crawler"
    allowed_domains = ["apps.shopify.com"]
    sitemap_urls = ["https://apps.shopify.com/sitemap.xml"]

    sitemap_rules = [(r"https://apps\.shopify\.com/([^/]+)$", "parse_app")]

    def parse_app(self, response):
        app_id = str(uuid.uuid4())
        url = response.url
        scraped_at = date.today().isoformat()

        # --- 1. ID & Handle ---
        handle = url.split("?")[0].split("/")[-1]

        internal_id = response.css(
            "button[data-partner-tracking-id]::attr(data-partner-tracking-id)"
        ).get()

        # --- 2. Core Info ---
        title = response.css("h1::text").get(default="").strip()

        privacy_policy_url = response.css(
            'a:contains("Privacy policy")::attr(href)'
        ).get()

        raw_date = response.xpath(
            '//p[contains(text(), "Launched")]/following-sibling::p/text()'
        ).get(default="")
        launch_date = raw_date.replace("·", "").strip()

        # --- 4. Performance & Misc ---
        rating = response.css(
            "#adp-hero dd > span.tw-text-fg-secondary ::text"
        ).extract_first()

        reviews_count_raw = response.css("#reviews-link::text").extract_first(
            default="0 Reviews"
        )
        reviews_count = int("".join(re.findall(r"\d+", reviews_count_raw)))

        description_raw = response.css("#app-details").get()
        description = " ".join(response.css("#app-details ::text").getall()).strip()
        pricing_hint = (
            response.css(
                "#adp-hero > div > div.tw-grow.tw-flex.tw-flex-col.tw-gap-xl > dl > div:nth-child(1) > dd > div.tw-hidden.sm\:tw-block.tw-text-pretty ::text"
            )
            .extract_first()
            .strip()
        )

        yield App(
            id=app_id,
            internal_id=internal_id,
            handle=handle,
            url=url,
            title=title,
            description=description,
            description_raw=description_raw,
            privacy_policy_url=privacy_policy_url,
            launch_date=launch_date,
            rating=rating,
            reviews_count=reviews_count,
            pricing_hint=pricing_hint,
            scraped_at=scraped_at,
        )

        # --- 5. Benefits ---
        for benefit in response.css(".tw-list-disc li"):
            yield KeyBenefit(
                app_id=app_id,
                description=benefit.css("::text").get(default="").strip(),
            )

        # --- 6. Categories ---
        for category_raw in response.css(
            '#adp-details-section a[href^="https://apps.shopify.com/categories"]::text'
        ).extract():
            category = category_raw.strip()
            category_id = hashlib.md5(category.lower().encode()).hexdigest()

            yield Category(id=category_id, title=category)
            yield AppCategory(app_id=app_id, category_id=category_id)

        # --- 7. Pricing Plans (FIXED) ---
        for pricing_plan in response.css(".app-details-pricing-plan-card"):
            pricing_plan_id = str(uuid.uuid4())
            yield PricingPlan(
                id=pricing_plan_id,
                app_id=app_id,
                name=pricing_plan.css('[data-test-id="name"] ::text')
                .extract_first(default="")
                .strip(),
                price=pricing_plan.css(
                    ".app-details-pricing-format-group::attr(aria-label)"
                )
                .extract_first()
                .strip(),
            )

            for feature in pricing_plan.css(
                'ul[data-test-id="features"] li::text'
            ).extract():
                feature_text = feature.strip()
                if not feature_text:
                    continue

                yield PricingPlanFeature(
                    pricing_plan_id=pricing_plan_id, app_id=app_id, feature=feature_text
                )

        # --- 8. Request Reviews ---
        yield scrapy.Request(
            url=f"{url}/reviews",
            callback=self.parse_reviews,
            meta={"app_id": app_id, "page_depth": 1},
            priority=10,
        )

    def parse_reviews(self, response):
        app_id = response.meta["app_id"]
        current_page = response.meta.get("page_depth", 1)

        for review in response.css("[data-merchant-review]"):
            rating = (
                review.css("[aria-label]::attr(aria-label)")
                .extract_first(default="")
                .strip()
                .split()[0]
            )

            # TODO maybe not working
            helpful_count = review.css(
                ".review-helpfulness .review-helpfulness__helpful-count ::text"
            ).extract_first()

            if helpful_count:
                helpful_count = helpful_count.replace("(", "").replace(")", "").strip()

            posted_at_text = review.css(".tw-text-fg-tertiary::text").getall()
            posted_at = posted_at_text[0].strip() if posted_at_text else ""

            all_meta_text = [
                t.strip()
                for t in review.css(".tw-order-1 div::text").getall()
                if t.strip()
            ]

            location = ""
            time_using = ""

            for text in all_meta_text:

                # Check if this text is the usage duration
                if "using the app" in text.lower() or "used the app" in text.lower():
                    time_using = text
                else:
                    # If it's not the name and not the time, it's the location
                    location = text

            yield AppReview(
                app_id=app_id,
                rating=rating,
                posted_at=posted_at,
                location=location,
                time_using_app=time_using,
                body=" ".join(
                    review.css("[data-truncate-content-copy] ::text").getall()
                ).strip(),
                helpful_count=helpful_count,
            )

        if current_page < 10:
            next_page = response.css('a[rel="next"]::attr(href)').get()
            if next_page:
                yield response.follow(
                    next_page,
                    callback=self.parse_reviews,
                    meta={"app_id": app_id, "page_depth": current_page + 1},
                    priority=20,
                )
