# -*- coding: utf-8 -*-
import sys

# import wikipedia
import urllib
from collections import defaultdict

try:
  from urllib.parse import unquote
except ImportError:
  from urllib import unquote

from bs4 import BeautifulSoup
import requests
import nltk

from colorama import Fore

from datetime import date

from wekeypedia.wikipedia.api import api as API

def url2title(url):
  """
  Transform an url into a title

  Parameters
  ----------
  url : string

  Returns
  -------
  title : string
  """
  title = url.split("/")

  if(len(title) > 4):
    title = title[4]
    title = title.encode("ascii")
    title = unquote(title).decode("utf8")
    title = title.replace("_", " ")
  else:
    title = title[3]

  return title

def url2lang(url):
  """
  Transform an language code into a title

  Parameters
  ----------
  url : string

  Returns
  -------
  lang : string
  """
  lang = url.split("/", 3)[2]
  lang = lang.split(".")[0]

  return lang

class WikipediaPage(object):
  """

  - http://www.mediawiki.org/wiki/API:Query
  - http://www.mediawiki.org/wiki/API:Revisions

  """
  def __init__(self, title=None, lang="en"):
    self.ready = False
    self.query = None
    self.page = None
    self.problem = None
    self.data = {}

    self.content = ""

    self.lang = lang

    if (title):
      title = title.strip()
      self.fetch_info(title, lang=self.lang)

  def fetch_info(self, title, opt_params={ "prop": "info", "inprop": "url" }, lang="en"):
    api = API(lang)

    params = {
      "format": "json",
      "action": "query",
      "titles": u""+title
      # "rvprop": "content",
      # "redirects": ""
    }

    params.update(opt_params)

    r = api.get(params)
    # print r.json()

    pages = r["query"]["pages"]

    self.page_id = list(pages.keys())[0]
    self.title = pages[ self.page_id ]["title"]
    self.lang = lang
    self.url = pages[ self.page_id ]["fullurl"]

    self.data.update(pages[ self.page_id ])

    # print r.url
    # print r.text

    return r

  def get_editors(self, revisions_list=[]):
    """
    Retrieve revisions and extract editors

    Parameters
    ----------
    revisions_list : list, optional
      If a list of revisions id is passed as an argument, the
      method will filter out the revisions that are in that list
      while still retrieving the list of all revisions firsts.

      A more optimal rewriting will be to fetch only the selected
      revisions.

    Returns
    -------
    editors : list
    """
    editors = []

    revisions = self.get_revisions_list()

    if len(revisions_list) > 0:
      revisions = [ r for r in revisions if r["revid"] in revisions_list ]

    editors = [ r["user"] for r in revisions ]

    return editors

  def get_revision(self, revid="", force=False, extra_params = {}):
    """
    Retrieve the content of a revision by its revision id

    For more paramaters, you can check the `wikipedia API <http://www.mediawiki.org/wiki/API:Revisions>`_
    documentation.

    Examples
    --------

    >>> p = WikipediaPage("Pi")
    >>> p.get_content()

    Parameters
    ----------
    revid : string, optional
      Revision id of the article. If none is given, it just check the last
      revision id give by the wikipedia API
    force : boolean, optional
      If set to `True`, it fetch the content whatever is in the cache object.
      Useful to retrieve different version without touching the cache
    extra_params : dict
      todo: document extra_params@get_content

    Returns
    -------
    content : string
      todo: document content@get_content
    """

    if (force == False) and (self.content != "") and (revid == ""):
      content = self.content
      return content

    q = {
      "redirects":"true",
      "rvparse" : "true",
      "prop": "info|revisions",
      "inprop": "url",
      "rvprop": "content"
    }

    if revid != "":
      q["rvstartid"] = revid
      q["rvlimit"] =  1

    # add extra parameters to current query
    q.update(extra_params)

    json = self.fetch_info(self.title, q)

    content = json["query"]["pages"][list(json["query"]["pages"].keys())[0]]
    content = content["revisions"][0]["*"]

    if force == False:
      self.content = content

    return content

  def get_current(self):
    """
    Retrieve the content of the current revision

    Return
    ------
    content : string
    """
    return self.get_revision()

  def get_diff_full(self, rev_id=""):
    """
    Retrieve the full json response from a request for diff.

    Parameters
    ----------
    rev_id : string, optional
      If no revision id is supplied, the method retrieve the diff from the
      current version of the page and compare it to its predecessor.
    """
    api = API(self.lang)

    q = {
      "format": "json",
      "action": "query",
      "titles": self.title,
      "redirects":"true",
      #"rvparse" : "true",
      "prop": "info|revisions",
      "inprop": "url",
      # "rvlimit": 1,
      # "rvprop": "content",
      "rvdiffto" : "prev"
    }

    if rev_id != "":
      q.update({ "rvlimit":1, "rvstartid": rev_id })

    r = api.get(q)

    return r

  def extract_diff_text(self, response):
    r = response

    content = r["query"]["pages"][list(r["query"]["pages"].keys())[0]]

    if "diff" in content["revisions"][0]:
      content = content["revisions"][0]["diff"]["*"]
    else:
      content = False
    # content = BeautifulSoup(content, 'html.parser')

    return content

  def get_diff(self, rev_id=""):
    """
    Retrieve diff content between a revision and its predecessor. The content
    is extracted from the API json response. To get the full response, you can
    still use `get_diff_full`

    Examples
    --------

    Parameters
    ----------
    rev_id : string, optional
      If no revision id is supplied, the method retrieve the diff from the
      current version of the page and compare it to its predecessor.

    Returns
    -------
    content : string

    See Also
    --------
    get_diff_full

    """
    r = self.get_diff_full(rev_id)

    return self.extract_diff_text(r)

  def get_revisions_list(self, extra_params={}):
    """
    Retrieve all the revisions and their info

    Return
    ------
    revisions : list
    """
    api = API()

    revisions = []

    params = {
      "format": "json",
      "action": "query",
      "titles": self.title,
      "prop": "revisions",
      "rvprop": "user|userid|timestamp|size|ids|sha1|comment",
      "rvlimit": "max",
      "redirects": "",
      "continue": ""
    }

    while True:
      r = api.get(params)

      pages = r["query"]["pages"]
      page = pages[ list(pages.keys())[0] ]

      revisions += page["revisions"]

      if "continue" in r:
        params.update(r["continue"])
      else:
        break

    return revisions

  def get_revisions(self, extra_params={}):
    """
    Parameters
    ----------
    extra_params : dictionary

    Returns
    -------
    revisions : list
      todo: document revisions@get_revisions
    """
    api = API()

    params = {
      "format": "json",
      "action": "query",
      "titles": self.title,
      "prop": "revisions",
      "rvprop": "user|userid|timestamp|size|ids|sha1|comment|content",
      "rvlimit": "max",
      "redirects": "",
      "continue": ""
    }

    params.update(extra_params)

    # print params

    revisions = []

    while True:
      r = api.get(params)

      # print r
      pages = r["query"]["pages"]
      page = pages[ list(pages.keys())[0] ]

      revisions += page["revisions"]

      if "continue" in r:
        params.update(r["continue"])
      else:
        break

    return revisions

  def get_langlinks(self):
    """
    Retrieve the list of hyperlinks to translation of the current page

    Returns
    -------
    langlinks : list
      List of language codes (e.g "en", "fr", "es", "ru", etc)
      todo: put a link to a page with the list of languages
    """
    api = API(self.lang)

    langlinks = []

    params = {
      "format": "json",
      "action": "query",
      "titles": self.title,
      "prop": "langlinks",
      "lllimit": 500
    }

    r = api.get(params)

    # print r

    page = r["query"]["pages"][ list(r["query"]["pages"].keys())[0] ]

    if ("langlinks" in page):
      langlinks += page["langlinks"]

    return langlinks

  def get_pageviews(self, fr="200712", to=""):
    """
    Retrieve daily page view statistics from http://stats.grok.se/

    Parameters
    ----------
    fr : string, optional
      Start of the range (minimum is december 2007) represented as `yearmonth` (`%Y%m`).

    to : string, optional
      End of the range represented as `yearmonth` (`%Y%m`).

      If no end date is given, the current date is used as an end date.

    Returns
    -------
    pageviews : list
      List of page views per day represented as tuples `[(day, views),...]`

    """
    results = []

    base_url = "http://stats.grok.se/json/%s" % (self.lang)

    if (to == ""):
      year_end = date.today().year
      month_end = date.today().month
    else:
      year_end = int(to[:4])
      month_end = int(to[4:])

    year_start = int(fr[:4])
    month_start = int(fr[4:])

    # print "from: %(year)4d-%(month)02d" % { "year": year_start, "month": month_start }
    # print "to: %(year)4d-%(month)02d" % { "year": year_end, "month": month_end }

    for y in range(year_start, year_end+1):
      m_start = month_start if (y == year_start) else 1
      m_end = month_end if (y == year_end) else 12

      for m in range(m_start, m_end+1):

        url_params = {
          "url": base_url,
          "year": y,
          "month": m,
          "title": self.title
        }

        month_url = "%(url)s/%(year)4d%(month)02d/%(title)s" % url_params
        # print month_url
        r = requests.get(month_url).json()
        results.append(r["daily_views"])

    return results


  def get_links(self, extra_params={}):
    """
    Retrieve links contained by a wikipedia page according to the API

    Parameters
    ----------
    extra_params : dict, optional
      By default, the method will only retrieve links from the namespace 0
      (usual pages) and skipped everything like templates, etc.

      You can still get `the other namespaces
      <http://en.wikipedia.org/wiki/Wikipedia:Namespace>`_ by updating the query
      with an extra parameters.

      >>> p.get_links({ plnamspace: 12 })

    Returns
    -------
      links : list

    See Also
    --------
    """
    links = []

    api = API(self.lang)

    params = {
      "format": "json",
      "action": "query",
      "titles": self.title,
      "prop": "links",
      "pllimit": 500,
      "plnamespace": 0,
      "continue":""
    }

    params.update(extra_params)

    while True:
      r = api.get(params)

      if "links" in r["query"]["pages"][ self.page_id ]:
        l = r["query"]["pages"][ self.page_id ]["links"]
        links.extend(l)

      if "continue" in r:
        params.update(r["continue"])
      else:
        break

    return links

  def get_categories(self, extra_params={}):
    """
    Retrieve a list of all categories used on the provided pages

    Parameters
    ----------
    extra_params : dict, optional
      - http://www.mediawiki.org/wiki/API:Property/Categories
    Returns
    -------
      links : list

    See Also
    --------
    """

    categories = []

    api = API(self.lang)

    params = {
      "format": "json",
      "action": "query",
      "titles": self.title,
      "prop": "categories",
      "cllimit": 500,
      "continue":""
    }

    while True:
      r = api.get(params)

      c = r["query"]["pages"][ self.page_id ]["categories"]

      categories.extend(c)

      if "continue" in r:
        params.update(r["continue"])
      else:
        break

    return categories

  def normalize(self, word):
    lemmatizer = nltk.WordNetLemmatizer()
    stemmer = nltk.stem.porter.PorterStemmer()

    word = word.lower()
    word = stemmer.stem_word(word)
    word = lemmatizer.lemmatize(word)

    return word

  def extract_plusminus(self, diff_html):
    """
    Transform HTML Wikipedia API response into a plus/minus dict. Information
    extraction is made with
    `BeautifulSoup <https://beautiful-soup-4.readthedocs.org/>`_

    Parameters
    ----------
    diff_html : string

    Return
    ------
    diff : dict
      `diff` contains two keys: diff["added"] and diff["deleted"]. Each of
      those entries correspond to blocks and inline extraction of addition,
      deletion and substition.

    See Also
    --------
    count_stems
    """

    diff = { "added": [], "deleted" : [] }

    d = BeautifulSoup(diff_html, 'html.parser')

    tr = d.find_all("tr")

    for what in [ ["added", "ins"], ["deleted", "del"] ]:
      a = []

      # checking block
      # we also check this is not only context showing for non-substition edits
      a = [ t.find("td", "diff-%sline" % (what[0])) for t in tr if len(t.find_all(what[1])) == 0 and len(t.find_all("td", "diff-empty")) > 0 ]

      # checking inline
      a.extend(d.find_all(what[1]))

      # filtering empty extractions
      a = [ x for x in a if x != None ]

      # registering
      diff[what[0]] = [ tag.get_text() for tag in a ]

    return diff

  def count_stems(self, sentences, inflections=None):
    """
    Count the number of stems in a list of sentences.

    An optional parameter allows to provide an inflections dictionary in order
    to register them. It can be usefull when looking for the most used form of
    a stem to produce more readable outputs.

    This function use a dummy normalizer (`self.normalize`) that take a
    tokenized sentences using the Punkt NTLK parser and apply a simple word
    normalization process (lowercase, stemmization, lemmatization).

    Parameters
    ----------
    sentences : list
    inflections : dict, optional

    Returns
    -------
    stems : dict

    See Also
    --------
    extract_plusminus
    """
    stems = defaultdict(int)

    ignore_list = "{}()[]<>./,;\"':!?&#=*&%"

    for sentence in sentences:
      for word in nltk.word_tokenize(sentence):
        old = word

        word = self.normalize(word)

        if not(word in ignore_list):
          stems[word] += 1

          # keeping track of inflection usages
          if inflections != None:
            inflections[word].setdefault(old,0)
            inflections[word][old] += 1

    return stems

  def print_plusminus_overview(self, diff):
    for minus in diff["deleted"]:
      print "- %s" % (minus)

    for plus in diff["added"]:
      print "+ %s" % (plus)


  def print_plusminus_terms_overview(self, stems):
    print "\n%s|%s\n" % ("+"*len(stems["added"].items()), "-"*len(stems["deleted"].items()))
