from urllib.parse import urlparse
from robots_test import *
import time


#okej, tko sm si zamislu
#url class bo za storanje url-ja ampak bo tud mel robotse tko da pomoje je treba narest check ce ze smo kdaj bli na tem domainu
#torej slovar bo en atribut razreda crawler, k bo torej slovar k bo mel za kljuc domain name in za value nek class site


#ko bos dajal v bazo klices to string da bos dal kot 1 string vse skupi
class Site:

    def __init__(self, url, allow, disallow, sitemap, delay):
        self.url = url
        self.domain = urlparse(url).netloc
        self.allow = allow
        self.disallow = disallow
        self.sitemap = sitemap
        self.delay = delay
        self.site_id = None

    def set_site_id(self, site_id):
        self.site_id = site_id

    def get_robots_strings(self):
        robots_allow = ""
        for allow in self.allow:
            robots_allow += "Allow: " + str(allow) + "\n"

        robots_disallow = ""
        for disallow in self.disallow:
            robots_disallow += "Disallow: " + str(disallow) + "\n"

        robots_sitemap = ""
        for sitemap in self.sitemap:
            robots_sitemap += "Sitemap: " + str(sitemap) + "\n"


        return robots_allow, robots_disallow, robots_sitemap

class URL:

    def __init__(self, url, allow, disallow, delay, site_id):#, page_id, html):
        self.url = url
        self.domain = urlparse(url).netloc
        self.time = None
        self.allow = allow
        self.disallow = disallow
        self.delay = delay
        self.site_id = site_id
        self.page_id = None
        self.html_status_code = None
        self.html = None


    def set_html(self, html):
        self.html = html

    def set_html_status_code(self, code):
        self.html_status_code = code

    def set_page_id(self, page_id):
        self.page_id = page_id

    def set_time(self, time):
        self.time = time
if __name__ == "__main__":
    url = URL("http://www.e-prostor.gov.si/dostop-do-podatkov/dostop-do-podatkov/")
