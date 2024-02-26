import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        # get data from books.toscrape.com
        books = response.css('article.product_pod')
        for book in books:
            yield {
                'title': book.css('h3 a::attr(title)').get(),
                'price': book.css('p.price_color::text').get(),
                'url': book.css('h3 a::attr(href)').get(),
            }

        # handle pagination
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = self.start_urls[0] + next_page
            else:
                next_page_url = self.start_urls[0] + 'catalogue/' + next_page
            yield response.follow(next_page_url, callback=self.parse)
