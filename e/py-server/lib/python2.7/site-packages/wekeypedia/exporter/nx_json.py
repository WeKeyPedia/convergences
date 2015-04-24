import codecs
import json

import networkx as nx
from networkx.readwrite import json_graph

class NetworkxJson:
  def __init__(self, graph):
    self.graph = graph

  def nx_export(self, export_type, output_file):
    data = getattr(json_graph, "%s_data" % export_type)(self.graph)

    target = codecs.open(output_file, "w", "utf-8")
    json.dump(data,target, sort_keys=True, indent=2, ensure_ascii=False)
    print "export node-link: %s" % output_file