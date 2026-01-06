# -*- coding: utf-8 -*-

BOT_NAME = "shopify_app_store_crawler"

SPIDER_MODULES = ["shopify_app_store_crawler.spiders"]
NEWSPIDER_MODULE = "shopify_app_store_crawler.spiders"

LOG_LEVEL = "INFO"


# --- 1. IDENTIFICATION ---
# Standard Chrome User Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# CRITICAL: Add these headers so Cloudflare thinks you are a real browser
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

# --- 2. ROBOTS & COOKIES ---
ROBOTSTXT_OBEY = False
COOKIES_ENABLED = False

# --- 3. SPEED (SAFE MODE) ---
# Set to 1 to avoid 429 blocks during a long 3-day run
CONCURRENT_REQUESTS = 1

# Wait roughly 2 seconds between requests (randomized between 1s and 3s)
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

# --- 4. PIPELINE ---
# Ensure this class exists in your pipelines.py
ITEM_PIPELINES = {
    "shopify_app_store_crawler.pipelines.SqliteRelationalPipeline": 300,
}

# --- 5. AUTOTHROTTLE ---
# This will slow you down further if the server starts struggling
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# --- 6. RETRIES ---
# Retry 429s (Too Many Requests) specifically
RETRY_TIMES = 100
RETRY_HTTP_CODES = [429, 500, 502, 503, 504, 522, 524, 408]

HTTPCACHE_ENABLED = False
