#!/usr/bin/env python3
"""
Auto Indexer Bot - 24/7 Operation
Usage: python run_bot.py --mode continuous --source urls.txt --workers 5
"""

import argparse
import time
from main import AutoIndexer

def run_continuous_bot():
    parser = argparse.ArgumentParser(description='Auto Indexer Bot - 24/7 Mode')
    parser.add_argument('--source', type=str, required=True, help='URL source (file, sitemap, or API)')
    parser.add_argument('--workers', type=int, default=5, help='Number of worker threads')
    parser.add_argument('--batch-size', type=int, default=50, help='URLs per batch')
    parser.add_argument('--delay', type=int, default=30, help='Delay between batches (seconds)')
    parser.add_argument('--total', type=int, help='Total URLs to process')
    
    args = parser.parse_args()
    
    indexer = AutoIndexer()
    
    print("🤖 Starting Auto Indexer Bot - 24/7 Mode")
    print(f"🔧 Workers: {args.workers} | Batch: {args.batch_size} | Delay: {args.delay}s")
    
    try:
        indexer.run_continuous_mode(
            url_source=args.source,
            batch_size=args.batch_size,
            max_workers=args.workers,
            delay_between_batches=args.delay,
            total_urls=args.total
        )
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
    finally:
        indexer.show_stats()

if __name__ == "__main__":
    run_continuous_bot()
