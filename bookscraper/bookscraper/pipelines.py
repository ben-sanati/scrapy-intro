# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import configparser
import mysql.connector
from mysql.connector import errorcode

from itemadapter import ItemAdapter


class BookscraperPipeline:
    adapter: ItemAdapter

    def process_item(self, item, spider):
        self.adapter = ItemAdapter(item)
        self._strip_whitespace()
        self._lower_case()
        self._clean_price_data()
        self._extract_availability()
        self._str_to_int()
        self._stars_to_int()
        return item

    def _strip_whitespace(self):
        ## Strip all whitespaces from strings
        field_names = self.adapter.field_names()
        for field_name in field_names:
            if field_name != 'description':
                value = self.adapter.get(field_name)[0]
                self.adapter[field_name] = value.strip()

    def _lower_case(self):
        ## Category & Product Type --> switch to lowercase
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = self.adapter.get(lowercase_key)
            self.adapter[lowercase_key] = value.lower()

    def _clean_price_data(self):
        ## Price --> convert to float
        price_keys = ['price', 'price_excluding_tax', 'price_including_tax', 'tax']
        for price_key in price_keys:
            value = self.adapter.get(price_key)
            value = value.replace('£', '')
            self.adapter[price_key] = float(value)

    def _extract_availability(self):
        ## Availability --> extract number of books in stock
        availability_string = self.adapter.get('availability')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            self.adapter['availability'] = 0
        else:
            availability_array = split_string_array[1].split(' ')
        self.adapter['availability'] = int(availability_array[0])

    def _str_to_int(self):
        ## Reviews --> convert string to number
        num_reviews_string = self.adapter.get('number_of_reviews')
        self.adapter['number_of_reviews'] = int(num_reviews_string)

    def _stars_to_int(self):
        ## Stars --> convert text to number
        star_converter = {
            "zero": 0,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5
        }

        stars_string = self.adapter.get('stars')
        split_stars_array = stars_string.split(' ')
        stars_text_value = split_stars_array[1].lower()
        self.adapter['stars'] = star_converter[stars_text_value]


class SaveToMySQLPipeline:
    def __init__(self):
        # setup connection to MYSQL database
        config = configparser.ConfigParser()
        config.read('secrets.cfg')

        self.conn = mysql.connector.connect(
            host="localhost",
            user=config['secrets']['mysql_user'],
            password=config['secrets']['mysql_password'],
            database="books"
        )
        self.cursor = self.conn.cursor()

        # Create books table if none exists
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id int NOT NULL auto_increment, 
            url VARCHAR(255),
            title text,
            upc VARCHAR(255),
            product_type VARCHAR(255),
            price DECIMAL,
            price_excluding_tax DECIMAL,
            price_including_tax DECIMAL,
            tax DECIMAL,
            availability INTEGER,
            number_of_reviews INTEGER,
            stars INTEGER,
            category VARCHAR(255),
            description text,
            PRIMARY KEY (id)
        )
        """)

    def process_item(self, item, spider):
        ## Define insert statement
        self.cursor.execute(""" insert into books (
            url,
            title,
            upc,
            product_type,
            price,
            price_excluding_tax,
            price_including_tax,
            tax,
            availability,
            number_of_reviews,
            stars,
            category,
            description
            ) values (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
                )""", (
            item["url"],
            item["title"],
            item["upc"],
            item["product_type"],
            item["price"],
            item["price_excluding_tax"],
            item["price_including_tax"],
            item["tax"],
            item["availability"],
            item["number_of_reviews"],
            item["stars"],
            item["category"],
            str(item["description"])
        ))

        ## Execute insert of data into database
        self.conn.commit()
        return item

    def close_spider(self, spider):
        # Close cursor & connection to database 
        self.cursor.close()
        self.conn.close()
