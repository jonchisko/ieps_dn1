from bs4 import BeautifulSoup
from selenium import webdriver
import posixpath
from urllib.parse import urlparse, urljoin, urlunparse, quote, unquote
from selenium.webdriver.firefox.options import Options
import re




class htmlGetAll:

    # important tokenz

    # token = ".[any alfanumeric]$" at the end
    # if it finds it is file, otherwise it is dir
    fileEnd = re.compile("\.\w*$")
    # token = index.php or index.html or index at the end
    defaultFile = re.compile("index\.php|index\.html|index$")
    # find href in javascript
    # match: "document.location.href =  "http://www.google.com" "
    # or "document.location.href =  "http://www.google.com" "
    jsHref = "document.location.href *= *['\"].*['\"]"

    @staticmethod
    def urlCleaner(url):
        """
        :param url: url
        :return: urlunparse, so basically url that was processed
        url1 = "https://cs.indiana.edu/%7Efil/"
        url2 = "https://cs.indiana.edu/My File.html"
        url3 = "https://cs.indiana.edu/%7Efil/My File.html"


        description:
        1. remove port number (done)**
        2. if root directory add a trailing slash (done)**
        3. if guessed directory, something/People -> add trailing slash (done)**
        4. if fragments present -> remove (done)**
        5. resolve paths sth/a/b/.././c (done)**
        6. remove default file name sth/index.html -> sth/ (done)**
                                        index.php -> so basically i guess index.* (done)**
        hard part
        7. decode needlessly encoded characters (done)**
        8. disallowed characters encoded  (done)**
        9. netloc to lowercase (done)**

        ### only use http, not https (done)**
        """
        parsed = urlparse(url)
        path = posixpath.normpath(parsed.path)
        #if path only root (current pos), normalize returns ., change it to "/"
        path = "/" if path == "." else path
        # try to remove if default filename
        path = re.sub(htmlGetAll.defaultFile, '', path)

        if not bool(re.search(htmlGetAll.fileEnd, path)) and not path.endswith("/"):
            path += "/"
        # decode path to fullblown unicode
        path = unquote(path)
        # encode, but only those outside ascii and unsafe
        path = quote(path, safe=":_.-/~")
        # do the same for query ...
        query = quote(unquote(parsed.query), safe=":_.-/~")

        # if not empty, it is an url with netloc and not just some relative path
        netloc = ''
        if parsed.netloc:
            netloc = str.lower(parsed.netloc.replace(':'+str(parsed.port), ''))
            # not all urls work with www. e-uprava for instance
            # netloc = tmp if tmp.startswith("www") else "www."+tmp

        url = urlunparse(
            (
                parsed.scheme.replace('s', ''),
                netloc,
                path,
                parsed.params,
                query,
                '' # parsed.fragment, remove fragments
            )
        )
        return url

    @staticmethod
    def possiblyExtendUrl(baseUrl, relUrl, robots):
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

        if parsedR.scheme == "javascript" or not relUrl or relUrl in robots:
            return baseUrl
        # if netloc is empty, then we are relative! This is netlocation, for example www.rtvslo.si, or //
        if not parsedR.netloc:
            # not of empty string is true
            # urljoin normalizes possibly not normalized relUrl
            # remove the first / for relUrl
            # it will otherwise go from root
            # if base is rtvslo.si/kultura and relis /knjige
            # without removing /, result will be rtvslo.si/knjige
            url = urljoin(baseUrl, htmlGetAll.urlCleaner(relUrl))
        else:
            # relUrl is absUrl
            # normalize possible unnormalized relUrl
            # ex: //r/lib/ok/notok/../../a -> //r/lib/a
            url = htmlGetAll.urlCleaner(relUrl)
        return url

    @staticmethod
    def isFile(url):
        return (url.endswith(".pdf") or url.endswith(".doc") or url.endswith(".doc")
                or url.endswith(".docx") or url.endswith(".ppt") or url.endswith(".pptx"))

    @staticmethod
    def doPage(base_url, htmlSoup, robots):
        urls = set()
        files = set()
        imgs = set()
        robots = set(robots)
        base_url = htmlGetAll.urlCleaner(base_url)
        for link in htmlSoup.find_all("a"):
            url = htmlGetAll.possiblyExtendUrl(base_url, link.get("href"), robots)
            # file or url
            if htmlGetAll.isFile(url):
                files.add(url)
            else:
                if "gov.si" in url:
                    urls.add(url)
        # get javascript urls ??
        for locations in re.findall(htmlGetAll.jsHref, str(htmlSoup), re.MULTILINE):
            url = htmlGetAll.possiblyExtendUrl(base_url, locations.split("=")[-1].strip(" \"'"), robots)
            if htmlGetAll.isFile(url):
                files.add(url)
            else:
                if "gov.si" in url:
                    urls.add(url)
        # remove base_url from urls set
        if base_url in urls:
            urls.remove(base_url)

        for img in htmlSoup.find_all("img"):
            imgUrl1, imgUrl2 = img.get("data-src"), img.get("src")
            if imgUrl1:
                imgs.add(imgUrl1)
                continue
            if imgUrl2:
                imgs.add(imgUrl2)
        return urls, files, imgs


