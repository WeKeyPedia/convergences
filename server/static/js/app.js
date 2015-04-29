var compute_convergence, draw_convergence, draw_convergence_menu, draw_convergence_mini_bar, draw_convergences_chart, load_convergences, load_links, load_pages, routes;

load_pages = function(data) {
  var h2, span;
  h2 = $("<h2>Pages</h2>").appendTo($("#list-pages"));
  span = $(document.createElement('span')).addClass("small pull-right").html("about").appendTo(h2).on("click", function() {
    return $("#about").slideToggle("slow");
  });
  return _(data).each(function(pages, lang) {
    var header, ul;
    ul = $(document.createElement('ul')).addClass("pages");
    header = $(document.createElement('h4')).addClass("lang").html(lang);
    ul.append(header);
    _(pages).each(function(page) {
      var li;
      li = $(document.createElement('li')).addClass("page");
      li.html(page);
      li.on("click", function() {
        load_convergences(lang, page);
        return $("#about").slideUp("slow");
      });
      return ul.append(li);
    });
    return $("#list-pages").append(ul);
  });
};

compute_convergence = function(stats) {
  return stats["intersection"] / ((stats["left"] + stats["right"]) * 0.5);
};

load_convergences = function(lang, page, trigger_links) {
  if (trigger_links == null) {
    trigger_links = true;
  }
  history.pushState({
    id: "/page/" + lang + "/" + page
  }, '', "/page/" + lang + "/" + page);
  return $.get("/api/" + lang + "/" + page, function(data) {
    var div, h2, legend, sorted, source_lang, source_page;
    div = $(document.createElement('div'));
    _(data["stats"]).each(function(value, key) {
      if (value === null) {
        return delete data["stats"][key];
      }
    });
    sorted = _(_.pairs(data["stats"])).sortBy(function(a) {
      return -compute_convergence(a[1]);
    });
    if (trigger_links) {
      load_links(lang, page, sorted[0][0]);
    }
    source_lang = lang;
    source_page = page;
    h2 = $(document.createElement('h2')).addClass("title").html("Convergences of translations of <a href=\"http://" + source_lang + ".wikipedia.org/wiki/" + source_page + "\" class=\"page\">" + source_page + "<span class=\"lang\">" + source_lang + "</span></a>").appendTo(div);
    legend = "<div class=\"legend\">\n<p><svg width=\"20\" height=\"20\"><rect  width=\"20\" height=\"20\" fill=\"#cf75ff\" opacity=\"0.3\"></rect></svg> links in language A that have no translation in language B</p>\n<p><svg width=\"20\" height=\"20\"><rect  width=\"20\" height=\"20\" fill=\"#cf75ff\" opacity=\"0.6\"></rect></svg> links of page in language A but absent from language B</p>\n<p><svg width=\"20\" height=\"20\"><rect  width=\"20\" height=\"20\" fill=\"#32ace9\" opacity=\"0.9\"></rect></svg> common links between language A and language B</p>\n<p><svg width=\"20\" height=\"20\"><rect  width=\"20\" height=\"20\" fill=\"#09c784\" opacity=\"0.6\"></rect></svg> links of page in language B but absent from language A</p>\n<p><svg width=\"20\" height=\"20\"><rect  width=\"20\" height=\"20\" fill=\"#09c784\" opacity=\"0.3\"></rect></svg> links in language B that have no translation in language A</p>\n</div>";
    $(legend).appendTo(div);
    _(sorted).each(function(array) {
      var c_stat, convergence, h, lg, panel, svg;
      lang = array[0];
      page = data["langs"][lang];
      panel = $(document.createElement('div')).addClass("page").data("target_lang", lang).on("click", function() {
        return load_links(source_lang, source_page, $(this).data("target_lang"));
      });
      h = $(document.createElement('div')).addClass("title page").append($(document.createElement('span')).html(page)).appendTo(panel);
      lg = $(document.createElement('span')).addClass("lang").html(lang).appendTo(h);
      convergence = compute_convergence(data["stats"][lang]);
      c_stat = $(document.createElement('div')).addClass("convergence indicator").html(("A=" + lang + " B=" + source_lang + " convergence=") + convergence.toFixed(3)).appendTo(panel);
      svg = $(document.createElement('div')).addClass("convergence-viz").append(draw_convergence_mini_bar(data["stats"][lang])[0]).appendTo(panel);
      return div.append(panel);
    });
    return $("#list-lang").html(div);
  });
};

