import os

import json

class Dataset:
  def __init__(self, dir=""):
    self.dir = dir

  def get_revision_content(self, page, rev_id):
    f = open( "%s/%s/revisions/%s.json" % (self.dir,page,rev_id), "r")

    return json.load(f)[0]["*"]