if __name__ == '__main__':

    options = Options()
    options.headless = True

    driver = webdriver.Firefox(options=options)
    # driver.get("https://www.rtvslo.si/")
    driver.get("http://www.vlada.si/teme_in_projekti/strategija_razvoja_slovenije_2030/")#"http://www.gov.si/")
    # driver.get("https://www.pexels.com/search/beauty/")
    html = driver.page_source
    soup = BeautifulSoup(html)
    for tag in soup.find_all('title'):
        print(tag.text)

    # some tests
    print(htmlGetAll.possiblyExtendUrl('http://www.test.com/', './../me'))
    print(htmlGetAll.possiblyExtendUrl('http://www.test.com/abc', './../../test'))
    print(htmlGetAll.possiblyExtendUrl('http://www.test.com/abc', '././test'))
    print(htmlGetAll.possiblyExtendUrl('http://www.test.com/abc', './miska/test'))
    print(htmlGetAll.possiblyExtendUrl('http://www.test.com/abc', '//a/b/./../../test'))
    print(htmlGetAll.possiblyExtendUrl('http://www.test.com/abc', '/../test'))

    # tests on canonization ... first slides 16th page
    print(htmlGetAll.urlCleaner("http://cs.indiana.edu:80/"))
    print(htmlGetAll.urlCleaner("http://cs.indiana.edu"))
    print(htmlGetAll.urlCleaner("http://cs.indiana.edu/People"))
    print(htmlGetAll.urlCleaner("http://cs.indiana.edu/faq.html#3"))
    print(htmlGetAll.urlCleaner("http://cs.indiana.edu/a/./../b"))
    print(htmlGetAll.urlCleaner("http://cs.indiana.edu/a/./../b/"))
    print(htmlGetAll.urlCleaner("http://cs.indiana.edu/a/./index.php"))
    print(htmlGetAll.urlCleaner("http://cs.indiana.edu/a/./index.html"))
    print(htmlGetAll.urlCleaner("http://cs.indiana.edu/index"))
    print(htmlGetAll.urlCleaner("http://cs.InDiana.edu/a/"))
    print(htmlGetAll.urlCleaner("https://cs.indiana.edu/%7Efil/"))
    print(htmlGetAll.urlCleaner("https://cs.indiana.edu/My File.html"))
    print(htmlGetAll.urlCleaner("https://cs.indiana.edu/%7Efil/My File.html"))
    print(htmlGetAll.urlCleaner("https://cs.indiana.edu/%7Efil/My FileŽ.html"))
    # Copatek shared some url tests
    print(htmlGetAll.urlCleaner("http://www.google.com/#test")) # - da vrže preč #test
    print(htmlGetAll.urlCleaner("http://delo.si/")) # - da doda www.
    print(htmlGetAll.urlCleaner("https://www.google.com:443/test")) # -  vrže vn port number



    multi = """
        asdsdfasdf
        df
        asdg
        dfgsdf
        document.location.href   = "www.rtvslo.si"
        asdasdads
        document.location.href="www.rtvslo.si"
        asdasdafa
        document.location.hrefasd
        document.location.href = 'www.rtvslo.si'
        asd
    """

    a = re.findall("document.location.href *= *['\"].*['\"]", multi, re.MULTILINE)
    for found in a:
        print(found.split("=")[-1].strip(" \"'"))


    # test gov

    results = htmlGetAll.doPage(driver.current_url, soup)
    for e in results:
        print(e)

    # close webpage
    driver.close()
    # tests end
