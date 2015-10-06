#!/usr/bin/env python

import copy, os, re, sqlite3, string, urllib
from bs4 import BeautifulSoup, NavigableString, Tag

DOCUMENTS_DIR = os.path.join('apiDoc.docset', 'Contents', 'Resources', 'Documents')
HTML_DIR = os.path.join('apidocjs.com')

db = sqlite3.connect('apiDoc.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

page = open(os.path.join(DOCUMENTS_DIR, HTML_DIR, "index.html")).read()
soup = BeautifulSoup(page, 'html5lib')
nav = soup.find('nav', class_='nav-main')

type = "Sample"

for item in nav.find_all("li"):
    link = item.find("a")

    name = link.text.strip()
    path = os.path.join(HTML_DIR, "index.html") + link.attrs["href"]

    if "class" in item.attrs and "nav-header" in item.attrs["class"]:
        if name == "Demo" or name == "Examples":
            type = "Sample"
        if name == "Getting started":
            type = "Guide"
        if name == "apiDoc-Params":
            type = "Parameter"

    if "class" in item.attrs and "deprecated" in item.attrs["class"]:
        type = "Guide"
        path = os.path.join(HTML_DIR, link.attrs["href"])

    cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)", (name, type, path))

    print "name: %s, type: %s, path: %s" % (name, type, path)

    article = soup.find(id=link.attrs["href"].lstrip("#"))

    if not article:
        continue

    headline = article.find("h1") or article.find("h2")

    if not headline:
        continue

    dashAnchor = headline.find("a", class_="dashAnchor")

    if dashAnchor:
        continue

    print "adding toc tag for section: %s" % name
    name = "//apple_ref/cpp/" + type + "/" + urllib.quote(name, "")
    dashAnchor = BeautifulSoup('<a name="%s" class="dashAnchor"></a>' % name).a
    headline.insert(0, dashAnchor)

 # strip unecessary tags
[t.extract() for t in soup("script")]
[t.extract() for t in soup.find("header").find_all("div")]
[t.extract() for t in soup.find(id="forkme")]

# strip Google-Fonts
for link in soup.find_all("link", { "rel" : "stylesheet" }):
    test = re.compile("^https?.*googleapis.*", re.IGNORECASE)

    if "href" in link.attrs and test.match(link["href"].strip()):
        link.extract()

fp = open(os.path.join(DOCUMENTS_DIR, HTML_DIR, "index.html"), "w")
fp.write(str(soup))
fp.close()

# cleanup deprecated.html
page = open(os.path.join(DOCUMENTS_DIR, HTML_DIR, "deprecated.html")).read()
soup = BeautifulSoup(page, 'html5lib')

[t.extract() for t in soup("script")]

fp = open(os.path.join(DOCUMENTS_DIR, HTML_DIR, "deprecated.html"), "w")
fp.write(str(soup))
fp.close()

db.commit()
db.close()
