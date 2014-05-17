#!/usr/bin/env python

import sqlite3
import datetime
import argparse
import traceback
import feedparser

import setup_db

def convert_timestamp(val):
    datepart, timepart = val.split(" ")
    year, month, day = map(int, datepart.split("-"))
    timepart_full = timepart.split(".")
    hours, minutes, seconds = map(int, timepart_full[0].split(":"))
    if len(timepart_full) == 2:
        microseconds = int('{:0<6.6}'.format(timepart_full[1].decode()))
    else:
        microseconds = 0

    val = datetime.datetime(year, month, day, hours, minutes, seconds, microseconds)
    return val

def sanity_feed_item(feed_id, feed_item):
    link = feed_item.link
    if 'title' in feed_item:
        title = feed_item.title
    else:
        title = feed_item.link
    if 'id' in feed_item:
        id = feed_item.id
    else:
        id = feed_item.link
    if 'updated_parsed' in feed_item:
        updated = datetime.datetime(*feed_item.updated_parsed[:6])
    elif 'created_parsed' in feed_item:
        updated = datetime.datetime(*feed_item.created_parsed[:6])
    elif 'published_parsed' in feed_item and feed_item.published_parsed is not None:
        updated = datetime.datetime(*feed_item.published_parsed[:6])
    else:
        updated = datetime.datetime.now()
    return (feed_id, title, link, id, updated, False)


def update_feed(c, feed_id, name, feed_uri):
    print(u"updating {} ({})".format(name, feed_id))
    feed = feedparser.parse(feed_uri)
    if len(feed.entries) == 0:
        raise RuntimeError(u"No Entries for feed {}".format(name))
    c.executemany("INSERT INTO feed_items VALUES(NULL,?,?,?,?,?,?)",
            [sanity_feed_item(feed_id, e) for e in feed.entries])
    print(u"done updating")
    return feed

def update_all(args):
    db = sqlite3.connect("feeds.db")
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("PRAGMA foreign_keys = ON")
    if args.only_feed:
        c.execute("SELECT * FROM feeds WHERE id = ?", (args.only_feed,))
    else:
        c.execute("SELECT * FROM feeds")
    for row in c.fetchall():
        if row['active'] == 0:
            continue
        c.execute("SELECT * FROM feed_status WHERE feed = ?", (row['id'],))
        r = c.fetchone()
        if r and r['last_fetch'] is not None:
            date = convert_timestamp(r['last_fetch'])
            if datetime.datetime.now() - date < datetime.timedelta(minutes=args.since):
                continue
            print(date, type(date))
        try:
            f = update_feed(c, row['id'], row['name'], row['feed_uri'])
            c.execute("INSERT OR REPLACE INTO feed_status VALUES(NULL, ?, ?, ?, NULL)",
                        (row['id'], datetime.datetime.now(), f.bozo) )
        except:
            error_string = traceback.format_exc()
            print(error_string)
            c.execute("INSERT OR REPLACE INTO feed_status VALUES(NULL, ?, NULL, NULL, ?)",
                        (row['id'], error_string))
        db.commit()
    c.close()

parser = argparse.ArgumentParser(description="fetch feeds into database")
parser.add_argument("--since", default=30, type=int, 
    help="how out of date fetched feeds need to be before they are fetched")
parser.add_argument("--only-feed", help="fetch this feed only")
parser.add_argument("--no-create", help="Don't create any tables", action="store_true")

args = parser.parse_args()

if not args.no_create:
    setup_db.create_tables()
update_all(args)
