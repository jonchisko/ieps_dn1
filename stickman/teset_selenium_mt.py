import os

if os.name == "nt":
    from pars import *
    from robots_test import *
elif os.name == "posix":
    from parser.pars import *
    from stickman.robots_test import *

from threading import Thread
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from multiprocessing import Queue

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
        self.frontier = ["http://evem.gov.si", "http://e-uprava.gov.si", "http://podatki.gov.si", "http://e-prostor.gov.si"]
        self.q = Queue()
        self.workers = []
        self.visited = set(["http://evem.gov.si", "http://e-uprava.gov.si", "http://podatki.gov.si", "http://e-prostor.gov.si"])


    def start_crawling(self):
        iii = 5
        while iii > 0:

            #launch workers
            for url in self.frontier[:self.threadnum]:
                t = Thread(target=self.store_processed_to_queue, args=(url,))
                t.start()
                self.workers.append(t)

            #TODO: Delete this when you are certain that the above for loop works
            """for unprocessed in self.waiting_for_processing[:self.threadnum]:
                t = Thread(target=self.store_processed_to_queue(unprocessed), args=(unprocessed))
                t.start()
                self.workers.append(t)"""

            #wait for workers to finish
            for thread in self.workers:
                thread.join()
            print(f"The length of the frontier is {len(self.frontier)}")
            #we have to remove the visited sites from the frontier
            #we also have to remove the stored bs for sites
            for i in range(self.threadnum):
                del self.frontier[0]


            print("Pobiram rezultat")
            #print out the results of crawling on lvl 1
            #the parser returns (url, set(urls), set(files), set(images))
            #now we have to empty the q, store stuff to the data base in feed everything to the frontier correctly
            while not self.q.empty():

                original_url, links, files, images = self.q.get()

                print(f"Adding links from {original_url} to frontier:")
                for link in links:
                    if link not in self.visited:
                        self.visited.add(link)
                        print(f"   - added: {link}")
                        self.frontier.append(link)

            iii -= 1

    def store_processed_to_queue(self, url):

        # set options for headless browsing
        print(f"Working for {url}")
        options = Options()
        options.headless = True

        # check for robots.txt and parse if exists
        rh = RobotsTxtHandler(url)

        # sleep for the crawl_delay, default 4s
        time.sleep(rh.crawl_delay)

        # set up the driver
        driver = webdriver.Chrome(options=options)

        # fetch html
        driver.get(url)
        html = driver.page_source

        # close driver
        driver.close()

        # add url to visited
        self.visited.add(url)

        # store html to soup and save it for multithreaded processing
        soup = BeautifulSoup(html, "lxml")

        self.q.put(self.parsePage(url, soup, rh.disallow))

        print(f"Done working for {url}")

    def process_soup(self, soup):
        rezultat = []
        for tag in soup.find_all('title'):
            rezultat.append(tag.text)
        return rezultat

    # en process soup, k sam sparsa - dodal user: jon skoberne
    def parsePage(self, url, soup, robots):
        urlSet, fileSet, imgSet = htmlGetAll.doPage(url, soup, robots)
        #TODO: check if unique urls, insert files, imgs into db
        return url, urlSet, fileSet, imgSet

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
    def checkPage(self, url):
        # get http head
        # head = requests.head(url)
        pass

    # get page
    def getPage(self, url):
        pass


crw = Crawler(4)

crw.start_crawling()

