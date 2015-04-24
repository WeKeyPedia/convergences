# -*- coding: utf-8 -*-

from __future__ import division
from math import ceil

from collections import defaultdict

import codecs
import json

from multiprocessing import Pool as ThreadPool


def stats(page, source, target):
  with codecs.open("data/{0}/{1}.json".format(page, source, target), "r", "utf-8-sig") as f:
    left_links = json.load(f)

  with codecs.open("data/{0}/{1}.{2}.json".format(page, source, target), "r", "utf-8-sig") as f:
    left_links_translated = json.load(f)

  with codecs.open("data/{0}/{2}.json".format(page, source, target), "r", "utf-8-sig") as f:
    right_links = json.load(f)

  with codecs.open("data/{0}/{2}.{1}.json".format(page, source, target), "r", "utf-8-sig") as f:
    right_links_translated = json.load(f)


  print set(left_links) - { x[0] for x in left_links_translated.items() }

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

if __name__ == "__main__":
  source = "Wisdom" # "Love"

  langlinks = json.load(codecs.open("data/en.{0}.json".format(source), "r", "utf-8-sig"))

  result = { l: stats(source, "en", l) for l in langlinks.keys() }

  with codecs.open("data/{1}.{0}.stats.json".format(source, "en"), "w", "utf-8-sig") as f:
    json.dump(result, f, ensure_ascii=False, indent=2, separators=(',', ': '))

  # def m(args):
  #   lang = args[0]
  #   page = args[1]
  #
  #   from_to(page, lang, p.lang, p.title)
  #   from_to(p.title, p.lang, lang, p.title, skip=True)
  #
  # pool = ThreadPool(8)
  #
  # pool.map(m, available_langs.items())
  #
  # pool.close()
  # pool.join()
