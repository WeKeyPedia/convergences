import requests

api_endpoint  = "http://api.wekeypedia.net"

class WeKeyApi:
  def __init__(self):
    self.endpoint = api_endpoint

  def get(self, query):
    return requests.get("%s/%s" % (self.endpoint, query))

  def get_pages(self):
    r = self.get("pages")

    return r.json()