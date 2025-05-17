import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
import time

class WebCrawler:
    def __init__(self,base_url,max_pages=50):
        self.base_url = base_url
        self.visited = set()
        self.to_visit = [base_url]
        self.max_pages = max_pages
        self.documents = {} 
    def crawl(self):
        while self.to_visit and len(self.visited) < self.max_pages:
            url = self.to_visit.pop(0)
            if url in self.visited:
                continue

            print(f"Crawling: {url}")
            try:
                response = requests.get(url, timeout=5)
                if response.status_code != 200:
                    continue
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract text (simple)
                text = soup.get_text(separator=' ', strip=True)

                # Store doc
                doc_id = len(self.visited)
                self.documents[doc_id] = {'url': url, 'text': text}

                self.visited.add(url)

                # Find new links within the same domain
                base_domain = urlparse(self.base_url).netloc
                for link in soup.find_all('a', href=True):
                    abs_link = urljoin(url, link['href'])
                    if urlparse(abs_link).netloc == base_domain and abs_link not in self.visited:
                        self.to_visit.append(abs_link)

                time.sleep(1)  # polite crawling

            except Exception as e:
                print(f"Failed to crawl {url}: {e}")

        print(f"Crawled {len(self.documents)} pages.")
        return self.documents
