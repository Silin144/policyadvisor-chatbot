import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
import os

class PolicyAdvisorScraper:
    def __init__(self):
        self.base_url = "https://policyadvisor.com"
        self.data = []
        self.visited_urls = set()
        
    def get_soup(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def extract_structured_data(self, soup):
        """Extract structured data from script tags"""
        structured_data = {}
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                structured_data.update(data)
            except:
                continue
        return structured_data

    def extract_faq_content(self, soup):
        """Extract FAQ sections and questions"""
        faqs = []
        # Look for common FAQ patterns
        faq_sections = soup.find_all(['div', 'section'], class_=lambda x: x and 'faq' in x.lower())
        
        for section in faq_sections:
            questions = section.find_all(['dt', 'h3', 'h4'])
            answers = section.find_all(['dd', 'p'])
            
            for q, a in zip(questions, answers):
                faqs.append({
                    'question': q.get_text(strip=True),
                    'answer': a.get_text(strip=True)
                })
        
        return faqs

    def extract_page_content(self, url):
        soup = self.get_soup(url)
        if not soup:
            return None

        content = {
            'url': url,
            'title': '',
            'content': '',
            'metadata': {},
            'structured_data': {},
            'faqs': [],
            'categories': [],
            'summary': '',
            'last_updated': '',
            'author': '',
            'related_topics': []
        }

        # Extract title
        title_tag = soup.find('h1')
        if title_tag:
            content['title'] = title_tag.get_text().strip()

        # Extract main content with better structure
        main_content = soup.find('main') or soup.find('article')
        if main_content:
            # Remove unwanted elements
            for unwanted in main_content.find_all(['script', 'style', 'nav', 'header', 'footer']):
                unwanted.decompose()
            
            # Extract content with structure preservation
            content_structure = []
            for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol']):
                if element.name.startswith('h'):
                    content_structure.append({
                        'type': 'heading',
                        'level': int(element.name[1]),
                        'text': element.get_text(strip=True)
                    })
                elif element.name == 'p':
                    text = element.get_text(strip=True)
                    if text:
                        content_structure.append({
                            'type': 'paragraph',
                            'text': text
                        })
                elif element.name in ['ul', 'ol']:
                    items = [li.get_text(strip=True) for li in element.find_all('li')]
                    if items:
                        content_structure.append({
                            'type': 'list',
                            'items': items
                        })
            
            # Store structured content
            content['content_structure'] = content_structure
            # Also keep plain text version for backward compatibility
            content['content'] = ' '.join(item['text'] if 'text' in item else ' '.join(item['items'])
                                        for item in content_structure)

        # Extract enhanced metadata
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name', tag.get('property', ''))
            if name and tag.get('content'):
                content['metadata'][name] = tag.get('content')

        # Extract structured data
        content['structured_data'] = self.extract_structured_data(soup)

        # Extract FAQs
        content['faqs'] = self.extract_faq_content(soup)

        # Extract categories/tags
        category_elements = soup.find_all(['a', 'span'], class_=lambda x: x and any(word in x.lower()
                                        for word in ['category', 'tag', 'topic']))
        content['categories'] = [el.get_text(strip=True) for el in category_elements]

        # Extract author information
        author_element = soup.find(['a', 'span', 'p'], class_=lambda x: x and 'author' in x.lower())
        if author_element:
            content['author'] = author_element.get_text(strip=True)

        # Extract last updated date
        date_element = soup.find(['time', 'span', 'p'], class_=lambda x: x and any(word in x.lower()
                                for word in ['date', 'published', 'updated']))
        if date_element:
            content['last_updated'] = date_element.get_text(strip=True)

        # Extract related topics
        related_elements = soup.find_all(['a'], class_=lambda x: x and 'related' in x.lower())
        content['related_topics'] = [el.get_text(strip=True) for el in related_elements]

        return content

    def get_internal_links(self, url):
        soup = self.get_soup(url)
        if not soup:
            return []

        internal_links = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(self.base_url, href)
            
            # Only include internal links from the same domain
            if full_url.startswith(self.base_url) and '#' not in full_url:
                internal_links.add(full_url)

        return list(internal_links)

    def scrape_site(self, max_pages=None):
        to_visit = [self.base_url]
        pages_scraped = 0

        while to_visit and (max_pages is None or pages_scraped < max_pages):
            url = to_visit.pop(0)
            
            if url in self.visited_urls:
                continue

            print(f"Scraping: {url}")
            content = self.extract_page_content(url)
            
            if content:
                self.data.append(content)
                self.visited_urls.add(url)
                pages_scraped += 1

                # Get new links to visit
                new_links = self.get_internal_links(url)
                to_visit.extend([link for link in new_links if link not in self.visited_urls])

            # Be polite with rate limiting
            time.sleep(2)

        # Save the scraped data
        self.save_data()

    def save_data(self):
        if not os.path.exists('data'):
            os.makedirs('data')
            
        with open('data/policyadvisor_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    scraper = PolicyAdvisorScraper()
    # Scrape up to 500 pages for extensive coverage
    scraper.scrape_site(max_pages=500)