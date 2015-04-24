# -*- coding: utf-8 -*-

from __future__ import division
from collections import defaultdict

import numpy as np

import nltk

def compare(text1, text2):
  """
  Compare two texts using the Linguistic Style Matching (LSM) [1]_ method

  .. math::

     LSM_{preps} = 1 - \\frac{|preps_1 - preps_2|}{preps_1 + preps_2 + 0.0001}

  .. math::

     LSM = \\frac{ LSM_{personal pronouns}
     + LSM_{impersonal pronouns}
     + LSM_{articles}
     + LSM_{auxiliary verbs}
     + LSM_{high-frequency adverbs}
     + LSM_{prepositions}
     + LSM_{conjunctions}
     + LSM_{negations}
     + LSM_{quantifiers} }{9}

  Parameters
  ----------
  text1 : string
  text2 : string

  Returns
  -------
  lsm : dict

  References
  ----------

  .. [1] Amy L. Gonzales, Jeffrey T. Hancock, and James W. Pennebaker :
     Language Style Matching as a Predictor of Social Dynamics in Small Groups.
     Communication Research 37(1):3-19, 2010.
  """
  t1c = extract_categories(text1)
  t2c = extract_categories(text2)

  cat_list = [ k for k in t1c.keys() if not(k.startswith("total")) ]

  lsm = { k: 1 - abs(t1c[k] - t2c[k])/(t1c[k] + t2c[k] + 0.001) for k in cat_list }

  lsm["mean"] = np.mean(lsm.values())

  return lsm

def extract_categories(text):
  """
  Extract percentages of LSM word categories over total words counting

  Parameters
  ----------
  text : string

  Return
  ------
  categories : dict

  Examples
  --------

  >>> txt = "One morning, when Gregor Samsa woke from troubled dreams, he found himself transformed in his bed into a horrible vermin. He lay on his armour-like back, and if he lifted his head a little he could see his brown belly, slightly domed and divided by arches into stiff sections. The bedding was hardly able to cover it and seemed ready to slide off any moment. His many legs, pitifully thin compared with the size of the rest of him, waved about helplessly as he looked."
  >>> wekeypedia.lsm.extract_categories(txt)
  {'personal pronouns': 0.11578947368421053, 'articles': 0.06315789473684211, 'hf adverbs': 0.0, 'prepositions': 0.12631578947368421, 'total words': 95, 'impersonal pronouns': 0.010526315789473684, 'quantifiers': 0.021052631578947368, 'auxiliary verbs': 0.010526315789473684, 'negations': 0.0, 'conjunctions': 0.031578947368421054}
  """

  categories = extract_categories_raw(text)

  for k in [ k for k in categories.keys() if k != "total words" ]:
    categories[k] = len(categories[k])/categories["total words"]

  return categories

def extract_categories_raw(text):
  """
  Extract raw counting of LSM word categories

  Parameters
  ----------
  text : string

  Return
  ------
  categories : dict

  Examples
  --------

  >>> txt = "One morning, when Gregor Samsa woke from troubled dreams, he found himself transformed in his bed into a horrible vermin. He lay on his armour-like back, and if he lifted his head a little he could see his brown belly, slightly domed and divided by arches into stiff sections. The bedding was hardly able to cover it and seemed ready to slide off any moment. His many legs, pitifully thin compared with the size of the rest of him, waved about helplessly as he looked."
  >>> wekeypedia.lsm.extract_categories_raw(txt)
  {'personal pronouns': ['his', 'his', 'his', 'his', 'he', 'himself', 'He', 'he', 'he', 'him', 'he'], 'articles': ['a', 'a', 'The', 'any', 'the', 'the'], 'hf adverbs': [], 'prepositions': ['from', 'in', 'into', 'on', 'if', 'by', 'into', 'with', 'of', 'of', 'about', 'as'], 'total words': 95, 'impersonal pronouns': ['it'], 'quantifiers': ['many', 'any'], 'auxiliary verbs': ['was'], 'negations': [], 'conjunctions': ['and', 'and', 'and']}
  """
  text_tagged = nltk.pos_tag(nltk.word_tokenize(text))

  lemmatizer = nltk.WordNetLemmatizer()
  tags = defaultdict(list)

  for (word, tag) in text_tagged:
    tags[tag].append(word)

  for i in ["''", ",", ".", "``", ":", "-NONE-"]:
    tags.pop(i, None)

  impersonal = ["it", "this", "that", "its", "anything" ]

  def get_per_pronouns(tags):
    pt = [ tags[tag] for tag in tags.keys() if tag.startswith('PRP') ]
    pt = [ p for pl in pt for p in pl ]

    return [ p for p in pt if not(p.lower() in impersonal) ]

  def get_imp_pronouns(tags):
    pt = [ tags[tag] for tag in tags.keys() if tag.startswith('PRP') ]
    pt = [ p for pl in pt for p in pl ]

    return [ p for p in pt if p.lower() in impersonal ]

  def get_aux_verbs(tags):
    vt = [ tags[tag] for tag in tags.keys() if tag.startswith('V') ]
    vt = [ v for vl in vt for v in vl ]

    aux_verbs = [ "be", "have", "do", "will" ]

    return [ verb for verb in vt if lemmatizer.lemmatize(verb, nltk.corpus.wordnet.VERB) in aux_verbs ]

  def get_hf_adverbs(tags):
    advt = tags["RB"]
    return [ w for w in advt if w.lower() in [ "often", "well", "very", "frequently", "generally" ] ]

  def get_negations(tags):
    nt = tags["RB"]
    return [ w for w in nt if w.lower() in [ "not", "no", "never" ] ]

  def get_quantifiers(tags):
    qt = [ tags[tag] for tag in ["JJ", "JJR", "DT", "PDT" ] ]
    qt = [ q for ql in qt for q in ql ]

    quants = [ "all", "any", "both", "each", "enough", "every", "few", "fewer",
              "little", "less", "lots", "many", "more", "several", "some" ]

    return [ w for w in qt if w.lower() in quants ]

  categories = {
    "personal pronouns": get_per_pronouns(tags),
    "impersonal pronouns": get_imp_pronouns(tags),
    "articles": tags["DT"],
    "auxiliary verbs": get_aux_verbs(tags),
    "hf adverbs": get_hf_adverbs(tags),
    "prepositions": tags["IN"],
    "conjunctions": tags["CC"],
    "negations": get_negations(tags),
    "quantifiers": get_quantifiers(tags),
    "total words": len(text_tagged)
  }

  return categories