load_links = function(source, page, target) {
  history.pushState({
    id: "/page/" + source + "/" + page + "/" + target
  }, '', "/page/" + source + "/" + page + "/" + target);
  return $.get("/api/" + source + "/" + page + "/" + target, function(data) {
    var div, h2, i, intersection, intersection_h, la, left_absent, left_absent_h, left_untranslated, left_untranslated_h, list, ra, right_absent, right_absent_h, right_untranslated, right_untranslated_h, source_a, source_href, source_links, source_untranslated, target_a, target_href, target_links, target_page, target_untranslated;
    div = $(document.createElement('div'));
    target_page = data["pages"][target];
    source_href = "http://" + source + ".wikipedia.org/wiki/" + page;
    target_href = "http://" + target + ".wikipedia.org/wiki/" + target_page;
    source_a = "<a href=" + source_href + " class=\"page\">" + page + "<span class=\"lang\">" + source + "</span></a>";
    target_a = "<a href=" + target_href + " class=\"page\">" + target_page + "<span class=\"lang\">" + target + "</span></a>";
    source_links = data["translations"][source];
    target_links = data["translations"][target];
    source_untranslated = data["untranslated"][source];
    target_untranslated = data["untranslated"][target];
    h2 = $(document.createElement('h2')).addClass("title").html("Links of " + source_a + " and " + target_a).appendTo(div);
    list = function(items, direction) {
      var d;
      d = $(document.createElement('div')).addClass("list");
      _(items).each(function(i) {
        var a;
        return a = $(document.createElement('a')).attr("href", "http://" + direction + ".wikipedia.org/wiki/" + i).html(i).appendTo(d);
      });
      return d;
    };
    i = _.intersection(_(source_links).keys(), _(target_links).values());
    intersection = $(document.createElement('div')).addClass("intersection").appendTo(div);
    intersection_h = $(document.createElement('h3')).addClass("small").html(i.length + " common links between " + source_a + " and " + target_a).appendTo(intersection);
    list(i, source).appendTo(intersection);
    la = _.difference(_(source_links).keys(), _(target_links).values());
    left_absent = $(document.createElement('div')).addClass("left_absent").appendTo(div);
    left_absent_h = $(document.createElement('h3')).addClass("small").html(la.length + " links which are on " + source_a + " but not on " + target_a + " ").appendTo(left_absent);
    list(la, source).appendTo(left_absent);
    ra = _.difference(_(target_links).keys(), _(source_links).values());
    right_absent = $(document.createElement('div')).addClass("right_absent").appendTo(div);
    right_absent_h = $(document.createElement('h3')).addClass("small").html(ra.length + " links which are on " + target_a + " but not on " + source_a + " ").appendTo(right_absent);
    list(ra, target).appendTo(right_absent);
    left_untranslated = $(document.createElement('div')).addClass("left_untranslated").appendTo(div);
    left_untranslated_h = $(document.createElement('h3')).addClass("small").html(source_untranslated.length + " links from " + source_a + " which have no translation on " + target + ".wikipedia.org").appendTo(left_untranslated);
    list(source_untranslated, source).appendTo(left_untranslated);
    right_untranslated = $(document.createElement('div')).addClass("right_untranslated").appendTo(div);
    right_untranslated_h = $(document.createElement('h3')).addClass("small").html(target_untranslated.length + " links from " + target_a + " which have no translation on " + source + ".wikipedia.org").appendTo(right_untranslated);
    list(target_untranslated, target).appendTo(right_untranslated);
    return $("#list-links").html(div);
  });
};

