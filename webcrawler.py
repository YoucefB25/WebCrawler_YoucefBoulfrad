import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

class WebCrawler:
    def __init__(self, base_url, max_pages=10):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited_urls = set()

    def fetch_page(self, url):
        """Fetch the HTML content of a given URL."""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Raise an error if request fails (e.g., 404, 500)
            return response.text
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def extract_links(self, html, base_url):
        """Extract all links from a page and return absolute URLs."""
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        for a_tag in soup.find_all("a", href=True):  # Find all <a> tags with href attribute
            full_url = urljoin(base_url, a_tag["href"])  # Convert relative URLs to absolute
            links.add(full_url)
        return links

    def crawl(self, start_url):
        """Main crawling function."""
        to_visit = {start_url}  # Set of URLs to visit (avoids duplicates)
        
        while to_visit and len(self.visited_urls) < self.max_pages:
            url = to_visit.pop()  # Get a URL from the set
            if url in self.visited_urls:
                continue  # Skip if already visited
            
            print(f"Crawling: {url}")
            html = self.fetch_page(url)
            if html is None:
                continue  # Skip failed requests
            
            self.visited_urls.add(url)  # Mark URL as visited
            
            # Extract new links and add them to the queue
            new_links = self.extract_links(html, url)
            to_visit.update(new_links - self.visited_urls)  # Avoid revisiting old links

            time.sleep(1)  # Politeness delay to avoid overloading servers

# Usage Example
if __name__ == "__main__":
    crawler = WebCrawler("https://yahoo.fr", max_pages=10)
    crawler.crawl("https://yahoo.fr")
