import scrapy
import sys
print(sys.path)
from scrapy.linkextractors import LinkExtractor

class OpenLibrarySpider(scrapy.Spider):
    name = "openlibrary"
    chosen_subjects = [
        "romance", "fantasy", "historical_fiction", "horror", "humor",
        "literature", "mystery_and_detective_stories", "science_fiction"
    ]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; OpenLibraryBot/1.0; +https://openlibrary.org)'
    }
    link_extractor = LinkExtractor(allow="https://openlibrary.org/subjects*")  # Define the pattern for URLs to extract

    def __init__(self, subdir="", *args, **kwargs):
        self.start_urls = [subdir] if subdir else ["https://openlibrary.org/subjects"]
        self.page_count = 0  # Initialize page_count
        print("Starting URL:", self.start_urls[0])
        super().__init__(*args, **kwargs)

    def parse(self, response):
        self.logger.info("Parsing subjects page")
        links = self.link_extractor.extract_links(response)  # Use LinkExtractor to extract links
        for link in links:
            if (
                link.url.startswith("https://openlibrary.org/subjects/") and 
                any(subject in link.url for subject in self.chosen_subjects) and 
                "juvenile_literature" not in link.url
            ):
                print(f"Valid subject URL: {link.url}")
                yield scrapy.Request(url=link.url, callback=self.parse_total_works)

    def parse_total_works(self, response):
        self.logger.info("Parsing to total works page")
        total_works_link = response.css("div.page-heading-search-box strong span a::attr(href)").get()

        if total_works_link:
            yield scrapy.Request(url=response.urljoin(total_works_link), callback=self.parse_books)

    def parse_books(self, response):
        self.logger.info("Parsing books page")
        book_link_list = []
        # Use LinkExtractor here to extract book links
        for book_list in response.css("div.resultsContainer.search-results-container div#searchResults ul.list-books li.searchResultItem.sri--w-main"):
            book_link = book_list.css("div.sri__main a::attr(href)").get()

            # should we go into the URL if there are no ratings?
            ratings_text = book_list.css("div.details span[itemprop='ratingValue']::text").get()
            if ratings_text:
                try:
                    ratings_num = int(ratings_text.split('(')[1].split()[0])
                    if ratings_num > 0:
                        book_link = "https://openlibrary.org" + book_link
                        book_link_list.append(book_link)
                except (IndexError, ValueError):
                    self.logger.warning(f"Failed to parse ratings from: {ratings_text}")

        # Handle pagination
        next_page = response.css("div.pagination a.ChoosePage::attr(href)").get()
        last_page = response.css("div.pagination a.ChoosePage::text").getall()
        last_page = int(last_page[-2])
        if next_page:
            self.page_count += 1
            if self.page_count < 1640: 
                yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse_books)  # Crawl the next page recursively
            else:
                self.logger.info(f"Reached {self.page_count} pages.")
                for book_link in book_link_list:
                    self.logger.info(book_link)
                    yield scrapy.Request(url=book_link, callback=self.parse_review_link)


    def parse_review_link(self, response):
        "Assume we are in the book page, return review link from the book"
        self.logger.info("Parsing books review link")
        
        # Iterate over the items in the CSS selector
        all_res = response.css("span.nav-bar-wrapper.sticky.mobile-only ul.nav-bar li a::attr(href)").getall()
        review_link = all_res[3]
        if review_link:
            full_review_url = response.urljoin(review_link)
            self.logger.info(f"Review link: {full_review_url}")
            yield scrapy.Request(url=full_review_url, callback=self.new_parse_book_reviews, dont_filter=True)
            self.logger.info(f"After review link")
        else:
            self.logger.warning(f"No valid review link found: {response.url}")


    def new_parse_book_reviews(self, response):
        "Assume we are in the book review page"
        self.logger.info("Entered parse_book_reviews")
        # Get number of user reviews
        num_review = response.css('a[href="#reader-observations"]::text').re_first(r'(\d+)')

        if num_review:
            num_review = int(num_review)
            book_name = response.css("div.work-title-and-author.mobile h1.work-title::text").get()
            author_name = response.css("div.work-title-and-author.mobile h2.edition-byline a::text").get()

            categories_data_name = []
            categories_data_description = []
            categories_data_percentage = []

            for category in response.css('span.review__category'):
                category_name = category.css('span.reviews__label::text').get()
                categories_data_name.append(category_name)
                reviews_pills = category.css('span.reviews__pill')

                for pill in reviews_pills:
                    description = pill.css('span.reviews__value::text').get()
                    categories_data_description.append(description)
                    percentage = pill.css('span.percentage::text').get()
                    categories_data_percentage.append(percentage)

            yield {
                "book_name": book_name,
                "author_name": author_name,
                "category_name": categories_data_name,
                "category_description": categories_data_description,
                "categories_data": categories_data_percentage
            }

        else:
            self.logger.info("No reviews available for this book.")