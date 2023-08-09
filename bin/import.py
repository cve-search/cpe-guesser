#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import os
import urllib.request
import gzip
import shutil
import xml.sax
import redis
import time
from dynaconf import Dynaconf

# Configuration
settings = Dynaconf(settings_files=['../config/settings.yaml'])
cpe_path = settings.cpe.path
cpe_source = settings.cpe.source
rdb = redis.Redis(host=settings.redis.host, port=settings.redis.port, db=8)


class CPEHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.cpe = ""
        self.title = ""
        self.title_seen = False
        self.cpe = ""
        self.record = {}
        self.refs = []
        self.itemcount = 0
        self.wordcount = 0
        self.start_time = time.time()

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
                insert(word=word, cpe=to_insert['cpeline'])
                self.wordcount += 1
            for word in canonize(to_insert['product']):
                insert(word=word, cpe=to_insert['cpeline'])
                self.wordcount += 1
            self.record = {}
            self.itemcount += 1
            if self.itemcount % 5000 == 0:
                time_elapsed = round(time.time() - self.start_time)
                print(
                    f"... {self.itemcount} items processed ({self.wordcount} words) in {time_elapsed} seconds"
                )


def CPEExtractor(cpe=None):
    if cpe is None:
        return False
    record = {}
    cpefield = cpe.split(":")
    record['vendor'] = cpefield[3]
    record['product'] = cpefield[4]
    cpeline = ""
    for cpeentry in cpefield[:5]:
        cpeline = f"{cpeline}:{cpeentry}"
    record['cpeline'] = cpeline[1:]
    return record


def canonize(value=None):
    value = value.lower()
    words = value.split('_')
    return words


def insert(word=None, cpe=None):
    if cpe is None or word is None:
        return False
    rdb.sadd(f"w:{word}", cpe)
    rdb.zadd(f"s:{word}", {cpe: 1}, incr=True)
    rdb.zadd("rank:cpe", {cpe: 1}, incr=True)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Initializes the Redis database with CPE dictionary.'
    )
    argparser.add_argument(
        '--download',
        '-d',
        action='count',
        default=0,
        help='Download the CPE dictionary even if it already exists.',
    )
    argparser.add_argument(
        '--replace',
        '-r',
        action='count',
        default=0,
        help='Flush and repopulated the CPE database.',
    )
    argparser.add_argument(
        '--update',
        '-u',
        action='store_true',
        default=False,
        help='Update the CPE database without flushing',
    )
    args = argparser.parse_args()

    if args.replace == 0 and rdb.dbsize() > 0 and not args.update:
        print(f"Warning! The Redis database already has {rdb.dbsize()} keys.")
        print("Use --replace if you want to flush the database and repopulate it.")
        sys.exit(0)

    if args.download > 0 or not os.path.isfile(cpe_path):
        print(f"Downloading CPE data from {cpe_source} ...")
        try:
            urllib.request.urlretrieve(cpe_source, f"{cpe_path}.gz")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            FileNotFoundError,
            PermissionError,
        ) as e:
            print(e)
            sys.exit(1)

        print(f"Uncompressing {cpe_path}.gz ...")
        try:
            with gzip.open(f"{cpe_path}.gz", 'rb') as cpe_gz:
                with open(cpe_path, 'wb') as cpe_xml:
                    shutil.copyfileobj(cpe_gz, cpe_xml)
            os.remove(f"{cpe_path}.gz")
        except (FileNotFoundError, PermissionError) as e:
            print(e)
            sys.exit(1)

    elif os.path.isfile(cpe_path):
        print(f"Using existing file {cpe_path} ...")

    if rdb.dbsize() > 0 and not args.update:
        print(f"Flushing {rdb.dbsize()} keys from the database...")
        rdb.flushdb()

    print("Populating the database (please be patient)...")
    parser = xml.sax.make_parser()
    Handler = CPEHandler()
    parser.setContentHandler(Handler)
    parser.parse(cpe_path)
    print(f"Done! {rdb.dbsize()} keys inserted.")
