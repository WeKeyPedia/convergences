load_pages = (data)->
  _(data).each (pages, lang)->
    ul = $(document.createElement('ul'))
      .addClass("pages")

    header = $(document.createElement('h4'))
      .addClass("lang")
      .html(lang)

    ul.append(header)

    _(pages).each (page)->
      li = $(document.createElement('li'))
        .addClass("page")

      li.html(page)

      li.on "click", ()->
        load_convergences(lang,page)

      ul.append(li)

    $("#list-pages").append(ul)

load_convergences = (lang, page)->
  $.get "/api/#{lang}/#{page}", (data)->
    div = $(document.createElement('div'))

    sorted = _(_.pairs(data["stats"])).sortBy (a)-> -a[1]["intersection"]

    source_lang = lang
    source_page = page

    _(sorted).each (array)->
      lang = array[0]
      page = data["langs"][lang]

      panel = $(document.createElement('div'))
        .addClass("page")
        .data("target_lang", lang)
        .on "click", ()->
          load_links(source_lang, source_page, $(this).data("target_lang"))

      h = $(document.createElement('div'))
        .addClass("title")
        .append($(document.createElement('span')).html(page))

      lg = $(document.createElement('span'))
        .addClass("lang")
        .html(lang)
        .appendTo(h)

      svg = $(document.createElement('div'))
        .addClass("convergence-viz")
        .append(draw_convergence_mini_bar(data["stats"][lang])[0])

      panel.append(h)
      panel.append(svg)

      div.append(panel)

      # li.append($(document.createElement('span')).addClass("page_lang").html(lang))

    $("#list-lang").html(div)

load_links = (source, page, target)->
  $.get "/api/#{source}/#{page}/#{target}", (data)->
    div = $(document.createElement('div'))

    target_page = data["pages"][target]

    source_href = "http://#{source}.wikipedia.org/wiki/#{page}"
    target_href = "http://#{target}.wikipedia.org/wiki/#{target_page}"

    source_a = "<a href=#{source_href}>[#{source}] #{page}</a>"
    target_a = "<a href=#{target_href}>[#{target}] #{target_page}</a>"

    source_links = data["translations"][source]
    target_links = data["translations"][target]

    source_untranslated = data["untranslated"][source]
    target_untranslated = data["untranslated"][target]

    intersection = $(document.createElement('div'))
      .appendTo(div)

    intersection.append($(document.createElement('h3')).addClass("small").html("Common links"))

    i = _.intersection(_(source_links).keys(), _(target_links).values())

    _(i).each (link)->
      a = $(document.createElement('a'))
        .attr("href", "http://#{source}.wikipedia.org/wiki/#{link}")
        .html(link)
        .appendTo(intersection)

    left_absent = $(document.createElement('div'))
      .appendTo(div)

    left_absent_h = $(document.createElement('h3'))
      .addClass("small")
      .html("Absent links from #{source_a} to #{target_a} ")
      .appendTo(left_absent)

    la = _.difference(_(source_links).keys(), _(target_links).values())

    _(la).each (link)->
      a = $(document.createElement('a'))
        .attr("href", "http://#{source}.wikipedia.org/wiki/#{link}")
        .html(link)
        .appendTo(left_absent)

    right_absent = $(document.createElement('div'))
      .appendTo(div)

    right_absent_h = $(document.createElement('h3'))
      .addClass("small")
      .html("Absent links from #{target_a} to #{source_a} ")
      .appendTo(right_absent)

    ra = _.difference(_(target_links).keys(), _(source_links).values())

    _(ra).each (link)->
      a = $(document.createElement('a'))
        .attr("href", "http://#{target}.wikipedia.org/wiki/#{link}")
        .html(link)
        .appendTo(right_absent)

    left_untranslated = $(document.createElement('div'))
      .appendTo(div)

    left_untranslated_h = $(document.createElement('h3'))
      .addClass("small")
      .html("Untranslated links from #{source_a}")
      .appendTo(left_untranslated)

    _(source_untranslated).each (link)->
      a = $(document.createElement('a'))
        .attr("href", "http://#{source}.wikipedia.org/wiki/#{link}")
        .html(link)
        .appendTo(left_untranslated)

    right_untranslated = $(document.createElement('div'))
      .appendTo(div)

    right_untranslated_h = $(document.createElement('h3'))
      .addClass("small")
      .html("Untranslated links from #{target_a}")
      .appendTo(right_untranslated)

    _(target_untranslated).each (link)->
      a = $(document.createElement('a'))
        .attr("href", "http://#{target}.wikipedia.org/wiki/#{link}")
        .html(link)
        .appendTo(right_untranslated)


    $("#list-links").html(div)

