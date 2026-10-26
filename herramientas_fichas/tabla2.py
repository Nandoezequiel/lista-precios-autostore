"""Tablas de equipamiento ●/x por versión, agrupando las marcas por posición (no depende de las cabeceras).
uso: python -I tabla2.py "ficha.pdf" pagina "Nombre1,Nombre2,..." [mitades=2] [claves_cabecera="Elite,Deluxe"]
Las columnas se infieren agrupando la x de los ●/x; los nombres se asignan de izquierda a derecha."""
import fitz, sys, os, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
D = r"C:\Users\fercu\Downloads\TODOS LOS PROYECTOS CLAUDE\VENTA DE VIDHUB\lista-precios-autostore\fichas"
GEN = {"Cabina","Simple","Doble","4x2","4x4","2WD","4WD","HEV","PHEV","Luxury","Elite","Deluxe","Dignity","Middle","High","Skin","SR","GT","Premium","Comfort","Diésel","Gasolina"}
SI = {"●", "•", "✓", "✔", "■", "◼", "○", "★", "·", "▪", "▫", "◾"} | ({"S"} if os.environ.get("MARK_S") else set()); NO = {"x", "X", "✗", "✘", "—", "–"} | ({"-"} if os.environ.get("MARK_H") else set())
def lineas(ws, tol=3.2):
    ws = sorted(ws, key=lambda w: ((w[1] + w[3]) / 2, w[0])); out, cur, cy = [], [], None
    for w in ws:
        y = (w[1] + w[3]) / 2
        if cy is None or abs(y - cy) <= tol: cur.append(w); cy = y if cy is None else (cy * (len(cur) - 1) + y) / len(cur)
        else: out.append((cy, sorted(cur, key=lambda w: w[0]))); cur = [w]; cy = y
    if cur: out.append((cy, sorted(cur, key=lambda w: w[0])))
    return out
def clusters(xs, n):
    xs = sorted(xs)
    if not xs: return []
    # k-means 1D simple
    cs = [xs[int(i * (len(xs) - 1) / max(1, n - 1))] for i in range(n)]
    for _ in range(30):
        g = [[] for _ in cs]
        for x in xs: g[min(range(len(cs)), key=lambda j: abs(cs[j] - x))].append(x)
        cs = [sum(a) / len(a) if a else cs[i] for i, a in enumerate(g)]
    return sorted(cs)
