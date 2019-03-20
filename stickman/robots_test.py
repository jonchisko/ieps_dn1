import requests

"""
For each domain respect the robots.txt file if it exists. Correctly respect the commands User-agent, Allow, Disallow, 
Crawl-delay and Sitemap. If a sitemap is defined, all the URLs that are defined within it, should be added to the frontier. 
Make sure to respect robots.txt as sites that define special crawling rules often contain spider traps.

"""

#Function parses the robots.txt file of a site and returns a list of link in the sitemap,
#list of disallowed postfixes and the crawl delay. If nothing is found then the lists are empty and the crawl delay is 4
def parse_robots(text):
    viable = text.split("User-agent:*")[1].split("User-agent:")[0]
    sitemap = []
    disallow = []
    crawl_delay = 4
    for line in viable.split("\n"):
        if "Sitemap: " in line:
            sitemap.append(line.split("Sitemap: ")[1])
        if "Disallow: " in line:
            disallow.append(line.split("Disallow: ")[1])
        if "Crawl-delay: " in line:
            crawl_delay = int(line.split("Crawl-delay: ")[1])

    return sitemap, disallow, crawl_delay


#this class is used to parse the robots.txt files for each site
class RobotsTxtHandler:

    def __init__(self, link):

        #add /robots.txt to link if needed
        self.link = link + "/robots.txt" if "robots.txt" not in link else link

        #fetch the page
        self.response = requests.get(self.link)

        #if the page exist and is accessible then parse the file and set the class attributes accordingly
        try:
            self.response.raise_for_status()
            self.sitemap, self.disallow, self.crawl_delay = parse_robots(self.response.text)

        #if raise for status triggers and exception assume that there is no robots.txt file and set attributes to default values
        except:
            self.sitemap, self.disallow, self.crawl_delay = [], [], 4



if __name__ == "__main__":
    rth = RobotsTxtHandler("https://www.thetimes.co.uk/")
