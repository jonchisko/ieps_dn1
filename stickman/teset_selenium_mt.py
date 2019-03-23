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
from database import Database
import getFile

class Crawler:

    def __init__(self, seeds, number_of_workers):
        self.threadnum = number_of_workers
        self.seeds = seeds
        self.frontier = []
        self.q = Queue()
        self.workers = []
        self.visited = set()
        self.sites = dict()
        self.db = Database()
        self.maxPageID, self.maxSiteID = self.db.getMaxIDs()

    def check_for_existing_site(self, url):
        # urlparese(url).netloc vrne domeno
        return urlparse(url).netloc in self.sites


    #This functions has to be called before we start crawling. It takes the seed urls and parses them and inserts them into the frontier
    def setup_crawler(self):
        print("Setting up the crawler by adding seeds to the frontier.")

        self.visited = self.db.getVisited()
        db_forntier = self.db.getFrontier(self.threadnum)

        # If the database froniter is empty, add the seeds to it and the RAM froniter
        if len(db_forntier) == 0:
            for url in self.seeds:
                # Make a class instance from string url (adds domain info, such as robots.txt and sitemap)
                url_class_instance = self.domain_checking(url)
                self.frontier.append(url_class_instance)
                self.visited.add(url)

        else:
            for page in db_forntier:
                p1 = page[4].find('Disallow: ')
                p2 = page[4].find('Delay: ')

                allows = page[4][:p1]
                disallows = page[4][p1:p2]
                delay = int(page[4][p2:].replace('Delay: ', ''))

                url_class_instance = URL(page[2], allows, disallows, delay, page[1], page[0])
                site = Site(page[3], allows, disallows, page[5], delay, page[1])

                self.sites[page[3]] = site
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
            # Remove visited sites from the frontier
            for i in range(workers):
                del self.frontier[0]


            print("            Pobiram rezultat               ")
            #print out the results of crawling on lvl 1
            #the parser returns (url, set(urls), set(files), set(images))
            #now we have to empty the q, store stuff to the database in feed everything to the frontier correctly
            while not self.q.empty():
                original_url, links, files, images = self.q.get()


                self.db.updateFroniter(original_url.page_id, original_url.html, original_url.html_status_code,
                                           original_url.time)


                print(f"Adding links from {original_url.url} to frontier:")

                fromPage = []
                toPage = []
                for link in links:
                    #preverja ce smo ze obiskali tocno tak url
                    #ce se nismo ga uzamemo, instanciramo url_class_instance in ga dodamo v bazo in na frontier

                    if link not in self.visited:
                        #TODO: Content check, samo to lahko naredis sele ko ze imas content, torej v obdelavi original _urlja

                        self.visited.add(link)
                        print(f"   - added: {link}")

                        #instanciran + doda page in site v DB + doda site v RAM
                        url_class_instance = self.domain_checking(link)
                        #dodan na frontier
                        self.frontier.append(url_class_instance)

                        # Record all the links
                        fromPage.append(original_url.page_id)
                        toPage.append(url_class_instance.page_id)

                # Write links to DB
                if len(fromPage) > 0:
                    self.db.insert('link', {'from_page':fromPage, 'to_page':toPage})


                for image in images:
                    if image not in self.visited:
                        response = getFile.GetFileFromURL.get_file_from_url(image)

                        if not response:
                            continue

                        fileName, imgType, statusCode = response

                        self.visited.add(image)
                        self.addFileToDB(image, 'img', fileName, imgType, statusCode)
                        getFile.GetFileFromURL.delete_file_from_disc(fileName)
                        print(f"   - image: {fileName}")

                for file in files:
                    type = file.split('.')[-1]

                    if type not in ['pdf', 'doc', 'docx', 'ppt', 'pptx']:
                        continue

                    if file not in self.visited:
                        response = getFile.GetFileFromURL.get_file_from_url(file)

                        if not response:
                            continue

                        fileName, fileType, statusCode = response

                        self.visited.add(file)
                        self.addFileToDB(file, 'doc', fileName, fileType, statusCode)
                        getFile.GetFileFromURL.delete_file_from_disc(fileName)
                        print(f"   - file: {fileName}")







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

    def addFileToDB(self, url, type, fileName, fileType, statusCode):
        domain = urlparse(url).netloc
        self.maxPageID += 1

        if self.check_for_existing_site(url):
            siteID = self.sites[domain].site_id

        else:
            rh = RobotsTxtHandler("http://" + domain)
            allow, disallow, sitemap = rh.allow, rh.disallow, rh.sitemap
            self.maxSiteID += 1
            site = Site(url, allow, disallow, sitemap, rh.crawl_delay, self.maxSiteID)
            allows, disallows, sitemap = site.get_robots_strings()
            self.db.insert('site', {'id': [self.maxSiteID],
                                    'domain': [site.domain],
                                    'robots_content': [allows + disallows + 'Delay: ' + str(site.delay)],
                                    'sitemap_content': [sitemap]})

            self.sites[domain] = site
            siteID = site.site_id

        if type == 'img':
            self.db.insertImage(url, siteID, self.maxPageID, fileName, fileType, statusCode)
        elif type == 'doc':
            self.db.insertFile(url, siteID, self.maxPageID, fileName, fileType, statusCode)


    #Preveri ce smo domeno ze shranili
    #Ce je nismo jo shrani lokalno in v bazo doda site
    def domain_checking(self, url):

        current_domain = urlparse(url).netloc
        self.maxPageID += 1

        # ce mamo ze site za ta page ne rabimo iskat robotsov itd
        # samo nrdimo instanco page-a
        if self.check_for_existing_site(url):
            siteID = self.sites[current_domain].site_id

            url_class_instance = URL(url, self.sites[current_domain].allow, self.sites[current_domain].disallow,
                                     self.sites[current_domain].delay, siteID, self.maxPageID)

            self.db.insert('page', {'id': [self.maxPageID],
                                    'site_id': [siteID],
                                    'page_type_code': ['FRONTIER'],
                                    'url': [url]})

        else:
            # v tem primeru pa se nimamo site in je treba narest najprej treba dobit robotse za domeno strani
            rh = RobotsTxtHandler("http://" + current_domain)
            allow, disallow, sitemap = rh.allow, rh.disallow, rh.sitemap

            # instancirat domeno strani
            self.maxSiteID += 1
            site = Site(url, allow, disallow, sitemap, rh.crawl_delay, self.maxSiteID)

            allows, disallows, sitemap = site.get_robots_strings()
            self.db.insert('site', {'id': [self.maxSiteID],
                                    'domain':[site.domain],
                                    'robots_content':[allows + disallows + 'Delay: ' + str(site.delay)],
                                    'sitemap_content': [sitemap]})

            self.sites[current_domain] = site

            self.db.insert('page', {'id': [self.maxPageID],
                                    'site_id':[self.maxSiteID],
                                    'page_type_code':['FRONTIER'],
                                    'url':[url]})

            url_class_instance = URL(url, site.allow, site.disallow, site.delay, site.site_id, self.maxPageID)

        return url_class_instance

    def store_processed_to_queue(self, url_class_instance):
        # set options for headless browsing
        options = Options()
        options.headless = True

        # sleep for the crawl_delay, default 4s
        time.sleep(url_class_instance.delay)

        # set up the driver
        driver = webdriver.Chrome(options=options)

        #get the status code
        try:
            r = requests.get(url_class_instance.url)
            url_class_instance.set_html_status_code(int(r.status_code))
        except:
            url_class_instance.set_html_status_code(404)

        # fetch html
        driver.get(url_class_instance.url)
        html = driver.page_source
        url_class_instance.set_html(html)
        url_class_instance.set_time(int(time.time()))


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

