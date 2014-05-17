#!/usr/bin/env python

import gzip_middleware
import bottle as b
import subprocess
import threading
import functools
import setup_db
import datetime
import binascii
import sqlite3
import hashlib
import pbkdf2
import time
import os

import conf

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

class Feed:
    def __init__(self, f_id, title, feed_url, site_url, active, items, sort_index):
        self.feed_id = f_id
        self.title = title
        self.items = items
        self.sort_index = sort_index
        self.feed_url = feed_url
        self.site_url = site_url
        self.active = active

class FeedItem:
    def __init__(self, db_id, title, link, feed, item_id, date):
        self.title = title
        self.link = link
        self.feed = feed
        self.item_id = item_id
        self.date = convert_timestamp(date)
        self.db_id = db_id

valid_auth_cookies = set()

def auth_required(view):
    @functools.wraps(view)
    def auth_view(*args, **kargs):
        auth_cookie = b.request.get_cookie("auth")
        if auth_cookie in valid_auth_cookies:
            return view(*args, **kargs)
        b.redirect(conf.prefix + "/auth?goto={}".format(b.request.url.replace("rss/rss/","")), 307)
    return auth_view

def cursor():
    db = sqlite3.connect(conf.database)
    db.row_factory = sqlite3.Row
    return db.cursor()

@b.route(conf.prefix + "/auth")
@b.view("auth")
def auth():
    b.response.add_header('Set-Cookie', 'goto={}'.format(b.request.params.get('goto')))
    return {'c': conf}

@b.post(conf.prefix + "/submit_auth")
def submit_auth():
    password = b.request.forms.get('password')
    c = cursor()
    c.execute("SELECT * from passwords WHERE user = ?", ("user",))
    pw_hash = c.fetchone()['password']
    if pbkdf2.check_hash(password, pw_hash):
        auth_token = binascii.b2a_hex(os.urandom(16))
        valid_auth_cookies.add(auth_token)
        b.response.add_header('Set-Cookie', 'auth={}'.format(auth_token))
        b.redirect(b.request.get_cookie('goto'))
    else:
        b.redirect(conf.prefix + "/auth")

@b.route(conf.prefix + "/")
@b.view("index")
@auth_required
def index():
    b.redirect(conf.prefix + "/unread")
    return {}

@b.route(conf.prefix + "/new")
@b.view("new")
@auth_required
def new():
    return {'c': conf}

@b.route(conf.prefix + "/unread")
@b.view("unread")
@auth_required
def unread():
    global fetch_process
    db = sqlite3.connect(conf.database)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("""SELECT * FROM feed_items JOIN feeds ON feed_items.feed = feeds.id
                    WHERE feed_items.read = 0 ORDER BY date(feed_items.date) DESC LIMIT 100""")
    unread_feeds = {}
    for i, row in enumerate(c):
        feed = unread_feeds.get(row['feed'], Feed(row['feed'],
                                                  row['name'],
                                                  row['feed_uri'],
                                                  row['site_uri'],
                                                  row['active'],
                                                  [], i))
        feed.items.append(FeedItem(row['id'],
                                   row['title'],
                                   row['link'],
                                   row['feed'],
                                   row['item_id'],
                                   row['date']))
        unread_feeds[row['feed']] = feed
    unread_feeds = unread_feeds.values()
    unread_feeds.sort(key=lambda x: x.sort_index)
    refreshing = fetch_process is not None and fetch_process.poll() is None
    return {'c': conf, 'unread_feeds': unread_feeds, 'refreshing' : refreshing}

@b.route(conf.prefix + "/feed/<feed_id>")
@b.view("feed")
@auth_required
def feed(feed_id):
    db = sqlite3.connect(conf.database)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("""SELECT * FROM feeds WHERE ID = ?""", (feed_id,))
    row = c.fetchone()
    if not row:
        b.abort(404, "No such feed")
    feed = Feed(row['id'],
                row['name'],
                row['feed_uri'],
                row['site_uri'],
                row['active'],
                [], None)
    c.execute("""SELECT * FROM feed_items WHERE feed = ? ORDER BY date(feed_items.date) DESC LIMIT 40""", (feed_id,))
    for row in c:
        feed.items.append(FeedItem(row['id'],
                                   row['title'],
                                   row['link'],
                                   row['feed'],
                                   row['item_id'],
                                   row['date']))
    return {'c':conf, 'feed' : feed}

