#!/usr/bin/env python

import pbkdf2
import getpass

import conf
import sqlite3
import setup_db

setup_db.create_tables()

db = sqlite3.connect(conf.database)
c = db.cursor()

password = getpass.getpass("Input password:")
pw_hash = pbkdf2.make_hash(password)

c.execute("INSERT INTO passwords VALUES (?, ?)",
            ("user", pw_hash))
db.commit()

