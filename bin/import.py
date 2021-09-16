
import xml.sax
import redis
rdb = redis.Redis(host='127.0.0.1', port=6379, db=8)

class CPEHandler( xml.sax.ContentHandler ):
    def __init__(self):
        self.cpe = ""
        self.title = ""
        self.title_seen = False
        self.cpe = ""
        self.record  = {}
        self.refs = []

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == 'cpe-23:cpe23-item':
            self.record['cpe-23'] = attributes['name']
        if tag == 'title':
            self.title_seen = True
        if tag == 'reference':
            self.refs.append(attributes['href'])

    def characters(self, data):
        if self.title_seen:
            self.title = self.title + data
      
    def endElement(self, tag):
        if tag == 'title':
            self.record['title'] = self.title
            self.title = ""
            self.title_seen = False
        if tag == 'references':
            self.record['refs'] = self.refs
            self.refs = []
        if tag == 'cpe-item':
            to_insert = CPEExtractor(cpe=self.record['cpe-23'])
            for word in canonize(to_insert['vendor']):
                insert( word=word, cpe=to_insert['cpeline'] )
            for word in canonize(to_insert['product']):
                insert( word=word, cpe=to_insert['cpeline'] )
            self.record = {}


def CPEExtractor( cpe=None ):
    if cpe is None:
        return False
    record = {}
    cpefield = cpe.split(":")
    record['vendor'] = cpefield[3]
    record['product'] = cpefield[4]
    cpeline = ""
    for cpeentry in cpefield[:5]:
        cpeline = "{}:{}".format(cpeline, cpeentry)
    record['cpeline'] = cpeline[1:] 
    return record 

def canonize( value=None ):
    value = value.lower()
    words = value.split('_')
    return words

def insert( word=None, cpe=None):
    if cpe is None or word is None:
        return False
    rdb.sadd('w:{}'.format(word), cpe)
    rdb.zadd('s:{}'.format(word), {cpe: 1}, incr=True)
    rdb.zadd('rank:cpe', {cpe: 1}, incr=True)

cpe_path = '../data/official-cpe-dictionary_v2.3.xml'

parser = xml.sax.make_parser()

Handler = CPEHandler()
parser.setContentHandler( Handler )
parser.parse(cpe_path)
