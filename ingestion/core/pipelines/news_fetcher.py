# ingestion/core/pipelines/news_fetcher.py
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import json
import os
from google.cloud import storage
from bs4 import BeautifulSoup
from .. import config, gcs
from ..clients.polygon_client import PolygonClient

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("STEP 1: Importing news_fetcher.py module.")

NEWS_OUTPUT_PREFIX = config.PREFIXES["news_analyzer"]["input"]
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

logging.info(f"STEP 2: Fetched POLYGON_API_KEY. Is it present? {'Yes' if POLYGON_API_KEY else 'No'}")

def map_polygon_news(article: dict) -> dict:
    html_text = article.get("body") or article.get("teaser", "")
    soup = BeautifulSoup(html_text, "html.parser")
    plain_text = soup.get_text(separator=" ", strip=True)
    return {
        "title": article.get("title"), "publishedDate": article.get("published"),
        "image": None, "site": article.get("author"), "text": plain_text,
        "url": article.get("url"),
    }

def fetch_and_save_headlines(ticker: str, storage_client: storage.Client):
    logging.info(f"[{ticker}] STEP 5: Starting fetch_and_save_headlines for this ticker.")
    
    if not POLYGON_API_KEY:
        logging.critical(f"[{ticker}] POLYGON_API_KEY is not set. Aborting task for this ticker.")
        return

    client = PolygonClient(POLYGON_API_KEY)
    today = datetime.date.today()
    from_date = today - datetime.timedelta(days=7)
    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = today.strftime("%Y-%m-%d")
    
    # Fetch stock-specific news
    logging.info(f"[{ticker}] STEP 6: Fetching stock-specific news.")
    stock_news_raw = client.fetch_news(
        ticker=ticker, from_date=from_date_str, to_date=to_date_str, limit_per_page=4
    )
    stock_news = [map_polygon_news(article) for article in stock_news_raw]
    logging.info(f"[{ticker}] STEP 7: Found {len(stock_news)} stock-specific articles.")
    
    # Fetch macro news
    logging.info(f"[{ticker}] STEP 8: Fetching macro news.")
    macro_news_raw = client.fetch_news(
        from_date=from_date_str, to_date=to_date_str, limit_per_page=4,
        topics_str="economy,markets,federal reserve,inflation,gdp,geopolitics"
    )
    macro_news = [map_polygon_news(article) for article in macro_news_raw]
    logging.info(f"[{ticker}] STEP 9: Found {len(macro_news)} macro articles.")
    
    headlines = {
        "stock_news": sorted(stock_news, key=lambda x: x.get('publishedDate', ''), reverse=True),
        "macro_news": sorted(macro_news, key=lambda x: x.get('publishedDate', ''), reverse=True)
    }
    
    output_path = f"{NEWS_OUTPUT_PREFIX}{ticker}_{today.strftime('%Y-%m-%d')}.json"
    logging.info(f"[{ticker}] STEP 10: Uploading data to {output_path}.")
    gcs.upload_json_to_gcs(storage_client, headlines, output_path)
    gcs.cleanup_old_files(storage_client, NEWS_OUTPUT_PREFIX, ticker, output_path)
    
    if not headlines["stock_news"] and not headlines["macro_news"]:
        logging.info(f"[{ticker}] No recent news found. Saved empty file.")
    
    logging.info(f"[{ticker}] STEP 11: Finished processing.")


def run_pipeline():
    logging.info("STEP 3: Starting run_pipeline.")
    
    if not POLYGON_API_KEY:
        logging.critical("CRITICAL: POLYGON_API_KEY not set. Aborting news_fetcher pipeline.")
        return

    logging.info("--- Starting News Fetcher Pipeline (SERIAL, VERBOSE LOGGING) ---")
    
    storage_client = storage.Client()
    tickers = gcs.get_tickers(storage_client)
    if not tickers:
        logging.warning("WARNING: No tickers found in tickerlist.txt. Exiting.")
        return

    logging.info(f"STEP 4: Found {len(tickers)} tickers. Starting SERIAL processing loop.")
    
    # --- SERIAL EXECUTION BLOCK FOR DEBUGGING ---
    processed_count = 0
    failed_count = 0
    for ticker in tickers:
        try:
            logging.info(f"--- Processing ticker: {ticker} ---")
            fetch_and_save_headlines(ticker, storage_client)
            processed_count += 1
        except Exception as e:
            logging.error(f"--- FAILED processing ticker: {ticker} ---", exc_info=True)
            failed_count += 1
    # --- END SERIAL EXECUTION BLOCK ---
                
    logging.info(f"STEP 12: Pipeline finished. Processed: {processed_count}, Failed: {failed_count}.")