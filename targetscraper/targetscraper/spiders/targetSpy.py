import time
import scrapy
import re
import json
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
        product={}
        try:
            script = soup.find("script", {"type": "application/ld+json"}).text
            data = json.loads(script)
            for index in data["@graph"]:
                product['title'] = index["name"]
                product['TCIN'] = index["sku"]
                product['description'] = index["description"]
                product['UPC'] = index["gtin13"]
                product['Price'] = index["offers"]["price"]
                product['currency'] = index["offers"]["priceCurrency"]
                product['url'] = index["offers"]["url"]

        except:
            product['description']=response.xpath("//div[@data-test='item-details-description']//text()").getall()
            product['title']=response.xpath("//h1[@data-test='product-title']//text()").get()
            product['currency']="USD"
            product['url'] = response.url
            try:
                product['Price'] = soup.find("span", {"data-test": "product-price"}).text.split("$")[-1]
            except:
                pass

            try:
                product_tabs = soup.find('div', {"id": "product-details-tabs"}).find("div", {'id': "tabContent-tab-Details"}).find("div", {"data-test": "item-details-specifications"}).find_all("div")
                for prodindex in product_tabs:
                    if re.search(r'(?i)TCIN:', prodindex.text):
                        product['TCIN'] = prodindex.text.split(":")[-1]

                    if re.search(r'(?i)UPC', prodindex.text):
                        product['UPC'] = prodindex.text.split(":")[-1]
            except:
                pass

        try:
            script = soup.find_all("script")
            # ingredients = []
            # spec = []
            for index in script:
                if re.search(r'(?i)window.__TGT_DATA__', index.text):
                    data = index.text
                    try:
                        start = data.find("ingredients")
                        end = data.find("nutrition_label_type_code")
                        ingre = data[start:end]
                        # ingredients.append(ingre)
                        product["ingredients"] = ingre
                    except:
                        pass
                    try:  # spec
                        start = data.find("nutrients")
                        end = data.find("videos")
                        Tempspec = data[start:end]
                        product["spec"]=Tempspec
                        # spec.append(Tempspec)
                    except:
                        pass

                else:
                    pass
        except:
            pass

        if len(product) > 0:
            yield product
        else:
            print(response.url)




