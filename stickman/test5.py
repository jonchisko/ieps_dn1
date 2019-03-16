from threading import Thread
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from multiprocessing import Queue

"""def th(bs):
    rezultat = ""
    for tag in bs.find_all('title'):
        rezultat += tag.text
    return rezultat


urls = ["http://evem.gov.si", "http://podatki.gov.si", "http://e-prostor.gov.si"] #"http://e-uprava.gov.si"
delo = []
for url in urls:
    options = Options()
    options.headless = True

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, "lxml")
    delo.append(soup)

    print(f"Stored {url}")


q = Queue()
threadlist = []
print("printing")
for i in range(len(urls)):

    argument = delo[i]
    t = Thread(target=lambda q, arg1: q.put(th(arg1)), args=(q, argument))
    t.start()
    threadlist.append(t)

for th in threadlist:
    th.join()

while not q.empty():
    print(q.get())"""


class Crawler:

    def __init__(self, number_of_workers):
        self.threadnum = number_of_workers
        self.frontier = ["http://evem.gov.si", "http://podatki.gov.si", "http://e-prostor.gov.si"]
        self.q = Queue()
        self.workers = []
        self.waiting_for_processing = []


    def start_crawling(self):

        #create soup elements from sites in the frontier without parallel, because soup doesn't work in threads
        for url in self.frontier:
            options = Options()
            options.headless = True

            driver = webdriver.Chrome(options=options)
            driver.get(url)
            html = driver.page_source
            driver.close()
            soup = BeautifulSoup(html, "lxml")
            self.waiting_for_processing.append(soup)

            print(f"Stored {url}")

        #launch threads for working
        for unprocessed in self.waiting_for_processing[:self.threadnum]:
            t = Thread(target=self.store_processed_to_queue(unprocessed), args=(unprocessed))
            t.start()
            self.workers.append(t)

        #wait for workers to finish
        for thread in self.workers:
            thread.join()


        #print out the results of crawling on lvl 1
        while not self.q.empty():
            print(self.q.get())

    def store_processed_to_queue(self, soup):
        self.q.put(self.process_soup(soup))


    def process_soup(self, soup):
        rezultat = []
        for tag in soup.find_all('title'):
            rezultat.append(tag.text)
        return rezultat


crw = Crawler(3)

crw.start_crawling()