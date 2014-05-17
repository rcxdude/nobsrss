NoBSRSS
========

Single-user self-hosted RSS reader which is simple to set up:

```
git clone https://github.com/rcxdude/nobsrss.git
cd nobsrss
virtualenv env
source env/bin/activate
pip install -r requirements.txt
cp conf.skel.py conf.py
./set_password.py
./app.py
```
And point your browser to http://localhost:9000/rss/

No complex dependencies, no javascript, no scale, no fuss, just a list of unread feeds and links:

![screenshot](https://i.imgur.com/XNVyUDv.png)
