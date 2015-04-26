# -*- coding: utf-8 -*-

from __future__ import division
import sys
from math import ceil

from collections import defaultdict

import codecs
import json

from multiprocessing import Pool as ThreadPool


def stats(page, source, target):

  if target in ignore_langs:
    return

  with codecs.open("data/{1}.{0}/{1}.json".format(page, source, target), "r", "utf-8-sig") as f:
    left_links = json.load(f)

  with codecs.open("data/{1}.{0}/{1}.{2}.json".format(page, source, target), "r", "utf-8-sig") as f:
    left_links_translated = json.load(f)

  with codecs.open("data/{1}.{0}/{2}.json".format(page, source, target), "r", "utf-8-sig") as f:
    right_links = json.load(f)

  with codecs.open("data/{1}.{0}/{2}.{1}.json".format(page, source, target), "r", "utf-8-sig") as f:
    right_links_translated = json.load(f)

  # print set(left_links) - { x[0] for x in left_links_translated.items() }

  stats = {
    "left": len(left_links),
    "right": len(right_links),
    "left_untranslated": len(set(left_links) - { x[0] for x in left_links_translated.items() }),
    "left_absent": len( { x[1] for x in left_links_translated.items() } - set(right_links)),
    "intersection": len({ x[0] for x in left_links_translated.items()  } & { x[1] for x in right_links_translated.items() }),
    "right_absent": len(  { x[1] for x in right_links_translated.items() } - set(left_links)),
    "right_untranslated": len(set(right_links) - { x[0] for x in right_links_translated.items() })
  }

  return stats

def compute_stats(source):
  lang = "en"

  if "#" in source:
    lang = source.split("#")[1]
    source = source.split("#")[0]

  langlinks = json.load(codecs.open("data/{1}.{0}.json".format(source, lang), "r", "utf-8-sig"))

  result = { l: stats(source, lang, l) for l in langlinks.keys() }

  with codecs.open("data/{1}.{0}.stats.json".format(source, lang), "w", "utf-8-sig") as f:
    json.dump(result, f, ensure_ascii=False, indent=2, separators=(',', ': '))

ignore_langs = [ "th" ]
ignore_langs = []

if __name__ == "__main__":
  if len(sys.argv) < 2:
    sources = ["Love", "Revolution", "Wisdom", "Ethics", "Morality", "Surveillance"]
    sources = [ "Russia", "Crimea", "Ukraine"]
  else:
    sources = sys.argv[1:]
    print sources

  map(compute_stats, sources)
