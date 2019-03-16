from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request
import posixpath
from urllib.parse import urlparse, urljoin, urlunparse
from selenium.webdriver.firefox.options import Options
import re

options = Options()
options.headless = True

driver = webdriver.Firefox(options=options)
#driver.get("https://www.rtvslo.si/")
driver.get("http://www.gov.si/")
#driver.get("https://www.pexels.com/search/beauty/")
html = driver.page_source
soup = BeautifulSoup(html)
for tag in soup.find_all('title'):
    print(tag.text)



# token = ".[any alfanumeric]$" at the end
# if it finds it is file, otherwise it is dir
fileEnd = re.compile("\.\w*$")
# token = index.php or index.html or index at the end
defaultFile = re.compile("index\.php|index\.html|index$")

def urlCleaner(url):
    """
    :param url: url
    :return: urlunparse, so basically url that was processed

    description:
    1. remove port number (done)**
    2. if root directory add a trailing slash (done)**
    3. if guessed directory, something/People -> add trailing slash (done)**
    4. if fragments present -> remove (done)**
    5. resolve paths sth/a/b/.././c (done)**
    6. remove default file name sth/index.html -> sth/ (done)**
                                    index.php -> so basically i guess index.* (done)**
    hard part
    7. decode needlessly encoded characters
    8. disallowed characters encoded
    9. netloc to lowercase (done)**

    ### only use http, not https (done)**
    """
    parsed = urlparse(url)
    # check if path only root, empty, et cetera
    path = posixpath.normpath(parsed.path)
    path = "/" if path == "." else path

    # try to remove if default filename
    path = re.sub(defaultFile, '', path)

    if not bool(re.search(fileEnd, path)) and not path.endswith("/"):
        path += "/"

    url = urlunparse(
        (
            parsed.scheme.replace('s', ''),
            str.lower(parsed.netloc.replace(':'+str(parsed.port), '')),
            path,
            parsed.params,
            parsed.query,
            '' # parsed.fragment
        )
    )
    return url

def possiblyExtendUrl(baseUrl, relUrl):
    # quick review
    # combine the baseUrl with relativeUrl and parse them
    #joined = urljoin(baseUrl, relUrl)
    # urlparse constructs an object:
    # ParseResult(scheme='https', netloc='rtvslo.si', path='/jon', params='', query='', fragment='')
    # url = urlparse(joined) # < not needed, since urljoin already provieds the path collapse functionality
    # urljoin already does that (so it seems)
    #path = posixpath.normpath(url[2]) # this is url.path, normpath collapses A/foo/../B to A/B
    # urlunparse makes url back from the previous ParseResult object
    #return urlunparse(joined)

    # actual code
    # check if relUrl is really relative!
    parsedR = urlparse(relUrl)
    baseUrl = urlCleaner(baseUrl)

    if parsedR.scheme == "javascript" or not relUrl:
        return baseUrl
    # if netloc is empty, then we are relative! This is netlocation, for example www.rtvslo.si, or //
    if not parsedR.netloc:
        # not of empty string is true
        # urljoin normalizes possibly not normalized relUrl
        # remove the first / for relUrl
        # it will otherwise go from root
        # if base is rtvslo.si/kultura and relis /knjige
        # without removing /, result will be rtvslo.si/knjige
        url = urljoin(baseUrl, urlCleaner(relUrl))
    else:
        # relUrl is absUrl
        # normalize possible unnormalized relUrl
        # ex: //r/lib/ok/notok/../../a -> //r/lib/a
        url = urlCleaner(relUrl)
    print(url)
    return url

# some tests
print(possiblyExtendUrl('http://www.test.com/', './../me'))
print(possiblyExtendUrl('http://www.test.com/abc', './../../test'))
print(possiblyExtendUrl('http://www.test.com/abc', '././test'))
print(possiblyExtendUrl('http://www.test.com/abc', './miska/test'))
print(possiblyExtendUrl('http://www.test.com/abc', '//a/b/./../../test'))
print(possiblyExtendUrl('http://www.test.com:8080/abc', '/../test'))
# tests end


def getUrls(page):
    pass

def getImages(page):
    pass

def getFiles(page):
    pass

# 1 find images, URLs
## (e.g. location.href or document.location)
## correctly extend relative URLs
## Detect images on a web page only based on img tag, where the src attribute points to an image URL
## download: .pdf, .doc, .docx, .ppt and .pptx.

# current url of location
curr_url = driver.current_url
# go through all elements in soup with "a" tag and get the "href"
urls = set(possiblyExtendUrl(curr_url, link.get("href")) for link in soup.find_all("a"))


images = soup.find_all("img")
imageUrls = set()
for img in images:
    imgUrl1, imgUrl2 = img.get("data-src"), img.get("src")
    if imgUrl1:
        imageUrls.add(imgUrl1)
        continue
    if imgUrl2:
        imageUrls.add(imgUrl2)


driver.close()