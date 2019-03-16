from multiprocessing import Pool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Crawler:

    def __init__(self, num_of_workers):
        self.frontier = ["evem.gov.si", "e-uprava.gov.si", "podatki.gov.si", "e-prostor.gov.si"]
        self.rezultati = [[] for i in range(num_of_workers)]
        options = Options()
        options.headless = True

        driver = webdriver.Firefox(options=options)
        # driver.get("https://www.rtvslo.si/")
        driver.get("http://www.gov.si/")
        # driver.get("https://www.pexels.com/search/beauty/")
        html = driver.page_source
        soup = BeautifulSoup(html)
        for tag in soup.find_all('title'):
            print(tag.text)


    def start_crawling(self):


    def worker(self, ):