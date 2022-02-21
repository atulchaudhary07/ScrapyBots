import time
import scrapy
import re
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager #pip install webdriver-manager
import time
from selenium import webdriver

class DemospySpider(scrapy.Spider):
    name = 'target'
    allowed_domains = ['www.target.com']
    def __init__(self, url=None, *args, **kwargs):
        super(DemospySpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'{url}']


    def parse(self, response, **kwargs):
        service = Service(executable_path=ChromeDriverManager().install())
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(response.url)
        time.sleep(7)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        description=response.xpath("//div[@data-test='item-details-description']//text()").getall()
        title=response.xpath("//h1[@data-test='product-title']//text()").get()
        currency="USD"
        try:
            script = soup.find_all("script")
            ingredients = []
            spec = []
            for index in script:
                if re.search(r'(?i)window.__TGT_DATA__', index.text):
                    data = index.text
                    try:
                        start = data.find("ingredients")
                        end = data.find("nutrition_label_type_code")
                        ingre = data[start:end]
                        ingredients.append(ingre)
                    except:
                        pass
                    try:  # spec
                        start = data.find("nutrients")
                        end = data.find("videos")
                        Tempspec = data[start:end]
                        spec.append(Tempspec)
                    except:
                        pass

                else:
                    pass

        except:
            pass

        try:
            product_price = soup.find("span",{"data-test":"product-price"}).text.split("$")[-1]
        except:
            pass

        try:
            product_tabs=soup.find('div',{"id":"product-details-tabs"}).find("div",{'id':"tabContent-tab-Details"}).find("div",{"data-test":"item-details-specifications"}).find_all("div")
            for prodindex in product_tabs:

                if re.search(r'(?i)TCIN:',prodindex.text):
                    TCIN=prodindex.text.split(":")[-1]


                if re.search(r'(?i)UPC',prodindex.text):
                    upc=prodindex.text.split(":")[-1]
        except:
            pass

        yield {
                'url':response.url,
                'description':description,
                'TCIN':TCIN,
                'upc':upc,
                'title':title,
                'currency':currency,
                'product_price':product_price,
                'Ingredients':ingredients,
                'spec':spec
                }




