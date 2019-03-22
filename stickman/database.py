import psycopg2 as psql

# TODO: Add Locking mechanism
# TODO: Include features like UPDATE and DELETE
# TODO: figure out the exact sequence of writing to db once a page is parsed and simulate it.
class Database:

    def __init__(self):
        self.config = {'host':'165.227.156.166', 'database':'Crawler', 'user':'postgres', 'password':'IEPS!Crawler.fri'}

    def insert(self, table, data):
        #db = psql.connect(host='165.227.156.166', database='Crawler', user='postgres', password='IEPS!Crawler.fri')

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

    def getFrontier(self):
        db = psql.connect(**self.config)
        cursor = db.cursor()

        query = 'SELECT a.id, site_id, url, domain, robots_content, sitemap_content FROM crawldb.page AS a INNER JOIN crawldb.site AS b ON a.site_id = b.id WHERE page_type_code = \'FRONTIER\';'

        cursor.execute(query)

        result = []
        for row in cursor:
            result.append(row)

        cursor.close()
        db.close()

        return result

if __name__ == '__main__':
    # Init
    db = Database()
    print(len(db.getFrontier()))
    print(db.get('site', 'WHERE domain = '+ "'www.gov.si'")[0][0])
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