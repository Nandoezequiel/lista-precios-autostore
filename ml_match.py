"""Cruza cada versión del Excel con los avisos 0km de Mercado Libre Uruguay (ml_cache.json)."""
import re, json, os, unicodedata, statistics
AQUI = os.path.dirname(os.path.abspath(__file__))
GENERIC = set("cvt mt at dct edc tm ph2 mx bra new nuevo nueva de con y el la gt full std 4x2 4x4 awd rwd 2wd 4wd 0km 0 km kwh hp".split())
MARCA_ML = {"Mitsubishi": "mitsubishi", "GWM": "gwm", "Changan": "changan", "Deepal": "deepal", "Omoda": "omoda", "Jaecoo": "jaecoo",
            "Leapmotor": "leapmotor", "Zeekr": "zeekr", "Xpeng": "xpeng", "Farizon": "farizon", "Nissan": "nissan", "JMC": "jmc", "Iveco": "iveco"}

def toks(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"\([^)]*\)", " ", s)
    return [t for t in re.findall(r"[a-z0-9\+]+", s) if not re.fullmatch(r"20\d\d", t)]

def cargar():
    p = os.path.join(AQUI, "ml_cache.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None

def verificar(f, cache):
    """Devuelve dict(estado, texto, n, min, max, mediana, links) para una versión."""
    av = cache["marcas"].get(MARCA_ML[f["marca"]], [])
    key = [t for t in toks(f["modelo"]) if t not in GENERIC]
    ver = [t for t in toks(f["marca"] + " " + f["modelo"] + " " + f["version"]) if t not in GENERIC]
    precios_ref = {p for p in (f["pvp"], f["final"], f.get("leasing")) if p}
    def inter(a):
        tt = set(toks(a["titulo"]))
        return len(set(ver) & tt) / max(1, len(set(ver))), (not key) or key[0] in tt   # el nombre del modelo debe estar (no basta "plus"/"phev")
    cand = []
    for a in av:
        sc, kok = inter(a)
        if kok and sc >= 0.5: cand.append((sc, a))
    if not cand:
        return dict(estado="sin", texto="Sin avisos 0km en Mercado Libre Uruguay para esta versión.", n=0)
    mejor = max(s for s, _ in cand)
    grp = [a for s, a in cand if s >= mejor - 0.15]
    precios = sorted(a["precio"] for a in grp)
    # coincide si algún aviso del grupo (o de cualquier aviso con la misma clave) tiene el mismo precio
    cerca = lambda p: any(abs(p - r) <= 60 for r in precios_ref)   # ML suele publicar 24.980 por 24.990
    hit = [a for a in grp if cerca(a["precio"])] or [a for s, a in cand if cerca(a["precio"]) and s >= 0.5]
    base = dict(n=len(grp), min=precios[0], max=precios[-1], mediana=int(statistics.median(precios)),
                links=[dict(t=a["titulo"], p=a["precio"], v=a["vendedor"], l=a["link"]) for a in sorted(grp, key=lambda a: a["precio"])[:5]])
    if hit:
        h = hit[0]
        base.update(estado="ok", texto=f"{len(grp)} aviso(s) 0km en Mercado Libre; uno publica USD {h['precio']:,} ({h['vendedor'] or 'vendedor'}).".replace(",", "."))
    else:
        rng = f"USD {precios[0]:,}".replace(",", ".") + (f" a {precios[-1]:,}".replace(",", ".") if precios[-1] != precios[0] else "")
        base.update(estado="dif", texto=f"Mercado Libre muestra {len(grp)} aviso(s) a {rng}; ninguno coincide con el Excel.")
    return base