draw_convergences_chart = function(langs) {
  var data, h, l_convergence, scale_x, scale_y, svg, w;
  w = 500;
  h = 100;
  scale_x = d3.scale.linear().domain([0, langs.length]).range([0, w]);
  scale_y = d3.scale.linear().domain([0, 1]).range([h - 1, 0]);
  svg = d3.select(document.createElement("div")).append("svg").attr("width", w).attr("height", h);
  svg.append("line").attr("x1", 0).attr("y1", h / 2).attr("x2", w).attr("y2", h / 2).attr("stroke", "#e4e4e4").attr("stroke-width", "1").attr("stroke-dasharray", "5,5");
  data = _(langs).map(function(l, i) {
    return {
      x: scale_x(i),
      y: scale_y(compute_convergence(l[1]))
    };
  });
  l_convergence = d3.svg.line().x(function(d) {
    return d.x;
  }).y(function(d) {
    return d.y;
  }).interpolate("linear");
  svg.append("path").attr("d", l_convergence(data)).attr("stroke", "#a5a2a2").attr("stroke-width", "1").attr("fill", "none");
  return svg;
};

draw_convergence_menu = function(stats, source, target) {
  var div, i, intersection, la, left_absent, left_untranslated, lu, max, ra, right_absent, right_untranslated, ru, scale;
  div = d3.select(document.createElement("div"));
  lu = stats["left_untranslated"];
  la = stats["left_absent"];
  ru = stats["right_untranslated"];
  ra = stats["right_absent"];
  i = stats["intersection"];
  max = stats["left_untranslated"] + stats["right_untranslated"] + stats["left_absent"] + stats["right_absent"] + stats["intersection"];
  scale = d3.scale.linear().domain([0, max]).range([30, 500]);
  left_untranslated = $(document.createElement("div")).html(lu + " links from " + source + " have no translation").css("background", "rgba(255,0,0,0.25)").height(scale(lu)).appendTo(div);
  left_absent = $(document.createElement("div")).html(la + " links of " + source + " are absent from " + target).css("background", "rgba(255,0,0,0.4)").height(scale(la)).appendTo(div);
  intersection = $(document.createElement("div")).html(i + " common links between " + source + " and " + target).css("background", "rgba(255,0,0,0.7)").height(scale(i)).appendTo(div);
  right_absent = $(document.createElement("div")).html(ra + " links of " + target + " are absent from " + source).css("background", "rgba(255,0,0,0.4)").height(scale(ra)).appendTo(div);
  right_untranslated = $(document.createElement("div")).html(ru + " links from " + target + " have no translation").css("background", "rgba(255,0,0,0.25)").height(scale(ru)).appendTo(div);
  return div;
};

