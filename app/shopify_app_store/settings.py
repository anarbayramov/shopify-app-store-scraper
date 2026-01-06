# -*- coding: utf-8 -*-

BOT_NAME = "shopify_app_store"

SPIDER_MODULES = ["shopify_app_store.spiders"]
NEWSPIDER_MODULE = "shopify_app_store.spiders"

# --- 1. CRITICAL: USER AGENT ---
# Use a real browser User-Agent to avoid 403 Forbidden errors from Shopify/Cloudflare
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Obey robots.txt rules
# Keep False, as Shopify usually disallows scrapers in robots.txt
ROBOTSTXT_OBEY = False

# --- 2. SPEED SETTINGS ---
# Increase concurrency (AutoThrottle will lower it if the server gets angry)
CONCURRENT_REQUESTS = 16

# Disable cookies (enabled by default) - usually good for scraping to prevent session tracking
COOKIES_ENABLED = False

# --- 3. CRITICAL: PIPELINE SETUP ---
# This MUST match the class name in your pipelines.py file
ITEM_PIPELINES = {
    "shopify_app_store.pipelines.PandasRelationalPipeline": 300,
}

# --- 4. AUTOTHROTTLE & RETRIES ---
# Enable AutoThrottle to prevent getting banned
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Retry middleware settings
# 100 is too high; if it fails 5 times, the page is likely broken or you are blocked.
RETRY_TIMES = 5

# Enable and configure HTTP caching (disabled by default)
# Useful for development (set to True), but for production scraping, keep False.
HTTPCACHE_ENABLED = False
