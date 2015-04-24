# -*- coding: utf-8 -*-

import csv

class Mapping:
  def __init__(self, mapping):
    self.mapping = mapping

  def csv(self, output):

    with open(output, "wb") as csv_file:
      w = csv.writer(csv_file)

      w.writerow([ "textbook", "wikipedia", "problem" ])

      for correspondance in self.mapping:
        w.writerow([ correspondance['query'],
          correspondance['page'],
          correspondance['problem'] ])