def mitad(page, x0, x1, nombres, claves):
    n = len(nombres)
    ws = [w for w in page.get_text("words") if x0 <= (w[0] + w[2]) / 2 < x1]
    for dr in page.get_drawings():   # marcas dibujadas (círculos/cuadrados rellenos) que no son texto
        r = dr["rect"]
        if dr.get("fill") is not None and 1.0 <= r.width <= 9 and 1.0 <= r.height <= 9 and abs(r.width - r.height) < 2.5 and x0 <= (r.x0 + r.x1) / 2 < x1 and sum(dr["fill"]) < 2.2:
            ws.append((r.x0, r.y0, r.x1, r.y1, "●"))
    try:   # marcas que son imágenes diminutas (cuadraditos)
        for im in page.get_image_info():
            bx = fitz.Rect(im["bbox"])
            if 1.0 <= bx.width <= 9 and 1.0 <= bx.height <= 20 and x0 <= (bx.x0 + bx.x1) / 2 < x1: ws.append((bx.x0, bx.y0, bx.x1, bx.y1, "▪"))
    except Exception: pass
    marc = [w for w in ws if w[4] in SI | NO]
    import collections
    xs = [(w[0] + w[2]) / 2 for w in marc]
    cnt = collections.Counter(round(x / 8) for x in xs); tops = []
    hdr = [(w[0] + w[2]) / 2 for w in ws if w[4] in claves and w[4] not in SI | NO]
    if hdr:   # preferir columnas de marcas cercanas a las palabras de cabecera
        hc = clusters(hdr, n) if len(set(round(h / 10) for h in hdr)) >= n else []
        for h in hc:
            cand = [(c, b) for b, c in cnt.items() if abs(b * 8 - h) <= 32 and all(abs(b - t) > 1 for t in tops)]
            if cand: tops.append(max(cand)[1])
    if len(tops) < n:
        tops = []
        for b, _ in cnt.most_common():
            if all(abs(b - t) > 1 for t in tops): tops.append(b)
            if len(tops) == n: break
    if len(tops) < n: return ["(no se pudieron separar las columnas)"]
    cs = sorted(sum(x for x in xs if abs(round(x / 8) - t) <= 1) / max(1, sum(1 for x in xs if abs(round(x / 8) - t) <= 1)) for t in tops)
    marc = [w for w in marc if min(abs((w[0] + w[2]) / 2 - c) for c in cs) <= 16]
    ws = [w for w in ws if w[4] not in SI | NO or w in marc]
    cmin = cs[0] - 14
    ls = lineas(ws)
    # separar filas de marcas / de etiqueta
    M, L, H = [], [], []
    for y, r in ls:
        mk = [w for w in r if w[4] in SI | NO and (w[0] + w[2]) / 2 >= cmin]
        lab = " ".join(w[4] for w in r if (w[0] + w[2]) / 2 < cmin or w[4] not in SI | NO and (w[0] + w[2]) / 2 < cmin)
        # etiqueta = palabras a la izquierda de la primera columna (o todas si no hay marcas)
        izq = [w for w in r if (w[0] + w[2]) / 2 < cmin]
        if mk: M.append((y, mk, " ".join(w[4] for w in izq)))
        else:
            left = [w for w in r if (w[0] + w[2]) / 2 < cmin]; right = [w for w in r if (w[0] + w[2]) / 2 >= cmin]
            tx = " ".join(w[4] for w in r)
            esver = lambda ws: ws and all(w[4] in GEN or w[4] in claves or re.fullmatch(r"[0-9]?[xX]?[0-9]|\d[xX]\d|[24]WD", w[4]) for w in ws)
            if left and right and esver(right): H.append((y, " ".join(w[4] for w in left)))
            elif right and not left and esver(right): pass
            else: L.append([y, tx, False])
    # etiquetas partidas: sumar líneas sin marcas cercanas a cada fila de marcas
    filas = []
    for y, mk, izq in M:
        extra = [l for l in L if not l[2] and abs(l[0] - y) <= 11 and l[1] != ""]
        for l in extra: l[2] = True
        partes = sorted([(l[0], l[1]) for l in extra] + ([(y, izq)] if izq else []))
        label = " ".join(t for _, t in partes).strip()
        vals = {}
        sep = min(b - a for a, b in zip(cs, cs[1:])) if n > 1 else 80
        if len(mk) == 1 and n > 1 and min(abs(c - (mk[0][0] + mk[0][2]) / 2) for c in cs) > 0.3 * sep:
            vals = {j: "SI" if mk[0][4] in SI else "NO" for j in range(n)}
        else:
            for w in mk:
                j = min(range(n), key=lambda j: abs(cs[j] - (w[0] + w[2]) / 2)); vals[j] = "SI" if w[4] in SI else "NO"
        filas.append((y, label, vals))
    ev = [("H", y, t) for y, t in H] + [("F", y, l, v) for y, l, v in filas] + [("N", l[0], l[1]) for l in L if not l[2]]
    ev.sort(key=lambda e: e[1])
    out = []
    for e in ev:
        if e[0] == "H": out.append(f"\n## {e[2]}")
        elif e[0] == "F":
            lab, v = e[2], e[3]
            if all(v.get(j) == "SI" for j in range(n)): out.append(f"- {lab}: en todas")
            elif all(v.get(j, "NO") == "NO" for j in range(n)): out.append(f"- {lab}: no la trae ninguna")
            else: out.append(f"- {lab}: " + "; ".join(f"{nombres[j]} {'SÍ' if v.get(j) == 'SI' else 'NO'}" for j in range(n)))
        else:
            if len(e[2]) > 3: out.append(f"  ({e[2]})")
    return out
if __name__ == "__main__":
    pdf, pg = sys.argv[1], int(sys.argv[2]); nombres = [s.strip() for s in sys.argv[3].split(",")]
    mit = int(sys.argv[4]) if len(sys.argv) > 4 else 2; claves = (sys.argv[5] if len(sys.argv) > 5 else "Elite,Deluxe").split(",")
    page = fitz.open(os.path.join(D, pdf))[pg - 1]; W = page.rect.width
    for k in range(mit):
        print("\n".join(mitad(page, W * k / mit, W * (k + 1) / mit, nombres, claves)))
