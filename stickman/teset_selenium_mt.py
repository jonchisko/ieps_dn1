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
from URLclasses import URL, Site
from urllib.parse import urlparse
import time
import requests

class Crawler:

    def __init__(self, number_of_workers):
        self.threadnum = number_of_workers
        self.frontier = ["http://evem.gov.si", "http://e-uprava.gov.si", "http://podatki.gov.si", "http://e-prostor.gov.si"]
        self.q = Queue()
        self.workers = []
        self.visited = set()
        self.sites = dict()

    def check_for_existing_site(self, url):
        return urlparse(url).netloc in self.sites

    def start_crawling(self):
        iii = 5
        while iii > 0:

            #launch workers
            for url in self.frontier[:self.threadnum]:
                t = Thread(target=self.store_processed_to_queue, args=(url,))
                t.start()
                self.workers.append(t)

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

                print(f"Adding links from {original_url.url} to frontier:")
                for link in links:
                    if link not in self.visited:
                        self.visited.add(link)
                        print(f"   - added: {link}")
                        self.frontier.append(link)

            iii -= 1
    """
    class Site:

    def __init__(self, allow, disallow, sitemap, delay, site_id):
        self.allow = allow
        self.disallow = disallow
        self.sitemap = sitemap
        self.delay = delay
        self.site_id = site_id

class URL:

    def __init__(self, url, allow, disallow, delay, site_id): #, page_id, html):
        self.url = url
        self.domain = urlparse(url).netloc
        self.acces_time = time.time()
        self.allow = allow
        self.disallow = disallow
        self.delay = delay
        self.site_id = site_id
        self.page_id = None
        self.html = None
    
    """
    def store_processed_to_queue(self, url):

        # set options for headless browsing
        options = Options()
        options.headless = True

        current_domain = urlparse(url).netloc

        #ce mamo ze site za ta page ne rabimo iskat robotsov itd
        #samo nrdimo instanco page-a
        if self.check_for_existing_site(url):
            url_class_instance = URL(url, self.sites[current_domain].allow, self.sites[current_domain].disallow, self.sites[current_domain].delay, self.sites[current_domain].site_id)
            print(f"Working for {url}: \n        We already know this domain, we have to avoid {len(self.sites[current_domain].disallow)} urls\n        We can visit {len(self.sites[current_domain].allow)} sites\n        We have to obey the crawl delay which is {self.sites[current_domain].delay}\n")
        else:
            #v tem primeru pa se nimamo site in je treba narest najprej treba dobit robotse za domeno strani
            rh = RobotsTxtHandler("http://" + current_domain)
            allow, disallow, sitemap = rh.allow, rh.disallow, rh.sitemap

            #instancirat domeno strani
            site = Site(allow, disallow, sitemap, rh.crawl_delay, None)

            #dodat site v vse site
            self.sites[current_domain] = site

            #narest se class url za obdelavo
            url_class_instance = URL(url, self.sites[current_domain].allow, self.sites[current_domain].disallow, self.sites[current_domain].delay, self.sites[current_domain].site_id)
            print(f"Working for {url}: \n        This is the first time visiting this domain, we have to avoid {len(self.sites[current_domain].disallow)} urls\n        We can visit {len(self.sites[current_domain].allow)} sites\n        We have to obey the crawl delay which is {self.sites[current_domain].delay}\n")



        # sleep for the crawl_delay, default 4s
        time.sleep(url_class_instance.delay)

        # set up the driver
        driver = webdriver.Chrome(options=options)

        # fetch html
        driver.get(url)
        html = driver.page_source
        url_class_instance.set_html(html)

        # close driver
        driver.close()

        # add url to visited
        self.visited.add(url)

        # store html to soup and save it for multithreaded processing
        soup = BeautifulSoup(html, "lxml")

        self.q.put(self.parsePage(url_class_instance, soup))

        print(f"Done working for {url}")

    def process_soup(self, soup):
        rezultat = []
        for tag in soup.find_all('title'):
            rezultat.append(tag.text)
        return rezultat

    # en process soup, k sam sparsa - dodal user: jon skoberne
    def parsePage(self, url_class_instance, soup):
        url = url_class_instance.url
        robots = url_class_instance.disallow
        urlSet, fileSet, imgSet = htmlGetAll.doPage(url, soup, robots)
        #TODO: check if unique urls, insert files, imgs into db
        return url_class_instance, urlSet, fileSet, imgSet

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

