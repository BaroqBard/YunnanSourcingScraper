# Scrapy Project: Yunnan Sourcing

### [YunnanSourcing](https://yunnansourcing.com/) | [LinkedIn](https://www.linkedin.com/in/theodorecheek)

---------------------------------------------------

### This project is presently under construction.
I shall provide more information as it becomes relevant and available.
Feel free to provide any constructive advice in the meantime. Just drop me a message at theodore.m.cheek@gmail.com

---------------------------------------------------

### Project Goals
The aim of this project is to collect and accurately collate the publicly available information on the store front of Yunnan Sourcing. What makes this source of reviews and product information remarkable is that it appears to be one of the most complete, public resources covering tea and its sourcing on the web.

Properly organized and interpreted, information gathered in this way could be used to better inform the decision making of leading retailers as well as supply vendors.

### Technical Details & Challenges
While some information is readily available through typical Scrapy xpath techniques, much of the webiste's code is either outdated or extremely bespoke to its plugins, most particularly that of Yotpo, rendering the majority of its data either difficult or completely impossible to access normally.

In order to gain access, I employed modular post requests, which would yield the review and product information in JSON formats. From there, I distilled these into BeautifulSoup objects and parsed the results in the classical fashion.

### Data & Utility Available
