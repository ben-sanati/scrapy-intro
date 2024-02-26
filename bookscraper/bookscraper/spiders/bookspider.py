"""
_summary_
"""
import scrapy


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
        star_conversion = {
            'One': 1,
            'Two': 2,
            'Three': 3,
            'Four': 4,
            'Five': 5,
        }
        table_rows = response.css('table.table.table-striped tr')
        star_rating_class = response.css('p.star-rating').attrib['class']

        yield {
            'url': response.url,
            'title': response.css('h1::text').get(),
            'UPC': table_rows[0].css('td::text').get(),
            'Product Type': table_rows[1].css('td::text').get(),
            'Price': response.css('p.price_color::text').get(),
            'Price Excluding Tax': table_rows[2].css('td::text').get(),
            'Price Including Tax': table_rows[3].css('td::text').get(),
            'Tax': table_rows[4].css('td::text').get(),
            'Availability': table_rows[5].css('td::text').get(),
            'Number of Reviews': table_rows[6].css('td::text').get(),
            'Stars': star_conversion[star_rating_class.split(' ')[1]],
            'Category': response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
            'Description': response.xpath("//div[@class='sub-header']/following-sibling::p/text()").get()
        }
