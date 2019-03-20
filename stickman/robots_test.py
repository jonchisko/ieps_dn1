import requests
import urllib.robotparser

"""
For each domain respect the robots.txt file if it exists. Correctly respect the commands User-agent, Allow, Disallow, 
Crawl-delay and Sitemap. If a sitemap is defined, all the URLs that are defined within it, should be added to the frontier. 
Make sure to respect robots.txt as sites that define special crawling rules often contain spider traps.

"""

#Function parses the robots.txt file of a site and returns a list of link in the sitemap,
#list of disallowed postfixes and the crawl delay. If nothing is found then the lists are empty and the crawl delay is 4
def parse_robots_sitemap(text):
    sitemap = []
    for line in  text.split("\n"):
        if "Sitemaps: " in line:
            sitemap.append(line.split("Sitemap: ")[1])
    return sitemap

def parse_robots_allows(url):
    allows = []
    disallows = []
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(url)
    rp.read()

    if rp.default_entry:
        for rule in rp.default_entry.rulelines:
            if rule.allowance:
                allows.append(rule.path)
            else:
                disallows.append(rule.path)
        if rp.default_entry.delay:
            crawl_delay = int(rp.default_entry.delay)
        else:
            crawl_delay = 4
    else:
        crawl_delay = 4
        allows = []
        disallows = []

    return crawl_delay, allows, disallows

#this class is used to parse the robots.txt files for each site
class RobotsTxtHandler:

    def __init__(self, link):
        #add /robots.txt to link if needed
        self.link = link + "/robots.txt" if "robots.txt" not in link else link

        #fetch the page
        self.response = requests.get(self.link)

        self.robots_exists = False


        #if the page exist and is accessible then parse the file and set the class attributes accordingly
        try:
            self.response.raise_for_status()
            self.sitemap = parse_robots_sitemap(self.response.text)
            self.robots_exists = True

        #if raise for status triggers and exception assume that there is no robots.txt file and set attributes to default values
        except Exception as e:
            #print(f"Exception was triggered while fetching: {e}")
            self.sitemap, self.allow, self.disallow, self.crawl_delay = [], [], [], 4

        #if the self.robots_exists flag has been set then the try clause didn't trigger an exception and the sitemap is set
        #we now have to get the delay and allow and disallow
        if self.robots_exists:
            self.crawl_delay, self.allow, self.disallow = parse_robots_allows(self.link)
        self.crawl_delay = int(self.crawl_delay)



if __name__ == "__main__":
    rth = RobotsTxtHandler("https://www.thetimes.co.uk/")