draw_convergence_mini_bar = (stats)->
  svg = d3.select(document.createElement("div")).append("svg")
    # .attr("width", 300).attr("height", 20)

  max = stats["left"] + stats["right"]  - stats["intersection"]
  scale = d3.scale.linear().domain([0, max]).range([0, 300])

  ri = parseInt(scale(stats["intersection"]))

  r1 = parseInt(scale(stats["left_absent"]))
  r2 = parseInt(scale(stats["right_absent"]))

  rua = parseInt(scale(stats["left_untranslated"]))
  rub = parseInt(scale(stats["right_untranslated"]))

  x = 0
  svg.append("rect")
    .attr("width", rua)
    .attr("height", 20)
    .attr("x", 0)
    .attr("y", 0)
    .attr("stroke", "none")
    .attr("fill", "red")
    .attr("opacity", 0.25)

  x += rua
  svg.append("rect")
    .attr("width", r1)
    .attr("height", 20)
    .attr("x", x)
    .attr("y", 0)
    .attr("stroke", "none")
    .attr("fill", "red")
    .attr("opacity", 0.4)

  x += r1
  svg.append("rect")
    .attr("width", ri)
    .attr("height", 20)
    .attr("x", x)
    .attr("y", 0)
    .attr("stroke", "none")
    .attr("fill", "red")
    .attr("opacity", 0.7)

  x += ri
  svg.append("rect")
    .attr("width", r2)
    .attr("height", 20)
    .attr("x", x)
    .attr("y", 0)
    .attr("stroke", "none")
    .attr("fill", "red")
    .attr("opacity", 0.4)

  x += r2
  svg.append("rect")
    .attr("width", rub)
    .attr("height", 20)
    .attr("x", x)
    .attr("y", 0)
    .attr("stroke", "none")
    .attr("fill", "red")
    .attr("opacity", 0.25)

  return svg

draw_convergence_mini = (stats)->
  svg = d3.select(document.createElement("div")).append("svg").attr("width", 300).attr("height", 200)

  max = d3.max(_(stats).values())
  scale = d3.scale.linear().domain([0, max]).range([10, 100])

  ri = scale(stats["intersection"])
#  ri = 50

  rua = scale(stats["left_untranslated"])
  rub = scale(stats["right_untranslated"])

  r1 = scale(stats["left_absent"]) + ri
  r2 = scale(stats["right_absent"]) + ri
  ra = scale(stats["left"])
  rb = scale(stats["right"])

  offset = 150

  svg.append("circle")
    .attr("r", ra)
    .attr("cx", - (ra - r1) - ri*2)
    .attr("cy", 100)
    .attr("stroke", "black")
    .attr("fill", "none")
    .attr("opacity", 0.4)

  svg.append("circle")
    .attr("r", r1)
    .attr("cx", 0 )
    .attr("cy", 100)
    .attr("opacity", 0.4)
    .attr("stroke", "none")

  svg.append("circle")
    .attr("r", r2)
    .attr("cx", r1 + r2 - ri*2)
    .attr("cy", 100)
    .attr("opacity", 0.4)
    .attr("stroke", "none")

  svg.append("circle")
    .attr("r", rb)
    .attr("cx", r1 + rb)
    .attr("cy", 100)
    .attr("stroke", "black")
    .attr("fill", "none")
    .attr("opacity", 0.4)

  return svg

$(document).ready ()->
  $.get("/api/list",load_pages)
  load_convergences("en", "Love")
  load_links("en", "Love", "fr")
