import psycopg2 as psql
from datetime import datetime
import time

# TODO: Add Locking mechanism
# TODO: Include features like UPDATE and DELETE
# TODO: figure out the exact sequence of writing to db once a page is parsed and simulate it.
class Database:

    def __init__(self):
        self.config = {'host':'165.227.156.166', 'database':'Crawler', 'user':'postgres', 'password':'IEPS!Crawler.fri'}

    def insert(self, table, data):
        keys = list(data.keys())
        intro = 'INSERT INTO crawldb.' + table
        columns = ' (' + ','.join(keys) + ') VALUES '
        dataString = ''

        template = '(' + ','.join(len(keys) * ['%s']) + ')'
        values = []

        for i in range(len(data[keys[0]])):
            dataString += template + ', '
            for key in keys:
                values.append(data[key][i])

        dataString = dataString[:-2]

        query = intro + columns + dataString + ';'

        db = psql.connect(**self.config)
        cursor = db.cursor()

        try:
            cursor.execute(query, values)
            db.commit()
        except psql.DataError as err:
            print(err.pgerror)
        except psql.IntegrityError as err:
            print(err.pgerror)

        cursor.close()
        db.close()

    def get(self, table, conditions = '', n = None):
        db = psql.connect(**self.config)
        cursor = db.cursor()

        limit = ';'
        if n:
            limit = ' LIMIT ' + str(n) + ';'

        query = 'SELECT * FROM crawldb.' + table + ' ' + conditions + limit

        cursor.execute(query)

        result = []
        for row in cursor:
            result.append(row)

        cursor.close()
        db.close()

        return result

    def getFrontier(self, N):
        db = psql.connect(**self.config)
        cursor = db.cursor()

        query = 'SELECT a.id, site_id, url, domain, robots_content, sitemap_content ' \
                'FROM crawldb.page AS a INNER JOIN crawldb.site AS b ON a.site_id = b.id ' \
                'WHERE page_type_code = \'FRONTIER\' ' \
                'LIMIT ' + str(N) + ';'

        cursor.execute(query)

        result = []
        for row in cursor:
            result.append(row)

        cursor.close()
        db.close()

        return result

    def updateFroniter(self, pageID, html, statusCode, time):
        db = psql.connect(**self.config)
        cursor = db.cursor()

        query = 'UPDATE crawldb.page ' \
                'SET page_type_code = \'HTML\', ' \
                '   html_content = %s, ' \
                '   http_status_code = ' + str(statusCode) + ', ' \
                '   accessed_time = \'' + datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S') + '\' ' \
                'WHERE id = ' + str(pageID) + ';'

        cursor.execute(query, [html])
        db.commit()

        cursor.close()
        db.close()

    def getVisited(self):
        db = psql.connect(**self.config)
        cursor = db.cursor()

        seen = []

        query = 'SELECT DISTINCT url FROM crawldb.page;'
        cursor.execute(query)

        for url in cursor:
            seen.append(url[0])

        cursor.close()
        db.close()

        return set(seen)

    def getMaxIDs(self):
        db = psql.connect(**self.config)
        cursor = db.cursor()

        query1 = 'SELECT MAX(id) FROM crawldb.page;'
        query2 = 'SELECT MAX(id) FROM crawldb.site;'

        cursor.execute(query1)
        for line in cursor:
            maxPageID = line[0]
            break

        if maxPageID is None:
            maxPageID = 0

        maxSiteID = 0
        cursor.execute(query2)
        for line in cursor:
            maxSiteID = line[0]
            break

        if maxSiteID is None:
            maxSiteID = 0

        cursor.close()
        db.close()

        return maxPageID, maxSiteID

    def insertImage(self, url, siteID, pageID, fileName, imgType, statusCode):
        accessTime = int(time.time())

        db = psql.connect(**self.config)
        cursor = db.cursor()

        keys = ['url', 'site_id', 'id', 'page_type_code', 'http_status_code', 'accessed_time']
        intro = 'INSERT INTO crawldb.page'
        columns = ' (' + ','.join(keys) + ') VALUES '
        dataString = '(' + ','.join(len(keys) * ['%s']) + ')'
        values = [url, siteID, pageID, 'BINARY', statusCode, datetime.utcfromtimestamp(accessTime).strftime('%Y-%m-%d %H:%M:%S')]

        query = intro + columns + dataString + ';'

        db = psql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(query, values)

        file = open(fileName, 'rb')
        data = file.read()

        keys = ['page_id', 'filename', 'content_type', 'data', 'accessed_time']
        intro = 'INSERT INTO crawldb.image'
        columns = ' (' + ','.join(keys) + ') VALUES '
        dataString = '(%s, %s, %s, %s, %s)'
        values = [pageID, fileName, imgType, data, datetime.utcfromtimestamp(accessTime).strftime('%Y-%m-%d %H:%M:%S')]

        query = intro + columns + dataString + ';'
        cursor.execute(query, values)

        db.commit()

        cursor.close()
        db.close()

    def insertFile(self, url, siteID, pageID, fileName, fileType, statusCode):
        fileType = fileType.upper()
        accessTime = int(time.time())

        db = psql.connect(**self.config)
        cursor = db.cursor()

        keys = ['url', 'site_id', 'id', 'page_type_code', 'http_status_code', 'accessed_time']
        intro = 'INSERT INTO crawldb.page'
        columns = ' (' + ','.join(keys) + ') VALUES '
        dataString = '(' + ','.join(len(keys) * ['%s']) + ')'
        values = [url, siteID, pageID, 'BINARY', statusCode, datetime.utcfromtimestamp(accessTime).strftime('%Y-%m-%d %H:%M:%S')]

        query = intro + columns + dataString + ';'

        db = psql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(query, values)

        file = open(fileName, 'rb')
        data = file.read()

        keys = ['page_id', 'data_type_code', 'data']
        intro = 'INSERT INTO crawldb.page_data'
        columns = ' (' + ','.join(keys) + ') VALUES '
        dataString = '(%s, %s, %s)'
        values = [pageID, fileType, data]

        query = intro + columns + dataString + ';'
        cursor.execute(query, values)

        db.commit()

        cursor.close()
        db.close()


if __name__ == '__main__':
    # Init
    db = Database()


    '''
    # Prepare and insert data
    data = {'id': [1, 2, 3],
            'domain': ['www.gov.si', 'www.najdi.si', 'www.chupacabra.it'],
            'robots_content': [None, 'You may do everything', None],
            'sitemap_content': [None, 'SiteMap!', 'Neverland']}

    db.insert('site', data)

    # Retrieve filtered data and print results
    results = db.get('site', conditions='WHERE id > 1')

    for row in results:
        print(row)
    
    '''