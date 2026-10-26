"""Baja los avisos 0km de Mercado Libre Uruguay por marca (precio en USD) a ml_cache.json.
Uso: python -I ml_precios.py   (tarda ~1-2 min; no usa la API, lee las páginas públicas)
"""
import re, os, json, html, time, urllib.request, datetime, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
MARCAS = ["nissan", "jmc", "iveco", "gwm", "changan", "deepal", "omoda", "jaecoo", "mitsubishi", "leapmotor", "zeekr", "xpeng", "farizon", "nevo", "avatr"]
UA = {"User-Agent": "Mozilla/5.0"}

def pagina(url):
    for _ in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(2)
    return ""

def avisos(h):
    out = []
    for c in re.split(r'<li class="ui-search-layout__item', h)[1:]:
        t = re.search(r'poly-component__title[^>]*>([^<]+)', c)
        sim = re.search(r'andes-money-amount__currency-symbol">([^<]+)', c)
        fr = re.search(r'andes-money-amount__fraction[^>]*>([^<]+)', c)
        ln = re.search(r'href="(https://auto\.mercadolibre\.com\.uy/MLU-[^"#?]*)', c)
        if not (t and sim and fr and ln): continue
        if "US" not in sim.group(1): continue          # solo avisos en dólares
        im = re.search(r'(?:data-src|src)="(https://http2\.mlstatic\.com[^"]+)"', c)
        sel = re.search(r'poly-component__seller[^>]*>([^<]+)', c)
        out.append(dict(titulo=html.unescape(t.group(1)).strip(), precio=int(fr.group(1).replace(".", "")),
                        link=ln.group(1), img=im.group(1) if im else "", vendedor=html.unescape(sel.group(1)).strip() if sel else ""))
    return out

todo = {}
for m in MARCAS:
    lst = []
    for p in range(8):
        u = f"https://autos.mercadolibre.com.uy/{m}/0km/" + (f"_Desde_{48*p+1}" if p else "")
        a = avisos(pagina(u))
        if not a: break
        lst += a
        if len(a) < 20: break
    todo[m] = lst
    print(m, len(lst)); sys.stdout.flush()
json.dump(dict(fecha=datetime.date.today().isoformat(), marcas=todo), open(os.path.join(AQUI, "ml_cache.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