draw_convergence_mini_bar = function(stats) {
  var max, r1, r2, ri, rua, rub, scale, svg, w, x;
  w = 500;
  svg = d3.select(document.createElement("div")).append("svg").attr("width", w);
  max = stats["left_untranslated"] + stats["right_untranslated"] + stats["left_absent"] + stats["right_absent"] + stats["intersection"];
  scale = d3.scale.linear().domain([0, max]).range([0, w]);
  ri = parseInt(scale(stats["intersection"]));
  r2 = parseInt(scale(stats["left_absent"]));
  r1 = parseInt(scale(stats["right_absent"]));
  rub = parseInt(scale(stats["left_untranslated"]));
  rua = parseInt(scale(stats["right_untranslated"]));
  x = 0;
  svg.append("rect").attr("width", rua).attr("height", 20).attr("x", 0).attr("y", 0).attr("stroke", "none").attr("fill", "#cf75ff").attr("opacity", 0.35);
  if (rua > 14) {
    svg.append("text").attr("x", x + rua * 0.5).attr("y", 10).attr("text-anchor", "middle").attr("dy", ".35em").text(stats["right_untranslated"]);
  }
  x += rua;
  svg.append("rect").attr("width", r1).attr("height", 20).attr("x", x).attr("y", 0).attr("stroke", "none").attr("fill", "#cf75ff").attr("opacity", 0.6);
  if (r1 > 14) {
    svg.append("text").attr("x", x + r1 * 0.5).attr("y", 10).attr("text-anchor", "middle").attr("dy", ".35em").text(stats["right_absent"]);
  }
  x += r1;
  svg.append("rect").attr("width", ri).attr("height", 20).attr("x", x).attr("y", 0).attr("stroke", "none").attr("fill", "#32ace9").attr("opacity", 0.9);
  if (ri > 14) {
    svg.append("text").attr("x", x + ri * 0.5).attr("y", 10).attr("text-anchor", "middle").attr("dy", ".35em").text(stats["intersection"]);
  }
  x += ri;
  svg.append("rect").attr("width", r2).attr("height", 20).attr("x", x).attr("y", 0).attr("stroke", "none").attr("fill", "#09c784").attr("opacity", 0.6);
  if (r2 > 14) {
    svg.append("text").attr("x", x + r2 * 0.5).attr("y", 10).attr("text-anchor", "middle").attr("dy", ".35em").text(stats["left_absent"]);
  }
  x += r2;
  svg.append("rect").attr("width", rub).attr("height", 20).attr("x", x).attr("y", 0).attr("stroke", "none").attr("fill", "#09c784").attr("opacity", 0.35);
  if (rub > 14) {
    svg.append("text").attr("x", x + rub * 0.5).attr("y", 10).attr("text-anchor", "middle").attr("dy", ".35em").text(stats["left_untranslated"]);
  }
  return svg;
};

draw_convergence = function(stats) {
  var max, offset, r1, r2, ra, rb, ri, rua, rub, scale, svg, x;
  svg = d3.select(document.createElement("div")).append("svg").attr("width", 400).attr("height", 200);
  max = d3.max(_(stats).values());
  scale = d3.scale.linear().domain([0, max]).range([10, 100]);
  ri = scale(stats["intersection"]);
  rua = scale(stats["left_untranslated"]);
  rub = scale(stats["right_untranslated"]);
  r1 = scale(stats["left_absent"]) + ri;
  r2 = scale(stats["right_absent"]) + ri;
  ra = scale(stats["left"]);
  rb = scale(stats["right"]);
  offset = 400 * 0.5 - (r1 + r2 - ri);
  x = offset + r1;
  svg.append("circle").attr("r", r1).attr("cx", x).attr("cy", 100).attr("stroke", "none").attr("fill", "red").attr("opacity", 0.4);
  svg.append("circle").attr("r", rua).attr("cx", x - r1 + rua).attr("cy", 100).attr("stroke", "none").attr("fill", "white").attr("opacity", 0.4);
  x += r1 + r2 - 2 * ri;
  svg.append("circle").attr("r", r2).attr("cx", x).attr("cy", 100).attr("stroke", "none").attr("fill", "red").attr("opacity", 0.4);
  svg.append("circle").attr("r", rub).attr("cx", x + r2 - rub).attr("cy", 100).attr("stroke", "none").attr("fill", "white").attr("opacity", 0.4);
  return svg;
};

$(document).ready(function() {
  var router;
  $.get("/api/list", load_pages);
  $("#about").detach().insertAfter($("#list-pages"));
  $("#about").hide();
  $("#about h2 span").on("click", function() {
    return $("#about").slideToggle("slow");
  });
  router = Router(routes).configure({
    html5history: true
  });
  return router.init();
});

routes = {
  "/page/:source/:page": function(source, page) {
    return load_convergences(source, decodeURIComponent(page));
  },
  "/page/:source/:page/:target": function(source, page, target) {
    load_convergences(source, decodeURIComponent(page), false);
    return load_links(source, decodeURIComponent(page), target);
  },
  "/about": function() {
    return $("#about").show();
  },
  "/": function() {
    return window.location = "/about";
  }
};
