#!/usr/bin/env python
import sqlite3

import conf

def create_tables():
    db = sqlite3.connect(conf.database)
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS
               feeds (id INTEGER PRIMARY KEY,
                      name TEXT NOT NULL,
                      feed_uri TEXT NOT NULL,
                      site_uri TEXT,
                      active BOOL)
              """)
    c.execute("""CREATE TABLE IF NOT EXISTS
                 passwords (user TEXT NOT NULL,
                            password TEXT NOT NULL,
                            UNIQUE(user, password) ON CONFLICT REPLACE
                            )""")
    c.execute("""CREATE TABLE IF NOT EXISTS
                feed_items ( id INTEGER PRIMARY KEY,
                             feed INTEGER NOT NULL,
                             title TEXT,
                             link TEXT,
                             item_id TEXT,
                             date DATETIME,
                             read BOOL,
                             UNIQUE (feed, item_id) ON CONFLICT IGNORE,
                             FOREIGN KEY(feed) REFERENCES feeds(id) )""")
    c.execute("""CREATE INDEX IF NOT EXISTS idx_item_id ON feed_items(feed, item_id)""")
    c.execute("""CREATE INDEX IF NOT EXISTS idx_unread ON feed_items(read)""")
    c.execute("""CREATE TABLE IF NOT EXISTS
                feed_status ( id INTEGER PRIMARY KEY,
                              feed INTEGER UNIQUE NOT NULL,
                              last_fetch DATETIME,
                              bozo BOOL,
                              last_error TEXT,
                              FOREIGN KEY(feed) REFERENCES feeds(id) )""")
    c.close()
    db.commit()

if __name__ == "__main__":
    print("Creating database tables")
    create_tables()
    print("Done")
