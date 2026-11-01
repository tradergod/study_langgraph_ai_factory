#!/usr/bin/env python3
"""output/research_data.json 을 읽어 output/travel_site.html 한 파일을 만든다.

화면에 쓰는 글은 전부 research_data.json 에서 가져온다. 새로 지어내지 않는다.
CSS · JavaScript 는 HTML 안에 넣는다 (바깥 파일 없음).
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "output" / "research_data.json"
OUT = ROOT / "output" / "travel_site.html"

# 기능1 아코디언 헤더 5개와 채우는 정보 슬롯 (STEP 2 고정)
HEADERS = [
    ("매력", ["매력"]),
    ("역사", ["역사"]),
    ("문화", ["문화", "주의사항"]),
    ("국가상태", ["국가상태"]),
    ("여행정보", ["항공권가격", "환율", "교통개요"]),
]
SLOT_TITLE = {
    "매력": "매력", "역사": "역사", "문화": "문화", "주의사항": "조심할 점",
    "국가상태": "지금 알려진 국가 상태", "항공권가격": "항공권 가격",
    "환율": "환율", "교통개요": "교통 개요",
}


def esc(text):
    return html.escape(text or "", quote=False)


def attr(text):
    return html.escape(text or "", quote=True)


def href(url):
    # 출처 주소는 모은 그대로 화면에 남긴다 (& 를 바꾸면 원문과 어긋난다)
    return (url or "").replace('"', "%22")


def source_link(item):
    name = esc(item.get("source_name") or "출처")
    return '<a data-source href="%s" target="_blank" rel="noopener">%s</a>' % (
        href(item.get("source_url")), name)


def evidence_list(items):
    rows = []
    for item in items or []:
        rows.append("<li>%s <span class=\"src\">— %s</span></li>" % (
            esc(item.get("text")), source_link(item)))
    return "<ul class=\"ev\">%s</ul>" % "".join(rows)


def img_tag(url, alt, extra):
    return '<img %s src="%s" alt="%s" loading="lazy">' % (extra, attr(url), attr(alt))


def feature1(intro):
    flag = intro["국기이미지"]["asset"]
    hero = intro["대표이미지"]["asset"]
    out = ['<section id="feature1"><h2>프랑스 한눈에 보기</h2>']
    out.append('<div class="hero-row">%s%s</div>' % (
        img_tag(flag["url"], flag["alt"], 'class="flag" data-role="flag"'),
        img_tag(hero["url"], hero["alt"], 'class="hero" data-role="hero"')))
    out.append('<div class="acc">')
    for key, slots in HEADERS:
        parts = []
        for slot in slots:
            node = intro.get(slot) or {}
            items = node.get("items") or []
            parts.append("<h4>%s</h4>" % esc(SLOT_TITLE[slot]))
            if items:
                parts.append(evidence_list(items))
            else:
                parts.append("<p>확인했으나 특별한 내용 없음</p>")
        out.append(
            '<button type="button" class="acc-header" data-acc="feature1" data-key="%s" '
            'aria-expanded="false">%s</button>' % (attr(key), esc(key)))
        out.append('<div class="acc-panel" data-acc="feature1" data-key="%s">%s</div>' % (
            attr(key), "".join(parts)))
    out.append("</div></section>")
    return "".join(out)


def city_panel(city):
    name = city["name"]
    out = ['<div class="city-panel" data-city-panel="%s">' % attr(name)]
    out.append("<h3>%s</h3>" % esc(name))
    out.append('<p class="why"><strong>왜 이 도시인가</strong> %s</p>' % esc(city.get("why_selected")))
    out.append("<h4>관광지 3곳</h4>")
    for spot in city["spots"]:
        sname = spot["name"]
        image = spot["image"]
        out.append('<article class="spot">')
        out.append(img_tag(image["url"], image["alt"], 'class="spot-img" data-spot-image="%s"' % attr(sname)))
        out.append('<button type="button" class="spot-btn" data-spot="%s" aria-expanded="false">%s</button>' % (
            attr(sname), esc(sname)))
        out.append('<div class="spot-detail" data-spot-detail="%s"><p>%s</p><h5>근거</h5>%s</div>' % (
            attr(sname), esc(spot.get("detail")), evidence_list(spot.get("items"))))
        out.append("</article>")
    out.append("<h4>취향 설명 — 넣은 이유와 뺀 이유</h4>")
    lines = [ln.strip() for ln in (city.get("preference_note") or "").splitlines() if ln.strip()]
    out.append('<div class="pref" data-preference-note="%s">%s</div>' % (
        attr(name), "".join("<p>%s</p>" % esc(ln) for ln in lines)))
    out.append('<button type="button" class="back" data-back>← 도시 목록으로 돌아가기</button>')
    out.append("</div>")
    return "".join(out)


def feature2(cities):
    out = ['<section id="feature2"><h2>도시와 관광지 고르기</h2>']
    out.append('<p class="lead">도시를 누르면 오른쪽에서 관광지 목록이 열립니다.</p>')
    out.append('<div class="city-buttons">')
    for city in cities:
        out.append('<button type="button" class="city-btn" data-city="%s">%s</button>' % (
            attr(city["name"]), esc(city["name"])))
    out.append("</div>")
    out.append('<aside id="city-drawer" hidden aria-label="도시 상세">')
    out.append("".join(city_panel(c) for c in cities))
    out.append("</aside></section>")
    return "".join(out)


KIND_CLASS = {"명소": "k-spot", "식사": "k-meal", "이동": "k-move", "휴식": "k-rest"}


def block_li(block):
    start = block["start"]
    end = block["end"]
    kind = block.get("kind", "")
    where = block.get("spot") or block.get("place") or ""
    return (
        '<li data-block="%s-%s"><span class="t">%s–%s</span> '
        '<span class="kind %s">%s</span> <strong>%s</strong><p>%s</p></li>' % (
            start, end, start, end, KIND_CLASS.get(kind, ""), esc(kind),
            esc(where), esc(block.get("why"))))


def feature3(cities):
    out = ['<section id="feature3"><h2>도시별 4일 일정</h2>']
    out.append('<p class="lead">네 도시를 나란히 놓고 비교해 한 곳을 고르세요. 도시마다 4일치 일정이 따로 있습니다.</p>')
    out.append('<div class="acc">')
    for city in cities:
        name = city["name"]
        plan = city["itinerary"]
        body = ['<h4>일정 근거</h4>', evidence_list(plan.get("items"))]
        for day in plan["days"]:
            body.append('<div class="day" data-day="%s"><h4>%s일차</h4><ul class="blocks">%s</ul></div>' % (
                day["day"], day["day"], "".join(block_li(b) for b in day["blocks"])))
        out.append(
            '<button type="button" class="acc-header" data-acc="feature3" data-key="%s" '
            'aria-expanded="false">%s 4일 일정</button>' % (attr(name), esc(name)))
        out.append('<div class="acc-panel" data-acc="feature3" data-key="%s">%s</div>' % (
            attr(name), "".join(body)))
    out.append("</div></section>")
    return "".join(out)


CSS = """
:root{--bg:#0f1720;--panel:#16212d;--panel2:#1c2a38;--text:#e6edf3;--muted:#9fb0c0;
--accent:#14B8A6;--accent2:#0d8f81;--line:#2a3a4a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font-family:system-ui,-apple-system,"Segoe UI","Malgun Gothic","Apple SD Gothic Neo",sans-serif;line-height:1.7}
header.top{padding:32px 20px 8px;max-width:960px;margin:0 auto}
header.top h1{margin:0 0 6px;font-size:1.8rem}
header.top p{margin:4px 0;color:var(--muted)}
main{max-width:960px;margin:0 auto;padding:0 20px 80px}
section{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px;margin:22px 0}
h2{margin:0 0 12px;color:var(--accent);font-size:1.35rem}
h3{margin:4px 0 10px;font-size:1.3rem}
h4{margin:18px 0 6px;color:var(--accent)}
h5{margin:14px 0 4px;color:var(--muted)}
.lead{color:var(--muted);margin-top:0}
.hero-row{display:flex;gap:14px;align-items:flex-start;justify-content:space-between;margin-bottom:14px}
img.flag{width:120px;height:80px;object-fit:cover;border-radius:8px;border:1px solid var(--line)}
img.hero{width:min(60%,520px);height:220px;object-fit:cover;border-radius:12px;border:1px solid var(--line)}
.img-fallback{display:flex;align-items:center;justify-content:center;background:var(--panel2);
color:var(--muted);border:1px dashed var(--line);border-radius:10px;padding:10px;text-align:center;font-size:.9rem}
.acc-header{display:block;width:100%;text-align:left;background:var(--panel2);color:var(--text);
border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:8px 0 0;font-size:1rem;cursor:pointer}
.acc-header:hover,.city-btn:hover,.spot-btn:hover,.back:hover{border-color:var(--accent)}
.acc-header[aria-expanded="true"]{border-color:var(--accent);color:var(--accent)}
.acc-panel{display:none;padding:6px 14px 14px;border-left:3px solid var(--accent);margin:0 0 4px 6px}
.acc-panel.open{display:block}
ul.ev{padding-left:20px;margin:6px 0}
ul.ev li{margin:6px 0}
.src{color:var(--muted);font-size:.9rem}
a{color:var(--accent)}
.city-buttons{display:flex;flex-wrap:wrap;gap:10px}
.city-btn{background:var(--accent2);color:#fff;border:1px solid var(--accent);border-radius:10px;
padding:12px 20px;font-size:1.05rem;cursor:pointer}
#city-drawer{position:fixed;top:0;right:0;height:100vh;width:min(560px,100vw);overflow-y:auto;
background:var(--panel);border-left:2px solid var(--accent);padding:20px;z-index:20;
box-shadow:-10px 0 30px rgba(0,0,0,.5)}
#city-drawer[hidden]{display:none}
.city-panel{display:none}
.city-panel.active{display:block}
.spot{border:1px solid var(--line);border-radius:12px;padding:10px;margin:10px 0;background:var(--panel2)}
img.spot-img{width:100%;height:190px;object-fit:cover;border-radius:8px}
.spot-btn{display:block;width:100%;text-align:left;margin-top:8px;background:transparent;color:var(--text);
border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-size:1rem;cursor:pointer}
.spot-btn[aria-expanded="true"]{border-color:var(--accent);color:var(--accent)}
.spot-detail{display:none;padding-top:8px}
.spot-detail.open{display:block}
.pref p{margin:6px 0;padding-left:10px;border-left:2px solid var(--line)}
.back{margin-top:16px;background:transparent;color:var(--accent);border:1px solid var(--accent);
border-radius:8px;padding:10px 14px;cursor:pointer}
.day{margin:14px 0;padding:10px;border:1px solid var(--line);border-radius:10px;background:var(--panel2)}
ul.blocks{list-style:none;padding:0;margin:0}
ul.blocks li{margin:8px 0;padding:8px 10px;border-left:3px solid var(--line)}
ul.blocks li p{margin:4px 0 0;color:var(--muted);font-size:.95rem}
.t{font-variant-numeric:tabular-nums;color:var(--accent)}
.kind{font-size:.75rem;padding:1px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}
.k-spot{border-color:var(--accent);color:var(--accent)}
footer{max-width:960px;margin:0 auto;padding:0 20px 40px;color:var(--muted);font-size:.9rem}
@media (max-width:640px){.hero-row{flex-direction:column}img.hero{width:100%}}
"""

JS = """
(function () {
  var drawer = document.getElementById('city-drawer');

  function closeSpots() {
    var opened = drawer.querySelectorAll('[data-spot-detail].open');
    for (var i = 0; i < opened.length; i++) { opened[i].classList.remove('open'); }
    var btns = drawer.querySelectorAll('button[data-spot]');
    for (var j = 0; j < btns.length; j++) { btns[j].setAttribute('aria-expanded', 'false'); }
  }

  function openCity(name) {
    var panels = drawer.querySelectorAll('[data-city-panel]');
    for (var i = 0; i < panels.length; i++) { panels[i].classList.remove('active'); }
    var target = drawer.querySelector('[data-city-panel="' + name + '"]');
    if (target) { target.classList.add('active'); }
    closeSpots();
    drawer.hidden = false;
    drawer.scrollTop = 0;
  }

  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.closest) { return; }

    var head = t.closest('.acc-header');
    if (head) {
      var area = head.getAttribute('data-acc');
      var key = head.getAttribute('data-key');
      var panel = document.querySelector('.acc-panel[data-acc="' + area + '"][data-key="' + key + '"]');
      if (panel) {
        var isOpen = panel.classList.toggle('open');
        head.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      }
      return;
    }

    var cityBtn = t.closest('button[data-city]');
    if (cityBtn) { openCity(cityBtn.getAttribute('data-city')); return; }

    var spotBtn = t.closest('button[data-spot]');
    if (spotBtn) {
      var sname = spotBtn.getAttribute('data-spot');
      var detail = drawer.querySelector('[data-spot-detail="' + sname + '"]');
      if (detail) {
        var shown = detail.classList.toggle('open');
        spotBtn.setAttribute('aria-expanded', shown ? 'true' : 'false');
      }
      return;
    }

    if (t.closest('[data-back]')) {
      closeSpots();
      drawer.hidden = true;
      var list = document.querySelector('#feature2 .city-buttons');
      if (list) { list.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !drawer.hidden) { closeSpots(); drawer.hidden = true; }
  });

  // 사진 주소가 열리지 않으면 대체 박스를 보여 준다
  document.addEventListener('error', function (e) {
    var im = e.target;
    if (!im || im.tagName !== 'IMG' || im.getAttribute('data-failed')) { return; }
    im.setAttribute('data-failed', '1');
    im.style.display = 'none';
    var box = document.createElement('div');
    box.className = 'img-fallback';
    box.style.height = im.className === 'flag' ? '80px' : '160px';
    box.textContent = '사진을 불러오지 못했습니다 · ' + (im.getAttribute('alt') || '');
    im.parentNode.insertBefore(box, im.nextSibling);
  }, true);
})();
"""


def build(data):
    req = data["request"]
    cities = data["cities"]
    style = req["style"]
    top = (
        '<header class="top"><h1>프랑스 %s일 · 도시 고르기 여행 가이드</h1>'
        '<p>초등학생 2명과 중학생 1명이 함께하는 가족 여행. 도시 선정 기준은 1등 내 취향, 2등 유명도, 3등 교통입니다.</p>'
        '<p>좋아하는 것 — %s</p><p>피하고 싶은 것 — %s</p><p>세부 사정 — %s</p></header>' % (
            req["days"], esc(" ".join(style["preferred"])), esc(" ".join(style["not_preferred"])),
            esc(" ".join(style["detailed"]))))
    foot = (
        '<footer><p>요금, 운영 시간, 운항 시각은 자주 바뀝니다. 출발 전에 각 출처의 공식 페이지에서 다시 확인하세요. '
        '사진이 해당 명소와 맞는지는 사람이 눈으로 확인해야 합니다.</p>'
        '<p>요금은 인당 기준으로만 적었습니다. 함께 가는 보호자 인원이 정해지지 않아 가족 합계는 계산하지 않았고, 나이별 요금은 초등학생 2명과 중학생 1명의 나이에 맞춰 확인해야 합니다.</p></footer>')
    body = "<main>%s%s%s</main>" % (feature1(data["country_intro"]), feature2(cities), feature3(cities))
    return (
        '<!DOCTYPE html>\n<html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>프랑스 %s일 도시 고르기 여행 가이드</title><style>%s</style></head><body>%s%s%s"
        "<script>%s</script></body></html>\n" % (req["days"], CSS, top, body, foot, JS))


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.write_text(build(data), encoding="utf-8")
    print("wrote", OUT, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
