import lxml
import requests
from bs4 import BeautifulSoup as BSoup
domain_country = 'https://www.aviasales.ru/countries'
domain_city = 'https://www.aviasales.ru/cities'
domain_prices = 'https://www.aviasales.ru/search/SVX2701IST16021?adults=1&center=98.189%2C68.148&checkin=2023-12-27&checkout=2024-01-19&children=&zoom=1.67'
tags_base_country = set()
tags_base_city = set()
# tags_base_prices = set()
def crawling ():
    response_country = requests.get(domain_country)
    site_content_country = BSoup(response_country.content, 'html.parser')
    for link_county in site_content_country.select(".index-list__table-wrap ul li a"):
        county_name = str(link_county.text).replace('\n','').lower()
        if ' и ' in county_name:
            county_name1,county_name2 = county_name.split(' и ')
            tags_base_country.add(county_name1)
            tags_base_country.add(county_name2)
        else:
            tags_base_country.add(county_name)

    response_city = requests.get(domain_city)
    site_content_city = BSoup(response_city.content, 'html.parser')
    for link_city in site_content_city.select(".index-list__table-wrap ul li a"):
        city_name = str(link_city.text).lower()
        tags_base_city.add(city_name)

    # response_prices = requests.get(domain_prices)
    # site_content_prices = BSoup(response_prices.content, 'html.parser')
    # for link_prices in site_content_prices.select(".minimized-calendar-matrix__item is-current"):
    #     prices_name = str(link_prices.text).lower()
    #     tags_base_prices.add(prices_name)



if __name__ == '__main__':
    crawling()
    # print(len(tags_base_prices))