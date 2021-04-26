# Scrapy Project: Yunnan Sourcing

### [YunnanSourcing](https://yunnansourcing.com/) | [LinkedIn](https://www.linkedin.com/in/theodorecheek) | Blog Writeup

---------------------------------------------------

### Project Goals
The aim of this project is to collect and accurately collate the publicly available information on the store front of Yunnan Sourcing. What makes Yunnan Sourcing particularly remarkable beyond its enormity, is its dual focus on clear sourcing of many of its products as well as on "verified purchase reviews."

Effective analysis of these data would be of major assistance to any of the following:
- Small business owners getting into Tea Retail
- Mid-level retailers or cafes looking to increase their appeal to the higher-end crowd of tea connoisseurs
- International wholesalers, who are looking to find the next best source for their own wares, to edge in on the competition and corner their own network of tea and teaware producers

#### Tools Employed

Over the course of the web scraping, I employed many classic tools, including Scrapy, Regex, Xpath, and BeautifulSoup. Over the course of my analysis, which you can review in the Notebook I have provided, I made heavy use of Pandas, Numpy, Seaborne, and Matplotlib.

#### Techincal Challenges

While some information is readily available through typical Scrapy xpath techniques, much of the website's code is either outdated or extremely bespoke to its plugins, particularly that of Yotpo, which handles all of the review information. As such, Xpath is rendered useless for half of the data we require.

Upon closer inspection of the Network, however, I found that paging through the reviews sent iterative requests to a Yotpo server for the raw review information. In order to access the customer information, I employed Trillworks' Curl Converter to convert the cURL into Python POST requests. From here, I looped over the JSON information and successfully acquired the customer data.

### Data Analysis

I will omit the majority of my analysis here, however, should you wish to examine it, you may find a fuller breakdown HERE, at my official blog writeup.
