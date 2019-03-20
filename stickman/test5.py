from threading import Thread
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from multiprocessing import Queue
from pars import htmlGetAll
from robots_test import *
import time
import requests

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

            #set options for headless browsing
            options = Options()
            options.headless = True

            #check for robots.txt and parse if exists
            rh = RobotsTxtHandler(url)

            #sleep for the crawl_delay, default 4s
            time.sleep(rh.crawl_delay)

            #set up the driver
            driver = webdriver.Chrome(options=options)

            #fetch html
            driver.get(url)
            html = driver.page_source

            #close driver
            driver.close()


            #store html to soup and save it for multithreaded processing
            soup = BeautifulSoup(html, "lxml")
            self.waiting_for_processing.append(soup)

            print(f"Stored BS for: {url}")

        #launch workers
        for i in range(len(self.waiting_for_processing[:self.threadnum])):
            t = Thread(target=self.store_processed_to_queue(self.frontier[i], self.waiting_for_processing[i], rh.disallow))
            t.start()
            self.workers.append(t)
        """for unprocessed in self.waiting_for_processing[:self.threadnum]:
            t = Thread(target=self.store_processed_to_queue(unprocessed), args=(unprocessed))
            t.start()
            self.workers.append(t)"""

        #wait for workers to finish
        for thread in self.workers:
            thread.join()


        #print out the results of crawling on lvl 1
        while not self.q.empty():
            print(self.q.get())

    def store_processed_to_queue(self, url, soup, robots):
        self.q.put(self.parsePage(url, soup, robots))


    def process_soup(self, soup):
        rezultat = []
        for tag in soup.find_all('title'):
            rezultat.append(tag.text)
        return rezultat

    # en process soup, k sam sparsa - dodal user: jon skoberne
    def parsePage(self, url, soup, robots):
        urlSet, fileSet, imgSet = htmlGetAll.doPage(url, soup, robots)
        #TODO: check if unique urls, insert files, imgs into db
        return urlSet, fileSet, imgSet

    # en process soup, k tud geta pa sparsa - dodal user: jon skoberne
    def getParsePage(self, url):
        #TODO:everything
        # urllib request apparently works in threads, so this is for threads
        response = requests.get(url, verify=False, allow_redirects=True, timeout=50)
        soup = BeautifulSoup(response.text, "lxml")
        robots = []
        urlSet, fileSet, imgSet = htmlGetAll.doPage(url, soup, robots)
        # TODO: status codes, check if unique urls, insert files, imgs into db

    # function checks if page needs selenium
    def getPage(self, url):
        # get http head
        # head = requests.head(url)
        pass

    # get page with requests
    def getPageR(self, url):
        pass

    # get page with selenium
    def getPageS(self, url):
        pass

crw = Crawler(3)

crw.start_crawling()