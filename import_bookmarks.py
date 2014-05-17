#!/usr/bin/env python

import sys
import json
import sqlite3
import argparse

import conf

parser = argparse.ArgumentParser(
    description="Import feeds from firefox json backup into sqlite database")
parser.add_argument("json_file", help="json file to import")
parser.add_argument("--import_folder", help="bookmark folder to import, e.g. /feed", default = "/")
parser.add_argument("--list-folders", help="list folders in backup and exit", action="store_true")

args = parser.parse_args()

bms = json.load(open(args.json_file))

def get_folder(bms, folder):
    if len(folder) == 0:
        return bms
    find = folder.pop()
    for child in bms['children']:
        if child['title'] == find:
            return get_folder(child, folder)
    raise RuntimError("Could not find folder {}".format(find))

def list_folders(bms, path=""):
    for child in bms['children']:
        if 'children' in child:
            cpath = path + "/" + child['title']
            print(cpath)
            list_folders(child, cpath)

if args.list_folders:
    list_folders(bms)
    sys.exit(0)

folder = get_folder(bms, [x for x in reversed(args.import_folder.split('/')) if len(x)])

def get_feeds(bms):
    feeds = []
    for child in bms['children']:
        if 'children' in child:
            feeds.extend(get_feeds(child))
        else:
            site_uri = None
            feed_uri = None
            for anno in child['annos']:
                if anno['name'] == "livemark/siteURI":
                    site_uri = anno['value']
                if anno['name'] == "livemark/feedURI":
                    feed_uri = anno['value']
            if not feed_uri:
                continue
            feeds.append((child['title'], feed_uri, site_uri))
    return feeds

feeds = get_feeds(folder)

print feeds

db = sqlite3.connect(conf.database)
c = db.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS
           feeds (id INTEGER PRIMARY KEY,
                  name TEXT NOT NULL,
                  feed_uri TEXT NOT NULL,
                  site_uri TEXT,
                  active BOOL)
          """)

c.executemany("INSERT INTO feeds VALUES (NULL,?,?,?,1)", feeds)

c.close()
db.commit()
