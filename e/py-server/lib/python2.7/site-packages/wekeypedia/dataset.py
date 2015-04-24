from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

import json

class Dataset():
  def __init__(self, mongo_conf):
    client = MongoClient("mongodb://%s/" % (mongo_conf))

    self.db = client["datasets"]

  def write(self, key, value):
    # print key
    # print json.JSONEncoder().encode(value)

    item = {
      "url": key,
      "dataset": value
    }

    try:
      print "inserting: %s" % (key)
      self.db.datasets.insert(item)
    except DuplicateKeyError:
      # print "duplicated entry: %s" % (key)
      pass

  def delete(self,key):
    self.db.datasets.remove({ "url": key })

  def read(self, key):
    item = {
      "url": key
    }

    value = self.db.datasets.find_one(item)

    return value

  def find(self, query, filter={}):
    return self.db.datasets.find(query, filter)