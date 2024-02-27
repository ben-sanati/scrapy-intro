"""
_summary_
"""
import scrapy
from bookscraper.items import BookItem

class BookspiderSpider(scrapy.Spider):
    """
    _summary_

    Args:
        scrapy (_type_): _description_

    Yields:
        _type_: _description_
    """
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        """
        _summary_

        Args:
            response (_type_): _description_

        Yields:
            _type_: _description_
        """
        # get data from books
        books = response.css('article.product_pod')
        for book in books:
            # go into the webpage for each book
            book_url_ext = book.css('h3 a::attr(href)').get()
            if 'catalogue/' in book_url_ext:
                book_url = self.start_urls[0] + book_url_ext
            else:
                book_url = self.start_urls[0] + 'catalogue/' + book_url_ext
            yield scrapy.Request(url=book_url, callback=self.parse_book)

        # handle pagination
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = self.start_urls[0] + next_page
            else:
                next_page_url = self.start_urls[0] + 'catalogue/' + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book(self, response):
        """
        _summary_

        Args:
            response (_type_): _description_

        Yields:
            _type_: _description_
        """
        book_item = BookItem()
        table_rows = response.css('table.table.table-striped tr')

        book_item['url'] = response.url,
        book_item['title'] = response.css('h1::text').get(),
        book_item['upc'] = table_rows[0].css('td::text').get(),
        book_item['product_type'] = table_rows[1].css('td::text').get(),
        book_item['price'] = response.css('p.price_color::text').get(),
        book_item['price_excluding_tax'] = table_rows[2].css('td::text').get(),
        book_item['price_including_tax'] = table_rows[3].css('td::text').get(),
        book_item['tax'] = table_rows[4].css('td::text').get(),
        book_item['availability'] = table_rows[5].css('td::text').get(),
        book_item['number_of_reviews'] = table_rows[6].css('td::text').get(),
        book_item['stars'] = response.css('p.star-rating').attrib['class'],
        book_item['category'] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']" \
                                    "/preceding-sibling::li[1]/a/text()").get(),
        book_item['description'] = response.xpath("//div[@class='sub-header']" \
                                        "/following-sibling::p/text()").get()
        yield book_item
