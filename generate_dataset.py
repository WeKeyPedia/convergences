# -*- coding: utf-8 -*-

from __future__ import division

import os
import sys

from math import ceil

from collections import defaultdict

import codecs
import json

from multiprocessing import Pool as ThreadPool

import wekeypedia
from wekeypedia.wikipedia.api import api as api


def api_bunch(page_titles, lang, req):
  results = defaultdict(list)
  param  = req

  w = api(lang)

  for i in range(0,int(ceil(len(page_titles)/50))):
    param["titles"] = "|".join(page_titles[i*50:i*50+50-1])

    while True:
      r = w.get(param, method="post")
      results.update({ p["title"]: p['langlinks'] for pageid, p in r["query"]["pages"].items() if 'langlinks' in p })

      if "continue" in r:
        param.update(r["continue"])
      else:
        break

  return results

def get_lang_projection(pages, source, target):
  params = {
    "redirects": "",
    "format": "json",
    "action": "query",
    "prop": "info|langlinks",
    "lllimit": 500,
    "lllang": target,
    "continue":""
  }

  r = api_bunch(pages, source, params)

  convergence = [ (page, t["*"]) for page,tt in r.items() for t in tt if t["lang"] == target ]

  return convergence

def replace_redirects(pages, lang, flat=True):
  results = set(pages)

  results_dict = {}

  params = {
    "redirects": "",
    "format": "json",
    "action": "query"
  }

  w = api(lang)

  for i in range(0,int(ceil(len(pages)/50))):
    # print i*50,i*50+50-1
    params["titles"] = "|".join(pages[i*50:i*50+50-1])
    resp = w.post(params)

    if "redirects" in resp["query"]:
      results = results - set([ r["from"] for r in resp["query"]["redirects"]])
      results = results | set([ r["to"] for r in resp["query"]["redirects"]])

      results_dict[r["from"]] = r["to"]

  if flat:
    return list(results)
  else:
    return results_dict

def from_to(page, source, target, dataset_name, skip=False):
  p = wekeypedia.WikipediaPage(page, source)
  links = replace_redirects(list({ x["title"] for x in p.get_links() }), p.lang)

  print( u"[{0}][{3}] {1} ---> {2} links".format(source, p.title, len(links), target) )

  if not skip:
    write(u"data/{0}/{1}.json".format(dataset_name, source), links)

  links_translated = get_lang_projection(links, source, target)

  links_translated_redirects = replace_redirects(list({ x[1] for x in links_translated }), target, False)

  links_translated = { x[0]: links_translated_redirects.setdefault(x[1], x[1])  for x in links_translated }

  write(u"data/{0}/{1}.{2}.json".format(dataset_name, source, target), links_translated)

def write(filename, data):
  with codecs.open(filename, "w", "utf-8-sig") as f:
    json.dump(data, f, ensure_ascii=False, indent=2, separators=(',', ': '))

def m(args):
  lang = args[0]
  page = args[1]
  p_lang = args[2]
  p_title = args[3]

  if lang in ignore_langs:
    return

  if not os.path.isfile(u"data/{1}.{0}/{3}.{1}.json".format(p_title, p_lang, page, lang)):
    from_to(page, lang, p_lang, u"{1}.{0}".format(p_title, p_lang))

  if not os.path.isfile(u"data/{1}.{0}/{1}.{3}.json".format(p_title, p_lang, page, lang)):
    from_to(p_title, p_lang, lang, u"{1}.{0}".format(p_title, p_lang), skip=True)

def compute_source(source):
  # source = "Love" # "Love"

  lang = "en"

  if "#" in source:
    lang = source.split("#")[1]
    source = source.split("#")[0]

  p = wekeypedia.WikipediaPage(source, lang)

  links = replace_redirects(list({ x["title"] for x in p.get_links() }), p.lang)

  print("links: {0}".format(len(links)))

  if not os.path.exists(u"data/{1}.{0}".format(source, p.lang)):
      os.makedirs(u"data/{1}.{0}".format(source, p.lang))

  write(u"data/{1}.{0}/{1}.json".format(source, p.lang), links)

  available_langs = { x["lang"]: x["*"] for x in p.get_langlinks() }

  write(u"data/{1}.{0}.json".format(source, p.lang), available_langs)

  # map(m, [ (x[0], x[1], p.lang, p.title) for x in available_langs.items() ] )

  pool = ThreadPool(4)

  pool.map(m, [ (x[0], x[1], p.lang, p.title) for x in available_langs.items() ] )

  pool.close()
  pool.join()

ignore_langs = []

if __name__ == "__main__":


  if len(sys.argv) < 2:
    sources = ["Love", "Revolution", "Wisdom", "Ethics", "Morality", "Surveillance"]
    sources = [ "Russia", "Crimea", "Ukraine"]
  else:
    sources = sys.argv[1:]
    sources = [ s.decode("utf-8") for s in sources ]

  map(compute_source, sources)
