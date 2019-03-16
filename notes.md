# Description of the seminar

#### This is basically a short guideline - [source](http://zitnik.si/teaching/wier/PA1.html)

We have to fulfill the following goals:
1. HTTP downloader and renderer: To retrieve and render a web page.
2. Data extractor: Minimal functionalities to extract images and hyperlinks.
3. Duplicate detector: To detect already parsed pages.
4. URL frontier: A list of URLs waiting to be parsed.
5. Datastore: To store the data and additional metadata used by the crawler.


We have to implement a webcrawler that will traverse
the following webpages (source URLs):
* evem.gov.si
* e-uprava.gov.si
* podatki.gov.si
* e-prostor.gov.si

Five additional ".gov.si" URLs:

* dv.gov.si
* mo.gov.si
* arso.gov.si
* mk.gov.si
* mzi.gov.si

The crawler will be implemented with <b>multiple threads</b> that will
run and retrieve web pages in parallel. Number of threads is a 
parameter that is given when starting the crawler. 

The <b>frontier</b> should follow BFS strategy (describe the implementation
in the final report)

#### "robots.txt"
If robots.txt file exist, you should respect it - [click](https://en.wikipedia.org/wiki/Robots_exclusion_standard).
Correctly respect the following commands as well: User-agent, Allow, Disallow, Crawl-delay and Sitemap. If a Sitemap
is defined, all the URLs that are defined within it, should be added to the frontier. Be careful of spider traps - 
[click](https://en.wikipedia.org/wiki/Spider_trap).

#### Duplicate web page detection
Three important things:
1. Check if URL was already parsed,
2. Check if URL is in frontier,
3. if you do not find URL in the above, try to check if perhaps
URL content was already parsed (checkin the html code - "extend the database with a hash or compare exact HTML code").


#### Bonus (extra 10 points)

Detecting a duplicate with direct content match is not that efficient, because 
there can be a small difference in the html documents, despite the web pages being the
same. Implement the Locality-Sensitive hashing method and apply Jaccard distance (with unigrams). Select
parameters for the method and show an example of a possible duplicate (in the report).

#### Links, images and other stuff

Copy paste from the source file:

    "When parsing links, include links from href attributes 
    and onclick Javascript events (e.g. location.href or 
    document.location). Be careful to correctly extend the 
    relative URLs before adding them to the frontier.
    Detect images on a web page only based on img tag, 
    where the src attribute points to an image URL.
    
    ... download also other files that web pages point to 
    (there is no need to parse them). File formats that 
    you should take into account are 
    .pdf, .doc, .docx, .ppt and .pptx."



#### Headless browser

Some useful libraries are:

    HTML Cleaner
    HTML Parser
    JSoup
    Jaunt API


## DataBase
TODO