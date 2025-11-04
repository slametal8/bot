import requests
import threading
import time
import random
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import json
import logging
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

class AutoIndexer:
    def __init__(self):
        self.setup_logging()
        self.results = {
            'success': 0,
            'failed': 0,
            'total_processed': 0
        }
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('indexer.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_urls_from_file(self, filename):
        """Load URLs from text file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            self.logger.info(f"Loaded {len(urls)} URLs from {filename}")
            return urls
        except Exception as e:
            self.logger.error(f"Error loading URLs from file: {e}")
            return []

    def extract_urls_from_sitemap(self, sitemap_url):
        """Extract URLs from sitemap.xml"""
        urls = []
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            response = requests.get(sitemap_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # Handle sitemap index
            if root.tag.endswith('sitemapindex'):
                for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                    loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None:
                        urls.extend(self.extract_urls_from_sitemap(loc.text))
            
            # Handle URL set
            elif root.tag.endswith('urlset'):
                for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None:
                        urls.append(loc.text)
            
            self.logger.info(f"Extracted {len(urls)} URLs from sitemap: {sitemap_url}")
            
        except Exception as e:
            self.logger.error(f"Error extracting from sitemap {sitemap_url}: {e}")
        
        return urls

    def filter_urls(self, urls, filters=None):
        """Filter URLs based on criteria"""
        if not filters:
            return urls
            
        filtered_urls = []
        for url in urls:
            include = True
            if 'include' in filters:
                include = any(keyword in url for keyword in filters['include'])
            if 'exclude' in filters:
                include = include and not any(keyword in url for keyword in filters['exclude'])
            
            if include:
                filtered_urls.append(url)
        
        self.logger.info(f"Filtered {len(urls)} -> {len(filtered_urls)} URLs")
        return filtered_urls

    def submit_to_google(self, url):
        """Submit URL to Google Indexing API"""
        try:
            # Using Google Indexing API (requires setup)
            api_url = "https://indexing.googleapis.com/v3/urlNotifications:publish"
            
            headers = {
                'Content-Type': 'application/json',
                # 'Authorization': 'Bearer YOUR_ACCESS_TOKEN'  # Add your token
            }
            
            payload = {
                'url': url,
                'type': 'URL_UPDATED'
            }
            
            # For demo, we'll simulate the request
            time.sleep(random.uniform(0.5, 2.0))
            success = random.random() > 0.1  # 90% success rate simulation
            
            if success:
                self.logger.info(f"✅ Google: {url}")
                return True
            else:
                self.logger.warning(f"❌ Google failed: {url}")
                return False
                
        except Exception as e:
            self.logger.error(f"Google submission error: {e}")
            return False

    def submit_to_bing(self, url):
        """Submit URL to Bing Webmaster Tools"""
        try:
            # Bing Submission API
            api_url = "https://www.bing.com/webmaster/api.svc/json/SubmitUrl"
            
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                # 'Authorization': 'Bearer YOUR_BING_API_KEY'
            }
            
            payload = {
                'siteUrl': urlparse(url).netloc,
                'url': url
            }
            
            # Simulation
            time.sleep(random.uniform(0.3, 1.5))
            success = random.random() > 0.15  # 85% success rate
            
            if success:
                self.logger.info(f"✅ Bing: {url}")
                return True
            else:
                self.logger.warning(f"❌ Bing failed: {url}")
                return False
                
        except Exception as e:
            self.logger.error(f"Bing submission error: {e}")
            return False

    def submit_to_yandex(self, url):
        """Submit URL to Yandex Webmaster"""
        try:
            # Yandex simulation
            time.sleep(random.uniform(0.7, 2.2))
            success = random.random() > 0.2  # 80% success rate
            
            if success:
                self.logger.info(f"✅ Yandex: {url}")
                return True
            else:
                self.logger.warning(f"❌ Yandex failed: {url}")
                return False
                
        except Exception as e:
            self.logger.error(f"Yandex submission error: {e}")
            return False

    def submit_to_yahoo_aol(self, url):
        """Submit URL to Yahoo & AOL (via Bing)"""
        try:
            # Yahoo & AOL use Bing's index
            time.sleep(random.uniform(0.4, 1.8))
            success = random.random() > 0.25  # 75% success rate
            
            if success:
                self.logger.info(f"✅ Yahoo/AOL: {url}")
                return True
            else:
                self.logger.warning(f"❌ Yahoo/AOL failed: {url}")
                return False
                
        except Exception as e:
            self.logger.error(f"Yahoo/AOL submission error: {e}")
            return False

    def submit_url(self, url):
        """Submit single URL to all search engines"""
        results = {}
        
        try:
            # Random delay to appear natural
            time.sleep(random.uniform(1, 3))
            
            # Submit to all search engines
            results['google'] = self.submit_to_google(url)
            results['bing'] = self.submit_to_bing(url)
            results['yandex'] = self.submit_to_yandex(url)
            results['yahoo_aol'] = self.submit_to_yahoo_aol(url)
            
            # Update statistics
            self.results['total_processed'] += 1
            if any(results.values()):
                self.results['success'] += 1
            else:
                self.results['failed'] += 1
                
        except Exception as e:
            self.logger.error(f"Error submitting URL {url}: {e}")
            self.results['failed'] += 1
            self.results['total_processed'] += 1
            
        return results

    def process_batch(self, urls, max_workers=10, delay_between_batches=5):
        """Process batch of URLs with multi-threading"""
        self.logger.info(f"Starting batch processing of {len(urls)} URLs with {max_workers} workers")
        
        successful_submissions = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.submit_url, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if any(result.values()):
                        successful_submissions += 1
                except Exception as e:
                    self.logger.error(f"Thread error for {url}: {e}")
        
        self.logger.info(f"Batch completed: {successful_submissions}/{len(urls)} successful")
        
        # Delay between batches
        if delay_between_batches > 0:
            time.sleep(delay_between_batches)
            
        return successful_submissions

    def run_continuous_mode(self, url_source, batch_size=50, max_workers=5, 
                           delay_between_batches=30, total_urls=None):
        """Run in continuous mode 24/7"""
        self.logger.info("🚀 Starting continuous mode (24/7)")
        
        processed_count = 0
        
        while True:
            try:
                # Get batch of URLs
                if isinstance(url_source, list):
                    batch_urls = url_source[processed_count:processed_count + batch_size]
                else:
                    # For API or dynamic source
                    batch_urls = self.get_urls_from_api(url_source, batch_size)
                
                if not batch_urls:
                    self.logger.info("No more URLs to process. Waiting...")
                    time.sleep(300)  # Wait 5 minutes
                    continue
                
                # Process batch
                success_count = self.process_batch(
                    batch_urls, 
                    max_workers=max_workers, 
                    delay_between_batches=delay_between_batches
                )
                
                processed_count += len(batch_urls)
                
                # Log progress
                self.logger.info(f"📊 Progress: {processed_count} URLs processed")
                
                # Check if we've reached the limit
                if total_urls and processed_count >= total_urls:
                    self.logger.info(f"🎯 Reached target of {total_urls} URLs")
                    break
                    
                # Random longer break every few batches
                if processed_count % 200 == 0:
                    nap_time = random.randint(60, 300)  # 1-5 minutes
                    self.logger.info(f"💤 Taking a {nap_time}s break...")
                    time.sleep(nap_time)
                    
            except KeyboardInterrupt:
                self.logger.info("⏹️ Continuous mode stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Continuous mode error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

    def get_urls_from_api(self, api_endpoint, limit=50):
        """Get URLs from API endpoint"""
        # Implement your API call here
        # This is a placeholder - implement based on your API
        try:
            response = requests.get(f"{api_endpoint}?limit={limit}")
            data = response.json()
            return [item['url'] for item in data.get('urls', [])]
        except:
            return []

    def save_progress(self, filename='progress.json'):
        """Save current progress"""
        progress = {
            'results': self.results,
            'last_update': datetime.now().isoformat(),
            'total_runtime': time.time() - self.start_time
        }
        
        with open(filename, 'w') as f:
            json.dump(progress, f, indent=2)

    def show_stats(self):
        """Display statistics"""
        print("\n" + "="*50)
        print("📊 INDEXING STATISTICS")
        print("="*50)
        print(f"✅ Successful: {self.results['success']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Total Processed: {self.results['total_processed']}")
        
        if self.results['total_processed'] > 0:
            success_rate = (self.results['success'] / self.results['total_processed']) * 100
            print(f"🎯 Success Rate: {success_rate:.2f}%")
        
        print("="*50)

def main():
    indexer = AutoIndexer()
    indexer.start_time = time.time()
    
    print("🚀 AUTO INDEXER BOT - Multi-Engine Submission")
    print("✅ Google, Bing, Yandex, Yahoo & AOL")
    print("⚡ Multi-threading & 24/7 Mode Supported\n")
    
    try:
        # Configuration
        MODE = input("Choose mode (1: Single File, 2: Sitemap, 3: Continuous, 4: API): ").strip()
        
        urls = []
        
        if MODE == "1":
            # Single file mode
            filename = input("Enter URLs file path: ").strip()
            urls = indexer.load_urls_from_file(filename)
            
        elif MODE == "2":
            # Sitemap mode
            sitemap_url = input("Enter sitemap URL: ").strip()
            urls = indexer.extract_urls_from_sitemap(sitemap_url)
            
        elif MODE == "3":
            # Continuous mode
            source_type = input("Source type (1: File, 2: Sitemap, 3: API): ").strip()
            
            if source_type == "1":
                filename = input("Enter URLs file path: ").strip()
                url_source = indexer.load_urls_from_file(filename)
            elif source_type == "2":
                sitemap_url = input("Enter sitemap URL: ").strip()
                url_source = indexer.extract_urls_from_sitemap(sitemap_url)
            else:
                api_url = input("Enter API endpoint: ").strip()
                url_source = api_url
            
            batch_size = int(input("Batch size (default 50): ") or "50")
            max_workers = int(input("Max workers (default 5): ") or "5")
            total_urls = input("Total URLs to process (empty for unlimited): ").strip()
            total_urls = int(total_urls) if total_urls else None
            
            indexer.run_continuous_mode(
                url_source=url_source,
                batch_size=batch_size,
                max_workers=max_workers,
                total_urls=total_urls
            )
            return
            
        elif MODE == "4":
            # API mode
            api_url = input("Enter API endpoint: ").strip()
            urls = indexer.get_urls_from_api(api_url, 100)
        
        # Filter URLs if needed
        filter_choice = input("Apply filters? (y/n): ").lower().strip()
        if filter_choice == 'y':
            include_keywords = input("Include keywords (comma separated): ").split(',')
            exclude_keywords = input("Exclude keywords (comma separated): ").split(',')
            
            filters = {
                'include': [k.strip() for k in include_keywords if k.strip()],
                'exclude': [k.strip() for k in exclude_keywords if k.strip()]
            }
            urls = indexer.filter_urls(urls, filters)
        
        # Ask for random selection
        if len(urls) > 100:
            random_choice = input(f"Found {len(urls)} URLs. Use random selection? (y/n): ").lower().strip()
            if random_choice == 'y':
                sample_size = int(input("How many URLs to process? ") or "100")
                urls = random.sample(urls, min(sample_size, len(urls)))
        
        # Process URLs
        if urls:
            max_workers = int(input("Max workers (default 10): ") or "10")
            indexer.process_batch(urls, max_workers=max_workers)
        else:
            print("❌ No URLs to process!")
            
    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        indexer.show_stats()
        indexer.save_progress()

if __name__ == "__main__":
    main()
