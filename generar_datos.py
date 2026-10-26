"""Lee PRECIOS SANTA ROSA.xlsx y genera datos.js para la lista de precios de AutoStore.

Uso:  python -I generar_datos.py "ruta\\PRECIOS SANTA ROSA.xlsx"
Cuando el gerente mande una lista nueva, se vuelve a correr y listo.
"""
import openpyxl, re, json, sys, os, warnings, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ml_match
warnings.filterwarnings("ignore")

EXCLUIR = {"Renault", "Avatr"}          # marcas que AutoStore no vende (dicho por Fernando 16/10/2026)

def num(v):
    """Número desde 29990, 'USD 29.990', 'USD 36. 588', '$ 65.990'. None si no hay."""
    if isinstance(v, (int, float)):
        return round(v) if v and v > 100 else None
    if isinstance(v, str):
        s = v.replace(" ", "")
        m = re.search(r"\d{1,3}(?:\.\d{3})+|\d{4,}", s)
        if m:
            return int(m.group(0).replace(".", ""))
    return None

def txt(v):
    return re.sub(r"\s+", " ", str(v)).strip() if v not in (None, "") else ""

# hoja: (marca fija o None, columnas {campo: letra}, fila inicial, hasta fila)
# bloques: algunas hojas tienen dos tablas lado a lado
CFG = {
 "Nissan":  [("Nissan", dict(m="A", v="D", pvp="F", an="G", cif="H", lea="I"), 2, 60),
             ("Nissan", dict(m="K", v="N", pvp="P", an="Q", cif="S", lea="U"), 2, 60)],
 "Omoda - Jaecoo": [(None, dict(m="A", v="C", pvp="G", cif="H", nota="E"), 2, 20)],
 "Farizon": [("Farizon", dict(m="A", v="C", pvp="D", an="E", lea="F", cif="G"), 2, 20)],
 "JMC":     [("JMC", dict(m="A", v="C", pvp="E", an="F", lea="G", cif="H", nota="I"), 2, 80)],
 "Changan": [("Changan", dict(m="A", v="D", pvp="F", an="G", cif="H", lea="I"), 2, 20)],
 "Deepal":  [("Deepal", dict(m="A", v="C", pvp="E", an="F", cif="G"), 2, 20)],
 "GWM.":    [("GWM", dict(m="A", v="C", lista="D", pvp="E", cif="F", nota="G"), 3, 30)],
 "Leapmotor": [("Leapmotor", dict(m="A", v="D", pvp="F", an="G", cif="H", nota="I"), 2, 8)],
 "MMC":     [("Mitsubishi", dict(m="A", v="D", pvp="F", an="G", cif="I", lea="J"), 2, 20)],
 "Zeekr":   [("Zeekr", dict(m="A", v="C", pvp="F", cif="G", nota="E"), 2, 10)],
 "Iveco":   [("Iveco", dict(m="A", v="D", pvp="F", lea="G", cif="H"), 2, 50)],
 "Xpeng":   [("Xpeng", dict(m="B", v="C", pvp="E", an="F"), 2, 8)],
}

def main(ruta):
    wb = openpyxl.load_workbook(ruta, data_only=True)
    filas = []
    for hoja, bloques in CFG.items():
        ws = wb[hoja]
        for marca_fija, c, r0, r1 in bloques:
            modelo = ""
            for r in range(r0, r1 + 1):
                g = lambda k: ws[f"{c[k]}{r}"].value if k in c else None
                if txt(g("m")) and not txt(g("m")).startswith("Modelo"):
                    modelo = txt(g("m"))
                version = txt(g("v"))
                pvp = num(g("pvp"))
                if version and pvp is None and hoja == "Iveco" and filas and filas[-1]["_r"] == r - 1 and filas[-1]["_h"] == hoja:
                    filas[-1]["version"] += " — " + version   # Iveco: la 2.ª línea describe la versión
                    continue
                if not version or pvp is None:
                    continue
                marca = marca_fija
                if marca is None:   # hoja Omoda - Jaecoo
                    marca = "Jaecoo" if "JAECOO" in version.upper() else "Omoda"
                if marca in EXCLUIR:
                    continue
                an_raw = g("an"); an_txt = txt(an_raw)
                if an_txt == "0": an_txt = ""
                if marca == "GWM":
                    mm = re.match(r"(HAVAL \w+|TANK \d+|ORA \d+|WINGLE \d|POER \w+)", version.upper())
                    modelo = mm.group(1).title() if mm else modelo
                bono = num(an_raw) if isinstance(an_raw, (int, float)) or "USD" in an_txt.upper() else None
                nota = " · ".join(x for x in [txt(g("nota")), "" if bono else an_txt] if x)
                estado = ""
                low = (an_txt + " " + nota).lower()
                if "sin stock" in low: estado = "Sin stock"
                elif "no disp" in low or "descontinuado" in low: estado = "No disponible"
                elif "consultar" in low: estado = "Consultar"
                filas.append(dict(
                    marca=marca, modelo=modelo, version=version, pvp=pvp,
                    lista=num(g("lista")) if "lista" in c else None,
                    bono=bono, final=pvp - (bono or 0),
                    cif=num(g("cif")), leasing=num(g("lea")),
                    nota=nota[:500], estado=estado, _r=r, _h=hoja))
    cache = ml_match.cargar()
    mp = json.loads(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapas.js"), encoding="utf-8").read().split("window.MAPAS = ", 1)[1].rstrip().rstrip(";"))
    def buscar(lista, clave):
        for t in lista:
            if re.search(t[0], clave): return t
        return None
    for i, x in enumerate(filas):
        x["id"] = i
        x.pop("_r"); x.pop("_h")
        clave2 = (x["marca"] + " " + x["modelo"] + " " + x["version"]).upper()
        ft, fi = buscar(mp["fotos"], clave2), buscar(mp["fichas"], clave2)
        x["foto"], x["foto_ilu"], x["ficha"] = (ft[1] if ft else None), bool(ft and len(ft) > 2), (fi[1] if fi else None)
        x["verif"] = ml_match.verificar(x, cache) if cache else dict(estado="sin", texto="Sin datos de Mercado Libre (correr ml_precios.py).", n=0)
    out = dict(generado=datetime.date.today().isoformat(), fuente=os.path.basename(ruta), ml_fecha=(cache or {}).get('fecha'), filas=filas)
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos.js")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("window.DATOS = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
    marcas = sorted({x["marca"] for x in filas})
    print(len(filas), "versiones,", len(marcas), "marcas:", ", ".join(marcas))

if __name__ == "__main__":
    main(sys.argv[1])
