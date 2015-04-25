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

    sorted = _(_.pairs(data["stats"])).sortBy (a)->
      -((a[1]["intersection"]/a[1]["left"]) + (a[1]["intersection"]/a[1]["left"])) * 0.5

    source_lang = lang
    source_page = page

    load_links(lang, page, sorted[0][0])

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

    source_a = "<a href=#{source_href}>#{page} <span>#{source}</span></a>"
    target_a = "<a href=#{target_href}>#{target_page} <span>#{target}</span></a>"

    source_links = data["translations"][source]
    target_links = data["translations"][target]

    source_untranslated = data["untranslated"][source]
    target_untranslated = data["untranslated"][target]

    $.get "/api/#{source}/#{page}", (data)=>
      # console.log source
      svg = $(document.createElement('div'))
        .addClass("convergence-viz")
        .append(draw_convergence_menu(data["stats"][target], source_a, target_a)[0])
        .prependTo(div)

    list = (items, direction)->
      d = $(document.createElement('div')).addClass("list")

      _(items).each (i)->
        a = $(document.createElement('a'))
          .attr("href", "http://#{direction}.wikipedia.org/wiki/#{i}")
          .html(i)
          .appendTo(d)

      d

    intersection = $(document.createElement('div'))
      .appendTo(div)

    intersection_h = $(document.createElement('h3'))
      .addClass("small")
      .html("Common links between #{source_a} and #{target_a}")
      .appendTo(intersection)

    i = _.intersection(_(source_links).keys(), _(target_links).values())

    list(i, source)
      .appendTo(intersection)

    left_absent = $(document.createElement('div'))
      .appendTo(div)

    left_absent_h = $(document.createElement('h3'))
      .addClass("small")
      .html("Links which are on #{source_a} but not on #{target_a} ")
      .appendTo(left_absent)

    la = _.difference(_(source_links).keys(), _(target_links).values())

    list(la, source)
      .appendTo(left_absent)

    right_absent = $(document.createElement('div'))
      .appendTo(div)

    right_absent_h = $(document.createElement('h3'))
      .addClass("small")
      .html("Links which are on #{target_a} but not on #{source_a} ")
      .appendTo(right_absent)

    ra = _.difference(_(target_links).keys(), _(source_links).values())

    list(ra, target)
      .appendTo(right_absent)

    left_untranslated = $(document.createElement('div'))
      .appendTo(div)

    left_untranslated_h = $(document.createElement('h3'))
      .addClass("small")
      .html("Links from #{source_a} which have no translation on #{target}.wikipedia.org")
      .appendTo(left_untranslated)

    list(source_untranslated, source)
      .appendTo(left_untranslated)

    right_untranslated = $(document.createElement('div'))
      .appendTo(div)

    right_untranslated_h = $(document.createElement('h3'))
      .addClass("small")
      .html("Links from #{target_a} which have no translation on #{source}.wikipedia.org")
      .appendTo(right_untranslated)

    list(target_untranslated, source)
      .appendTo(right_untranslated)

    $("#list-links").html(div)

draw_convergence_menu = (stats, source, target)->
  div = d3.select(document.createElement("div"))

  lu = stats["left_untranslated"]
  la = stats["left_absent"]

  ru = stats["right_untranslated"]
  ra = stats["right_absent"]

  i = stats["intersection"]

  max = stats["left_untranslated"] + stats["right_untranslated"] + stats["left_absent"] + stats["right_absent"]  + stats["intersection"]
  scale = d3.scale.linear().domain([0, max]).range([10, 500])

  left_untranslated = $(document.createElement("div"))
    .html("#{lu} #{source} links have no translation")
    .css("background", "rgba(255,0,0,0.25)")
    .height(scale(lu))
    .appendTo(div)

  left_absent = $(document.createElement("div"))
    .html("#{la} links of #{source} are absent from #{target}")
    .css("background", "rgba(255,0,0,0.4)")
    .height(scale(la))
    .appendTo(div)

  intersection = $(document.createElement("div"))
    .html("#{i} common links")
    .css("background", "rgba(255,0,0,0.7)")
    .height(scale(i))
    .appendTo(div)

  right_absent = $(document.createElement("div"))
    .html("#{ra} links of #{target} are absent from #{source}")
    .css("background", "rgba(255,0,0,0.4)")
    .height(scale(ra))
    .appendTo(div)

  right_untranslated = $(document.createElement("div"))
    .html("#{ru} #{target} links have no translation")
    .css("background", "rgba(255,0,0,0.25)")
    .height(scale(ru))
    .appendTo(div)

  return div

draw_convergence_mini_bar = (stats)->
  svg = d3.select(document.createElement("div")).append("svg")
    # .attr("width", 300).attr("height", 20)

  # max = stats["left"] + stats["right"]  - stats["intersection"]
  max = stats["left_untranslated"] + stats["right_untranslated"] + stats["left_absent"] + stats["right_absent"]  + stats["intersection"]
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

draw_convergence = (stats)->
  svg = d3.select(document.createElement("div"))
    .append("svg")
    .attr("width", 400)
    .attr("height", 200)

  max = d3.max(_(stats).values())
  scale = d3.scale.linear().domain([0, max]).range([10, 100])

  ri = scale(stats["intersection"])

  rua = scale(stats["left_untranslated"])
  rub = scale(stats["right_untranslated"])

  r1 = scale(stats["left_absent"]) + ri
  r2 = scale(stats["right_absent"]) + ri
  ra = scale(stats["left"])
  rb = scale(stats["right"])

  # ri = 50
  # r1 = 50
  # r2 = 50

  offset = 400 * 0.5 - (r1 + r2 - ri)
  # svg.append("circle")
  #   .attr("r", r1 + r2 - ri)
  #   .attr("cx", 200)
  #   .attr("cy", 100)
  #   .attr("stroke", "red")
  #   .attr("fill", "none")
  #   .attr("opacity", 0.4)

  x = offset + r1
  svg.append("circle")
    .attr("r", r1)
    .attr("cx", x)
    .attr("cy", 100)
    .attr("stroke", "none")
    .attr("fill", "red")
    .attr("opacity", 0.4)

  svg.append("circle")
    .attr("r", rua)
    .attr("cx", x - r1 + rua)
    .attr("cy", 100)
    .attr("stroke", "none")
    .attr("fill", "white")
    .attr("opacity", 0.4)

  x += r1 + r2 - 2*ri
  svg.append("circle")
    .attr("r", r2)
    .attr("cx", x)
    .attr("cy", 100)
    .attr("stroke", "none")
    .attr("fill", "red")
    .attr("opacity", 0.4)

  svg.append("circle")
    .attr("r", rub)
    .attr("cx", x + r2 - rub)
    .attr("cy", 100)
    .attr("stroke", "none")
    .attr("fill", "white")
    .attr("opacity", 0.4)

  return svg

$(document).ready ()->
  $.get("/api/list",load_pages)
  load_convergences("en", "Love")
  # load_links("en", "Love", "fr")
