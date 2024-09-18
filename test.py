import scrapy
from scrapy.crawler import CrawlerProcess
from newspaper import Article
from urllib.parse import urljoin, urlparse
from datetime import datetime
import csv
import os

class NewsCrawler(scrapy.Spider):
    name = 'news_crawler'

    def __init__(self, start_urls=None, allowed_domains=None, *args, **kwargs):
        super(NewsCrawler, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.allowed_domains = allowed_domains

        # Create a CSV file with the current timestamp as its name
        current_time = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
        self.output_file = f'output/{current_time}.csv'

        # Create the CSV file and write the header
        with open(self.output_file, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Title', 'Content', 'Publish Date', 'URL'])

    def parse(self, response):
        # Extract article links from the current page
        article_links = response.css('a::attr(href)').getall()
        for link in article_links:
            absolute_link = urljoin(response.url, link)  # Ensure absolute URL
            yield scrapy.Request(url=absolute_link, callback=self.parse_article)

        # Follow pagination links if available
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            next_page_url = urljoin(response.url, next_page)  # Ensure absolute URL
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_article(self, response):
        """Extract article using Newspaper3k and save data to the CSV file"""
        article = Article(response.url)
        article.download()
        article.parse()

        if not article.publish_date:
            return

        # Get the article's content
        title = article.title or "untitled"
        content = article.text
        publish_date = article.publish_date
        url = response.url

        # Prepare the data for output
        scraped_data = [title, content, str(publish_date), url]

        # Append the article data to the CSV file
        with open(self.output_file, mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(scraped_data)

def extract_base_urls(urls):
    base_urls = set()  # Using a set to avoid duplicate domains
    for url in urls:
        try:
            parsed_url = urlparse(url)
            base_url = parsed_url.netloc
            if base_url.startswith('www.'):
                base_url = base_url[4:]  # Remove 'www.' if present
            base_urls.add(base_url)
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
    return list(base_urls)

def run_crawler():
    # Define custom settings for the spider
    custom_settings = {
        'CONCURRENT_REQUESTS': 100,  # Increase the number of concurrent requests
        'CONCURRENT_REQUESTS_PER_DOMAIN': 50,  # Adjust based on your needs
        'DOWNLOAD_DELAY': 0.1,  # Reduce delay between requests
        'AUTOTHROTTLE_ENABLED': True,  # Enable auto-throttling
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,  # Adjust concurrency target
        'AUTOTHROTTLE_MAX_DELAY': 60,  # Max delay if server is slow
        'DEPTH_LIMIT': 10,  # Increase depth limit for crawling
    }

    # Initialize the CrawlerProcess with custom settings
    process = CrawlerProcess(settings=custom_settings)

    # Define spider arguments
    start_urls = [
        'https://www.inquirer.com/',
        'https://www.post-gazette.com',
        'https://www.mcall.com',
        'https://www.lancasteronline.com',
        'https://www.witf.org',
        'https://www.wtae.com',
        'https://www.wpxi.com',
        'https://www.kdka.com',
        'https://www.nbcphiladelphia.com',
        'https://www.6abc.com',
        'https://www.cbsnews.com/philadelphia/',
        'https://www.timesleader.com',
        'https://www.citizensvoice.com',
        'https://www.delcotimes.com',
        'https://www.pennlive.com',
        'https://www.triblive.com',
        'https://www.ydr.com',
        'https://www.theintell.com',
        'https://www.pennlive.com/',
        'https://www.couriertimes.com',
        'https://www.phillytrib.com',
        'https://www.observer-reporter.com',
        'https://www.statecollegelive.com',
        'https://www.ldnews.com',
        'https://www.timesherald.com',
        'https://www.bradfordera.com',
        'https://www.dailyitem.com',
        'https://www.greenfieldreporter.com',
        'https://www.grovecitynews.com',
        'https://www.republicanherald.com'
    ]

    allowed_domains = extract_base_urls(start_urls)

    # Start the crawling process
    process.crawl(
        NewsCrawler,
        start_urls=start_urls,  # Pass start_urls as a named argument
        allowed_domains=allowed_domains  # Pass allowed_domains as a named argument
    )
    process.start()

if __name__ == '__main__':
    run_crawler()
