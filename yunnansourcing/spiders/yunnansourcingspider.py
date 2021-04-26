from scrapy import Spider, Request
from yunnansourcing.items import YunnansourcingItem
from bs4 import BeautifulSoup
import re
import math
import requests
import time

# test shell command
# scrapy shell -s USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36" "https://yunnansourcing.com/collections/all-loose-leaf-teas/products/yunnan-black-gold-bi-luo-chun-black-tea"

my_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"

# found review urls  --- ?yoReviewsPage=1 fine

class YunnanSourcing_Spider(Spider):
    name = 'YunnanSourcing_Spider'
    allowed_urls = ['https://yunnansourcing.com']
    start_urls = ['https://yunnansourcing.com/collections']

    def parse(self, response):
        # collect YS collection urls
        url_extensions = response.xpath('//div[@class="blocklayout"]/div/div/a/@href').extract()
        coll_urls = ['https://yunnansourcing.com' + i for i in url_extensions]

        # collate collection urls & sizes into dict; product_url: coll_size
        coll_size_text = response.xpath('//div[@class="blocklayout"]//div[@class="meta"]/p/text()').extract()
        coll_size = [int(coll.split(' ')[0]) for coll in coll_size_text]

        product_dict = dict(zip(coll_urls, coll_size))

        # create result_urls; adjust for 24 products per page, combine page urls
        result_urls = []
        for prod in list(product_dict.keys()):
            product_dict[prod] = math.ceil(product_dict[prod] / 24)
            templist = [prod + f"?page={i+1}" for i in range(product_dict[prod])]
            result_urls.extend(templist)

        for url in result_urls:
            yield Request(url=url, callback=self.parse_collection_page)

    def parse_collection_page(self, response):
        product_urls = response.xpath('//div[@class="blocklayout do-infinite"]/div/div/a/@href').extract()
        product_urls = ['https://yunnansourcing.com' + i for i in product_urls]

        # grab collection name into meta
        collection = response.xpath('//div[@class="inner"]/h1/text()').extract_first().strip()
        meta = {'collection': collection}

        print('='*55)
        print('Number of Products in the collection: ')
        print(len(product_urls))
        print(collection)
        print('='*55)

        for url in product_urls:
            yield Request(url=url, callback=self.parse_product_page, meta=meta)

    def parse_product_page(self,response):
        item_name = response.xpath('//div[@class="padded cf"]//h1/text()').extract_first()
        brand = response.xpath('//div[@class="padded cf"]//p/span/a/text()').extract_first()
        tags = response.xpath('//div[@class="morelinks section"]/div[2]/a/text()').extract()
        display_price = response.xpath('//div[@class="pricearea"]/span/span/text()').extract_first()
        try:
            wishlist_score = response.xpath('//div[@class="div-wishlist"]/div/input').attrib['value']
        except:
            wishlist_score = '0'
        item_type = response.xpath('//div[@class="morelinks section"]/div/a/text()').extract_first()
        pid = response.xpath('//*[@id="content"]/div[2]/@data-product-id').extract_first()
        notes = response.xpath('//div[@class="descriptionunder padded"]//p/text()').extract_first()

        ########## BeautifulSoup for Bad HTML Pricing ############
        tea_soup = BeautifulSoup(response.body, 'html5lib')

        # find price options available; oddly BS saves a step vs xpath
        price_options = tea_soup.find_all('option', {'data-sku': ''})
        price_strings = [tag.string for tag in price_options][18:]

        ########## Yotpo Info Grabbing ##########
        # construct headers & data for initial yotpo post request
        general_method = '[{"method":"main_widget","params":{"pid":"' + pid + '","order_metadata_fields":{},"index":0}},{"method":"bottomline","params":{"pid":"' + pid + '","link":"' + response.url +  '","skip_average_score":false,"main_widget_pid":"' + pid +          '","index":1}},{"method":"badge","params":{"pid":null,"index":2}}]'
        headers = {
            'authority': 'staticw2.yotpo.com',
            'accept': 'application/json',
            'user-agent': my_agent,
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://yunnansourcing.com',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': response.url,
            'accept-language': 'en-US,en;q=0.9'
        }
        data = {
            'methods': general_method,
            'app_key': 'E0M5FDBP9ujse59Fej4iFkR48YWRjCA43IXPzFeb',
            'is_mobile': 'false',
            'widget_version': '2019-10-17_08-00-18'
        }

        # Make post request & jsonify the results
        yot_data = requests.post('https://staticw2.yotpo.com/batch', headers=headers, data=data)
        yot_data = yot_data.json()
        yot_soup = BeautifulSoup(yot_data[0]['result'], 'html5lib')

        star_soup = BeautifulSoup(yot_data[1]['result'], 'html5lib')
        starscore = star_soup.find('span', {'class': 'sr-only'}).text
        starscore = re.findall('\d+', starscore)
        starscore = float(starscore[0] + '.' + starscore[1])

        # Calculate range of review pages
        try:
            total_revs = yot_soup.find('span', {'class': 'reviews-amount'}).text.strip()
            total_revs = int(re.findall('\d+', total_revs)[0])
            total_revpages = math.ceil(total_revs / 5)
        except:
            total_revs = 0
            total_revpages = 1

        try:
            amount = re.search('(.+?) /', price_strings[0]).group(1)
        except:
            amount = '1 Unit'

        ##########Loop to grab review info##########
        # assign empty lists & loop to fill
        review_names = []
        review_titles = []
        review_scores = []
        review_texts = []
        review_dates = []
        review_helpful = []
        review_unhelpful = []

        # Loop & pour BeautifulSoup over every review response
        for i in range(total_revpages):
            # iterate post request data; headers are the same as before
            review_method = '[{"method":"main_widget","params":{"pid":"' + pid + '","page":' + str(i+1) + ',"order_metadata_fields":{},"index":0,"host-widget":"main_widget","is_mobile":false,"pictures_per_review":10}}]'
            data = {
                'methods': review_method,
                'app_key': 'E0M5FDBP9ujse59Fej4iFkR48YWRjCA43IXPzFeb',
                'is_mobile': 'false',
                'widget_version': '2019-10-17_08-00-18'
            }

            # make soup
            loop_data = requests.post('https://staticw2.yotpo.com/batch', headers=headers, data=data)
            loop_data = loop_data.json()
            loop_soup = BeautifulSoup(loop_data[0]['result'], 'html5lib')

            # collect information
            loop_scores = loop_soup.find_all('span', {'class': 'sr-only', 'id': ''})[12:]
            loop_names = loop_soup.find_all('span', {'class': 'y-label yotpo-user-name yotpo-font-bold pull-left'})[1:6]
            loop_titles = loop_soup.find_all('div', {'class': 'content-title yotpo-font-bold'})[1:6]
            loop_texts = loop_soup.find_all('div', {'class': 'content-review'})[1:]
            loop_dates = loop_soup.find_all('span', {'class': 'y-label yotpo-review-date'})[2:]
            loop_helpful = loop_soup.find_all('span', {'class': 'y-label yotpo-sum vote-sum', 'data-type': 'up'})[1:6]
            loop_unhelpful = loop_soup.find_all('span', {'class': 'y-label yotpo-sum vote-sum', 'data-type': 'down'})[1:6]

            review_scores.extend([int(loop_scores[i].string[0]) for i in range(0, len(loop_scores))])
            review_names.extend([tag.string.strip() for tag in loop_names])
            review_titles.extend([tag.string.strip() for tag in loop_titles])
            review_texts.extend([tag.get_text().strip() for tag in loop_texts])
            review_dates.extend([loop_dates[i].text.strip() for i in range(0, len(loop_dates), 2)])
            review_helpful.extend([int(loop_helpful[i].string[0]) for i in range(0, len(loop_helpful))])
            review_unhelpful.extend([int(loop_unhelpful[i].string[0]) for i in range(0, len(loop_unhelpful))])

            print('Page ' + str(i+1) + ' done')
            time.sleep(1) # sleep for 1 second between post requests

        # fix owner comments in texts & dates
        owner_comments = [pos for pos,com in enumerate(review_texts) if "- Scott" in com]
        for comment in owner_comments:
            del review_texts[comment]
            del review_dates[comment]

        # Test Prints

        ##########Tie it all together##########
        item = YunnansourcingItem()

        # testprints
        print('='*55)
        print('Item Name: ' + item_name)
        print('Brand: ' + brand)
        print('Display Price: ' + display_price)
        print('Wishlist Score: ' + wishlist_score)
        print('Item type: ' + item_type)
        print('This is the PID Number: ' + pid)
        print('Tags:')
        print(tags)
        print('='*55)
        print('Total Reviews: ' + str(total_revs))
        print('Number of Rev Texts: ' + str(len(review_texts)))
        if len(review_texts) != total_revs:
            print('*' * 55)
            print('COME ON, SCOTT')
            print('*' * 55)
        print('='*55)

        item['pid'] = pid
        item['item_name'] = item_name
        item['collection'] = response.meta['collection']
        item['item_type'] = item_type
        item['display_price'] = display_price
        item['amount'] = amount
        item['pricing'] = price_strings
        item['brand'] = brand
        item['tags'] = tags
        item['wishlist_score'] = wishlist_score
        item['starscore'] = starscore
        item['review_scores'] = review_scores
        item['review_names'] = review_names
        item['review_titles'] = review_titles
        item['review_texts'] = review_texts
        item['review_dates'] = review_dates
        item['review_helpful'] = review_helpful
        item['review_unhelpful'] = review_unhelpful

        yield item
