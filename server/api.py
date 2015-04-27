import json
import codecs

from collections import defaultdict

from os import listdir
from os.path import isfile, join

import flask
from flask import Flask
from flask import jsonify
from flask import render_template


app = Flask(__name__)

# API

data_dir = "../data"

@app.route("/api/list")
def get_list():
  result = defaultdict(list)

  files = [ f for f in listdir(data_dir) if isfile(join(data_dir,f)) ]

  for f in [ f for f in files if "stats" not in f ]:
    lang,page,format = f.split(".")
    result[lang].append(page)

  return jsonify(result)

@app.route("/api/<lang>/<page>")
def get_page(lang, page):
  response = ""

  langs = json.load(codecs.open(u"{0}/{1}.{2}.json".format(data_dir, lang, page), "r", "utf-8-sig"))
  stats = json.load(codecs.open(u"{0}/{1}.{2}.stats.json".format(data_dir, lang, page), "r", "utf-8-sig"))

  response = {
    "langs": langs,
    "stats": stats
  }

  return jsonify(response)

@app.route("/api/<lang>/<page>/<target>")
def get_page_correspondances(lang, page, target):

  response = {
    "pages": {
      lang: {},
      target: {}
    },
    "links": {
      lang: {},
      target: {}
    },
    "translations": {
      lang: {},
      target: {}
    },
    "untranslated": {
      lang: {},
      target: {}
    }
  }

  langs = json.load(codecs.open(u"{0}/{1}.{2}.json".format(data_dir, lang, page), "r", "utf-8-sig"))
  response["pages"][lang] = page
  response["pages"][target] = langs[target]

  source_links = codecs.open(u"{0}/{1}.{2}/{1}.json".format(data_dir, lang, page, target), "r", "utf-8-sig")
  target_links = codecs.open(u"{0}/{1}.{2}/{3}.json".format(data_dir, lang, page, target), "r", "utf-8-sig")

  target_lang = codecs.open(u"{0}/{1}.{2}/{3}.{1}.json".format(data_dir, lang, page, target), "r", "utf-8-sig")
  lang_target = codecs.open(u"{0}/{1}.{2}/{1}.{3}.json".format(data_dir, lang, page, target), "r", "utf-8-sig")

  response["links"][lang] = json.load(source_links)
  response["links"][target] = json.load(target_links)
  response["translations"][lang] = json.load(lang_target)
  response["translations"][target] = json.load(target_lang)
  response["untranslated"][lang] = list(set(response["links"][lang]) - { k for k,v in response["translations"][lang].items() })
  response["untranslated"][target] = list(set(response["links"][target]) - { k for k,v in response["translations"][target].items() })

  return jsonify(response)

# WEB
@app.route("/page/<source>/<page>")
@app.route("/page/<source>/<page>/<target>")
@app.route("/about")
@app.route("/")
def site(**args):
  return render_template("app.html")

if __name__ == "__main__":
    app.run(debug=True)
