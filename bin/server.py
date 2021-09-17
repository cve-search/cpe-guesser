import falcon
from wsgiref.simple_server import make_server
import requests
import redis
from datetime import datetime
import json

rdb = redis.Redis(host='127.0.0.1', port=6379, db=8, decode_responses=True)


class Search():
    def on_post(self, req, resp):
        ret = []
        data_post = req.bounded_stream.read()
        js = data_post.decode('utf-8')
        q = json.loads(js) 

        if 'query' in q:
            pass 
        else:
            resp.status = falcon.HTTP_500
            resp.media = "Missing query array or incorrect JSON format"
            return

        k=[]
        for keyword in q['query']:
            k.append('w:{}'.format(keyword.lower()))

        maxinter = len(k)
        cpes = []
        for x in reversed(range(maxinter)):
            ret = rdb.sinter(k[x])
            cpes.append(list(ret))
        result = set(cpes[0]).intersection(*cpes)

        ranked = []

        for cpe in result:
            rank = rdb.zrank('rank:cpe', cpe)
            ranked.append((rank, cpe))

        resp.media=sorted(ranked)

app = falcon.App()
app.add_route('/search', Search())

if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')
        httpd.serve_forever()

