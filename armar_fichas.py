"""Une la lectura visual/posicional de las páginas de tablas (fichas_txt/_visual/X.txt, 1.ª línea «# paginas: 2,3») con el texto original (fichas_txt/_crudo/X.txt) de las demás páginas -> fichas_txt/X.txt"""
import os, re, sys
A = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(A, "fichas_txt", "_visual"); C = os.path.join(A, "fichas_txt", "_crudo")
for n in sorted(os.listdir(V)):
    v = open(os.path.join(V, n), encoding="utf-8").read(); m = re.match(r"# paginas: ([\d,]+)\n", v)
    leidas = set(int(x) for x in m.group(1).split(",")) if m else set(); v = v[m.end():] if m else v
    crudo = open(os.path.join(C, n), encoding="utf-8", errors="ignore").read()
    trozos = re.split(r"\n?--- p(\d+) ---\n", crudo); resto = []
    for i in range(1, len(trozos), 2):
        if int(trozos[i]) not in leidas and trozos[i + 1].strip(): resto.append(f"[texto de la página {trozos[i]}]\n" + trozos[i + 1].strip())
    out = "LECTURA VISUAL DE LAS TABLAS DE LA FICHA (versiones y equipamiento, ya asociados a cada versión):\n" + v.strip() + "\n\nOTRAS PÁGINAS DE LA FICHA (texto):\n" + "\n\n".join(resto)
    open(os.path.join(A, "fichas_txt", n), "w", encoding="utf-8").write(out); print(n, len(out))
