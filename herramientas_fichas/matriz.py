"""Matriz versiones x características (celdas con texto). uso: python -I matriz.py ficha.pdf pagina "Lista,de,cabeceras,de,columna" """
import fitz, sys, os, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
D = r"C:\Users\fercu\Downloads\TODOS LOS PROYECTOS CLAUDE\VENTA DE VIDHUB\lista-precios-autostore\fichas"
pdf, pg = sys.argv[1], int(sys.argv[2]); ncol = int(sys.argv[3]); y_head = float(sys.argv[4])  # y de la 2.ª línea de cabecera (nivel S/SE/XE...)
page = fitz.open(os.path.join(D, pdf))[pg - 1]
ws = page.get_text("words")
head2 = sorted([w for w in ws if abs((w[1] + w[3]) / 2 - y_head) < 3 and (w[0] + w[2]) / 2 > 200], key=lambda w: w[0])
head1 = [w for w in ws if abs((w[1] + w[3]) / 2 - (y_head - 7)) < 4 and (w[0] + w[2]) / 2 > 200]
cx = [(w[0] + w[2]) / 2 for w in head2]
assert len(cx) == ncol, (len(cx), [w[4] for w in head2])
names = []
for c, w2 in zip(cx, head2):
    t1 = " ".join(w[4] for w in sorted(head1, key=lambda w: w[0]) if abs((w[0] + w[2]) / 2 - c) < 22)
    names.append(f"{t1} {w2[4]}".strip())
print("COLUMNAS (en orden de izquierda a derecha en la ficha): " + " | ".join(f"{i+1}={n}" for i, n in enumerate(names)))
lim = cx[0] - 18
rows = {}
for w in ws:
    y = round((w[1] + w[3]) / 2 / 2.6)
    rows.setdefault(y, []).append(w)
for y in sorted(rows):
    r = sorted(rows[y], key=lambda w: w[0])
    if (r[0][1] + r[0][3]) / 2 < y_head + 6: continue
    lab = " ".join(w[4] for w in r if (w[0] + w[2]) / 2 < lim)
    cells = [[] for _ in cx]
    for w in r:
        xc = (w[0] + w[2]) / 2
        if xc < lim: continue
        j = min(range(len(cx)), key=lambda j: abs(cx[j] - xc))
        if abs(cx[j] - xc) <= 20: cells[j].append(w[4])
    vals = [" ".join(c) if c else "·" for c in cells]
    if all(v == "·" for v in vals):
        if lab.strip(): print(f"\n## {lab}")
        continue
    if len(set(vals)) == 1: print(f"- {lab}: {vals[0]} (todas)")
    else: print(f"- {lab}: " + " | ".join(vals))
