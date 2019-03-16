from multiprocessing import Pool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time




"""def obdelej(stran):
    return stran.find('h1').text.strip()

#zacetni frontier
frontier = ["evem.gov.si", "e-uprava.gov.si", "podatki.gov.si", "e-prostor.gov.si"]

work = []

start_time = time.time()

for url in frontier:
    #options da bo headless
    options = Options()
    options.headless = True

    driver = webdriver.Chrome(options=options)
    driver.get("http://www.gov.si/")
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    work.append(soup)
    driver.close()

end_time = time.time() - start_time
print(f"Time it took to fetch all websitest: {end_time}")

start_time = time.time()
p = Pool()
result = p.map(obdelej, work)
p.close()
p.join()

end_time = time.time() - start_time

print(result)"""

import itertools as it
import requests
from bs4 import BeautifulSoup

def get_links(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    return {e.get('href') for e in soup.find_all('a')
            if e.get('href') and e.get('href').startswith('https')}

links = get_links('https://www.nytimes.com')

with Pool() as p:
    links_on_pages = p.map(get_links, links)