# -*- coding: utf-8 -*-

from __future__ import division

import os
import sys

from math import ceil

from collections import defaultdict

import codecs
import json

from multiprocessing import Pool as ThreadPool

import click
from pync import Notifier

import wekeypedia
from wekeypedia.wikipedia.api import api as api

from generate_stats import compute_stats

data_dir = "data"

options = {
  "force": False
}

def api_bunch(page_titles, lang, req):
  results = defaultdict(list)
  param  = req

  w = api(lang)

  # print len(page_titles)

  for i in range(0,int(ceil(len(page_titles)/50))):
    param["titles"] = "|".join(page_titles[i*50:i*50+50])

    while True:
      r = w.get(param, method="post")

      if hasattr(r, 'status_code'):
        click.secho("Request error", bg="red", fg="black")
        print r
        continue

      for pageid, p in r["query"]["pages"].items():
        if "langlinks" in p:
          results[ p["title"] ].extend(p['langlinks'])

      # results.update({ p["title"]: p['langlinks'] for pageid, p in r["query"]["pages"].items() if 'langlinks' in p })

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
    params["titles"] = "|".join(pages[i*50:i*50+50])
    resp = w.post(params)

    if hasattr(resp, 'status_code'):
      click.secho("Request error", bg="red", fg="black")
      print resp
      continue

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

  #links = list({ x["title"] for x in p.get_links() })
  links = replace_redirects(list({ x["title"] for x in p.get_links() }), p.lang)

  print( u"[{0}][{3}] {1} ---> {2} links".format(source, p.title, len(links), target) )

  if not skip:
    write(u"data/{0}/{1}.json".format(dataset_name, source), links)

  links_translated = get_lang_projection(links, source, target)

  links_translated_redirects = replace_redirects(list({ x[1] for x in links_translated }), target, False)

  links_translated = { x[0]: links_translated_redirects.setdefault(x[1], x[1]) for x in links_translated }

  write(u"data/{0}/{1}.{2}.json".format(dataset_name, source, target), links_translated)

def write(filename, data):
  with codecs.open(filename, "w", "utf-8-sig") as f:
    json.dump(data, f, ensure_ascii=False, indent=2, separators=(',', ': '))

def m(args):
  lang = args[0]
  page = args[1]
  p_lang = args[2]
  p_title = args[3]
  options = args[4]

  if lang in ignore_langs:
    return

  if options["force"] or not os.path.isfile(u"data/{1}.{0}/{3}.{1}.json".format(p_title, p_lang, page, lang)):
    from_to(page, lang, p_lang, u"{1}.{0}".format(p_title, p_lang))

  if options["force"] or not os.path.isfile(u"data/{1}.{0}/{1}.{3}.json".format(p_title, p_lang, page, lang)):
    from_to(p_title, p_lang, lang, u"{1}.{0}".format(p_title, p_lang), skip=True)

def compute_source(source):
  # source = "Love" # "Love"

  lang = "en"

  if "#" in source:
    lang = source.split("#")[1]
    source = source.split("#")[0]

  Notifier.notify('begining download for {1} ({0})'.format(lang, source), title='generate_dataset.py')

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

  pool.map(m, [ (x[0], x[1], p.lang, p.title, options) for x in available_langs.items() ] )

  Notifier.notify('download for {1} ({0}) is finised'.format(lang, source), title='generate_dataset.py')

  pool.close()
  pool.join()

ignore_langs = []

def reset():
  pass

def current_datasets():
  result = defaultdict(list)

  files = [ f for f in os.listdir(data_dir) if os.path.isfile("/".join([ data_dir,f ])) ]

  for f in [ f for f in files if "stats" not in f ]:
    lang,page,format = f.split(".")
    result[lang].append(page)

  return result

@click.command()
@click.option("--datasets", help="list of current datasets", is_flag=True)
@click.option("--reset", help="remove all datasets", is_flag=True)
@click.option("--force","-f", help="force dataset creation", is_flag=True)
@click.option("--page", "-p", default=[], help="list of pages", multiple=True)
def cli(page, datasets, reset, force):
  options["force"] = force

  if datasets:
    datasets = current_datasets()

    for l in datasets.keys():
      click.echo(l)
      click.echo("-"*len(l))

      for p in datasets[l]:
        click.echo(p)

      click.echo("")

  if len(page) > 0:
    sources = page
    sources = [ s for s in sources ]

    click.echo(sources)

    map(compute_source, sources)

    click.echo("computing statistics")
    map(compute_stats, sources)

if __name__ == "__main__":
  cli()
