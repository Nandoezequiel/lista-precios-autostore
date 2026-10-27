"""Une la investigación de fichas (investigacion/<grupo>.json + investigacion/descargas/<grupo>/) con la lista -> specs.js.

Uso:  python -I armar_specs.py
- Copia a fichas/ los PDF descargados y a fotos/galeria/ las fotos (solo si son PDF/imagen reales).
- Escribe fichas_txt/<modelo> (web).txt para los modelos sin PDF (lo lee el Asesor IA).
- specs.js: clave «marca|modelo|versión» (igual que en datos.js) -> datos técnicos, equipamiento, fotos, fuentes.
"""
import os, re, json, shutil, glob

A = os.path.dirname(os.path.abspath(__file__))
INV = os.path.join(A, "investigacion")
GAL = os.path.join(A, "fotos", "galeria")
os.makedirs(GAL, exist_ok=True)

def es_pdf(p): return open(p, "rb").read(5) == b"%PDF-"
def es_img(p):
    h = open(p, "rb").read(12)
    return os.path.getsize(p) > 15000 and (h[:3] == b"\xff\xd8\xff" or h[:8] == b"\x89PNG\r\n\x1a\n" or (h[:4] == b"RIFF" and h[8:12] == b"WEBP"))
def limpio(s): return re.sub(r'[<>:"/\\|?*]+', " ", s).strip()

filas = json.loads(open(os.path.join(A, "datos.js"), encoding="utf-8").read().split("window.DATOS = ", 1)[1].rstrip().rstrip(";"))["filas"]
specs, avisos = {}, []
RES = {}   # huecos completados por versión (investigacion/huecos_*_resueltos.json): {id: {campo: valor | null = no aplica}}
for r in glob.glob(os.path.join(INV, "huecos_*_resueltos.json")):
    for k, v in json.load(open(r, encoding="utf-8")).items(): RES.setdefault(int(k), {}).update(v)
for ruta in sorted(glob.glob(os.path.join(INV, "*.json"))):
    grupo = os.path.splitext(os.path.basename(ruta))[0]
    if grupo == "filas_por_marca" or grupo.startswith("huecos_"): continue
    desc = os.path.join(INV, "descargas", grupo)
    for m in json.load(open(ruta, encoding="utf-8")).get("modelos", []):
        fotos = []
        for n in m.get("fotos") or []:
            src = os.path.join(desc, "fotos", os.path.basename(n))
            if os.path.exists(src) and es_img(src):
                dst = f"{grupo}-{os.path.basename(n)}"
                shutil.copyfile(src, os.path.join(GAL, dst)); fotos.append("galeria/" + dst)
            else: avisos.append(f"foto inválida o faltante: {grupo}/{n}")
        pdfs = []
        for n in m.get("pdf") or []:
            src = os.path.join(desc, "pdf", os.path.basename(n))
            if os.path.exists(src) and es_pdf(src):
                shutil.copyfile(src, os.path.join(A, "fichas", os.path.basename(n))); pdfs.append(os.path.basename(n))
            elif os.path.exists(os.path.join(A, "fichas", os.path.basename(n))): pdfs.append(os.path.basename(n))   # ya estaba en fichas/
            else: avisos.append(f"pdf inválido o faltante: {grupo}/{n}")
        ids = [i for i in m.get("ids", []) if isinstance(i, int) and 0 <= i < len(filas)]
        txt = None
        if m.get("ficha_texto") and not any(filas[i].get("ficha") for i in ids):
            txt = limpio(f"{m['marca']} {m['modelo']} {min(ids) if ids else ''} (web)") + ".txt"
            fu = "\n".join(f"- {x.get('que','')}: {x.get('url','')}" for x in m.get("fuentes", []) if isinstance(x, dict))
            open(os.path.join(A, "fichas_txt", txt), "w", encoding="utf-8").write(
                f"FICHA TÉCNICA ARMADA CON FUENTES DE INTERNET ({m['marca']} {m['modelo']}; confianza {m.get('confianza','?')})\nFuentes:\n{fu}\nNotas: {m.get('notas','')}\n\n{m['ficha_texto']}")
        eq = m.get("equipamiento") or {}
        for i in ids:
            f = filas[i]
            res = dict(RES.get(i, {})); eq_res = res.pop("_eq", None) or {}
            d = {**(m.get("comun") or {}), **((m.get("versiones") or {}).get(str(i)) or {}), **res}
            e = {}
            for k in ("seguridad", "confort", "multimedia"):
                vals = (eq.get("todas") or {}).get(k, []) + (eq.get(str(i)) or {}).get(k, []) + (eq_res.get(k) or [])
                e[k] = list(dict.fromkeys(v.strip() for v in vals if isinstance(v, str) and v.strip()))
            specs[f"{f['marca']}|{f['modelo']}|{f['version']}"] = dict(
                d=d, eq=e, fotos=fotos, pdf=f.get("ficha") or (pdfs[0] if pdfs else None), txt=txt,
                fuentes=[x for x in m.get("fuentes", []) if isinstance(x, dict)][:8], conf=m.get("confianza", ""), notas=m.get("notas", ""))

open(os.path.join(A, "specs.js"), "w", encoding="utf-8").write("window.SPECS = " + json.dumps(specs, ensure_ascii=False, indent=0) + ";\n")
sin = [f"{f['id']} {f['marca']} {f['modelo']} {f['version']}" for f in filas if f"{f['marca']}|{f['modelo']}|{f['version']}" not in specs]
print(len(specs), "de", len(filas), "versiones con datos técnicos;", sum(len(os.listdir(GAL)) for _ in [0]), "fotos en galería")
for a in avisos: print("AVISO", a)
for s in sin: print("SIN DATOS", s)
