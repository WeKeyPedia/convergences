import mwparserfromhell as mw

class Mediawiki:
  def __init__(self, txt=""):
    self.text = self.parse(txt)

  def parse(self,txt):
    return mw.parse(txt)


  def get_headings(self):
    return self.text.filter_headings()

  def get_blocks(self):
    sections = []
    structure = []

    nodes = self.text.get_sections(include_lead=True, flat=True)

    n_index = 0

    for n in nodes:
      section = []

      node = mw.parse(n)

      # print ""

      start_at = 1
      previous_level = 2

      if len(node.filter_headings())>0:
        h = node.filter_headings()[0]

        # print h.level
        # print h.title

        # if(h.level <= previous_level):
        #   structure.append([ h.level ])
        # else:
        #   structure[-1].append([ h.level ])
        
        previous_level = h.level

        section.append( len( h.title ) )
      else:
        section.append(0)
        start_at = 0

      stripped_text = node.strip_code()

      # structure.append( "%s:%s" % (previous_level, n_index) )
      structure.append( previous_level )

      paragraphs = stripped_text.split("\n\n")[start_at:]

      for p in paragraphs:
        for w in p.split(" "):
          section.append(len(w))

        section.append(0)

      # print section
      sections.append(section)

      n_index += 1

    return sections, structure