# -*- coding: utf-8 -*-

from __future__ import division

import os

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
      r = w.get(param)
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
    resp = w.get(params)

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

  print( u"[{0}] {1} ---> {2} links".format(source, p.title, len(links)) )

  if not skip:
    with codecs.open("data/{0}/{1}.json".format(dataset_name, source), "w", "utf-8-sig") as f:
      json.dump(links, f, ensure_ascii=False, indent=2, separators=(',', ': '))


  links_translated = get_lang_projection(links, source, target)

  links_translated_redirects = replace_redirects(list({ x[1] for x in links_translated }), target, False)

  links_translated = { x[0]: links_translated_redirects.setdefault(x[1], x[1])  for x in links_translated }

  with codecs.open("data/{0}/{1}.{2}.json".format(dataset_name, source, target), "w", "utf-8-sig") as f:
    json.dump(links_translated, f, ensure_ascii=False, indent=2, separators=(',', ': '))


def m(args):
  lang = args[0]
  page = args[1]
  p_lang = args[2]
  p_title = args[3]

  from_to(page, lang, p_lang, "{1}.{0}".format(p_title, p_lang))
  from_to(p_title, p_lang, lang, "{1}.{0}".format(p_title, p_lang), skip=True)

def compute_source(source):
  # source = "Love" # "Love"

  p = wekeypedia.WikipediaPage(source)

  links = replace_redirects(list({ x["title"] for x in p.get_links() }), p.lang)

  print("links: {0}".format(len(links)))

  if not os.path.exists("data/{1}.{0}".format(source, p.lang)):
      os.makedirs("data/{1}.{0}".format(source, p.lang))

  with codecs.open("data/{1}.{0}/{1}.json".format(source, p.lang), "w", "utf-8-sig") as f:
    json.dump(links, f, ensure_ascii=False, indent=2, separators=(',', ': '))

  available_langs = { x["lang"]: x["*"] for x in p.get_langlinks() }

  with codecs.open("data/{1}.{0}.json".format(source, p.lang), "w", "utf-8-sig") as f:
    json.dump(available_langs, f, ensure_ascii=False, indent=2, separators=(',', ': '))

  # for lang, page in available_langs.items():
  #   from_to(page, lang, p.lang, p.title)
  #   from_to(p.title, p.lang, lang, p.title, skip=True)

  # map(m, available_langs.items())

  pool = ThreadPool(4)

  pool.map(m, [ (x[0], x[1], p.lang, p.title) for x in available_langs.items() ] )

  pool.close()
  pool.join()

if __name__ == "__main__":
  sources = ["Love", "Revolution", "Wisdom", "Ethics", "Morality", "Surveillance"]
  sources = [ "Ethics", "Morality", "Surveillance"]

  map(compute_source, sources)