@b.route(conf.prefix + "/status")
@b.view("status")
@auth_required
def status():
    db = sqlite3.connect(conf.database)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("""SELECT * FROM feed_status JOIN feeds ON feed_status.feed = feeds.id ORDER BY feeds.active, feed_status.last_error DESC""")
    return {'c': conf, 'statuses': c.fetchall()}

@b.post(conf.prefix + "/mark_read")
@auth_required
def mark_read():
    db = sqlite3.connect(conf.database)
    db.row_factory = sqlite3.Row
    feed_id = b.request.forms.get("feed_id")
    c = db.cursor()
    if feed_id == 'all':
        c.execute("""UPDATE feed_items SET read = 1""")
    else:
        c.execute("""UPDATE feed_items SET read = 1 WHERE feed = ?""", (feed_id,))
    db.commit()
    b.redirect(conf.prefix + "/unread")

@b.post(conf.prefix + "/mark_active")
@auth_required
def mark_active():
    db = sqlite3.connect(conf.database)
    db.row_factory = sqlite3.Row
    feed_id = b.request.forms.get("feed_id")
    active = b.request.forms.get("active")
    c = db.cursor()
    c.execute("""UPDATE feeds SET active = ? WHERE id = ? """, 
            ({"false": 0, "true": 1}[active], feed_id))
    db.commit()
    b.redirect(conf.prefix + "/feed/{}".format(feed_id))

@b.post(conf.prefix + "/edit_feed")
@auth_required
def edit_feed():
    db = sqlite3.connect(conf.database)
    db.row_factory = sqlite3.Row
    feed_id = b.request.forms.get("feed_id")
    name = b.request.forms.get("name")
    feed_url = b.request.forms.get("feed_url")
    site_url = b.request.forms.get("site_url")
    c = db.cursor()
    c.execute("""UPDATE feeds SET name=?, feed_uri=?, site_uri=? WHERE id = ?""",
               (name, feed_url, site_url, feed_id))
    db.commit()
    b.redirect(conf.prefix + "/feed/{}".format(feed_id))

@b.post(conf.prefix + "/add_feed")
@auth_required
def add_feed():
    db = sqlite3.connect(conf.database)
    db.row_factory = sqlite3.Row
    name = b.request.forms.get("name")
    feed_url = b.request.forms.get("feed_url")
    site_url = b.request.forms.get("site_url")
    c = db.cursor()
    c.execute("""INSERT INTO feeds VALUES (NULL,?,?,?,1)""",
               (name, feed_url, site_url))
    feed_id = c.lastrowid
    db.commit()
    b.redirect(conf.prefix + "/feed/{}".format(feed_id))

def run_refresh(feed_id = None):
    global fetch_process
    if fetch_process is None or fetch_process.poll() is not None:
        cmd = ['./fetch_feeds.py']
        if feed_id is not None:
            cmd.extend(['--only-feed', feed_id, '--since', '0'])
        fetch_process = subprocess.Popen(cmd)

@b.post(conf.prefix + "/refresh")
@auth_required
def refresh():
    feed_id = b.request.forms.get("feed_id")
    if feed_id == 'all':
        feed_id = None
    run_refresh(feed_id)
    b.redirect(conf.prefix + "/unread")

def refresh_thread():
    while True:
        run_refresh()
        time.sleep(1800)

@b.route(conf.prefix + "/css/<filename:path>")
def css(filename):
    return b.static_file(filename, root="./css")

setup_db.create_tables()

fetch_process = None

if conf.auto_fetch:
    t = threading.Thread(target=refresh_thread)
    t.daemon = True
    t.start()

app = b.app()

if conf.compress:
    app = gzip_middleware.Gzipper(app)

b.debug(conf.debug)
if conf.fastcgi:
    b.run(app, host=conf.host, port=conf.port, server=b.FlupFCGIServer)
else:
    b.run(app, host=conf.host, port=conf.port)
