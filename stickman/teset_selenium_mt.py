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

    def __init__(self, seeds, number_of_workers):
        self.threadnum = number_of_workers
        self.seeds = seeds
        self.frontier = []
        self.q = Queue()
        self.workers = []
        self.visited = set()
        self.sites = dict()

    def check_for_existing_site(self, url):
        return urlparse(url).netloc in self.sites


    #This functions has to be called before we start crawling. It takes the seed urls and parses them and inserts them into the frontier

    def setup_crawler(self):
        print("Setting up the crawler by adding seeds to the frontier.")

        for url in self.seeds:

            # narest se class url za obdelavo
            url_class_instance = self.domain_checking(url)

            self.frontier.append(url_class_instance)

    def start_crawling(self):
        iii = 5
        while iii > 0:

            #launch workers
            workers = self.threadnum if len(self.frontier) >= self.threadnum else len(self.frontier)
            for url_class_instance in self.frontier[:workers]:
                t = Thread(target=self.store_processed_to_queue, args=(url_class_instance,))
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


            print("            Pobiram rezultat               ")
            #print out the results of crawling on lvl 1
            #the parser returns (url, set(urls), set(files), set(images))
            #now we have to empty the q, store stuff to the data base in feed everything to the frontier correctly
            while not self.q.empty():

                #tukej updejtas original_url pa addas otroke
                original_url, links, files, images = self.q.get()

                print(f"Adding links from {original_url.url} to frontier:")

                ##########################################
                #treba je pohendlat se zacetek!!!!!!!!!!!#
                ##########################################

                #okej zdej vse radi. zdej rabmo pa update pa dodat
                #TODO: v bazi je treba updejtat podatke od original_url
                    #- UpdateDataInDBFor(original_url.page_id)
                    #- Spremenit mores polja:
                        #- page_type_code FRONTIER -> HTML
                        #- html_content Null -> original_url.html
                        #- html_status_code  Null -> original_url.html_status_code
                #zdej je zrihtan original html in je to to


                for link in links:

                    #preverja ce smo ze obiskali tocno tak url
                    #ce se nismo ga uzamemo, instanciramo url_class_instance in ga dodamo v bazo in na frontier
                    if link not in self.visited:
                        self.visited.add(link)
                        print(f"   - added: {link}")

                        #instanciran
                        url_class_instance = self.domain_checking(link)
                        #dodan na frontier
                        self.frontier.append(url_class_instance)

                        #TODO: v bazo je treba dodat url_class_instace ampak brez dolocenih polji, ker jih bomo dodali potem ko bo evalviran iz frontierja
                            #- site_it dobis iz url_class_instance.site_id
                            #- page_type_code je FRONTIER
                            #- url je url_class_instance.url
                            #- html_content je Null
                            #- html_status_code je Null
                            #- accessed_time je Null

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

    #Preveri ce smo domeno ze shranili
    #Ce je nismo jo shrani lokalno in v bazo doda site
    def domain_checking(self, url):

        current_domain = urlparse(url).netloc

        # ce mamo ze site za ta page ne rabimo iskat robotsov itd
        # samo nrdimo instanco page-a
        if self.check_for_existing_site(url):
            url_class_instance = URL(url, self.sites[current_domain].allow, self.sites[current_domain].disallow,
                                     self.sites[current_domain].delay, self.sites[current_domain].site_id)
        else:
            # v tem primeru pa se nimamo site in je treba narest najprej treba dobit robotse za domeno strani
            rh = RobotsTxtHandler("http://" + current_domain)
            allow, disallow, sitemap = rh.allow, rh.disallow, rh.sitemap

            # instancirat domeno strani
            site = Site(url, allow, disallow, sitemap, rh.crawl_delay)

            #TODO: tukej dodej v bazo ta site. Rabis:
                #- domain kar dobis z site.domain
                #- robots kar dobis z allows, disallows, sitemap = site.get_robots_string()

            #TODO: zdej mores se eno poizvedbo narest da dobis vn site id
                #sepravi a = GetSiteIDFromDB
                #site.set_site_id(a)

            # dodas site v vse site
            self.sites[current_domain] = site

            # narest se class url za obdelavo
            url_class_instance = URL(url, site.allow, site.disallow, site.delay, site.site_id)

        return url_class_instance

    def store_processed_to_queue(self, url_class_instance):
        #print(f"Working for {url_class_instance.url}\n   Delay: {url_class_instance.delay}\n   Allow: {len(url_class_instance.allow)}\n   Disllow: {len(url_class_instance.disallow)}\n")
        # set options for headless browsing
        options = Options()
        options.headless = True

        # sleep for the crawl_delay, default 4s
        time.sleep(url_class_instance.delay)

        # set up the driver
        driver = webdriver.Chrome(options=options)

        #get the status code
        r = requests.get(url_class_instance.url)
        url_class_instance.set_html_status_code(r.status_code)

        # fetch html
        driver.get(url_class_instance.url)
        html = driver.page_source
        url_class_instance.set_html(html)
        url_class_instance.set_time(time.time())


        # close driver
        driver.close()

        # add url to visited
        self.visited.add(url_class_instance.url)

        # store html to soup and save it for multithreaded processing
        soup = BeautifulSoup(html, "lxml")

        self.q.put(self.parsePage(url_class_instance, soup))

        print(f"Done working for {url_class_instance.url}")

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


crw = Crawler(["http://evem.gov.si", "http://e-uprava.gov.si", "http://podatki.gov.si", "http://e-prostor.gov.si"], 4)
crw.setup_crawler()
crw.start_crawling()

