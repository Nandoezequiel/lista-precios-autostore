"""Servidor local de la Lista de Precios AutoStore: sirve la página y atiende el asesor IA.

Uso:  python server.py        → abre http://127.0.0.1:8770
Solo escucha en 127.0.0.1 (tu PC). La clave de Anthropic se toma de la variable ANTHROPIC_API_KEY o del
archivo API_KEY_CLAUDE_FERNANDO.txt de la carpeta raíz de proyectos; nunca se envía al navegador.
"""
import os, re, json, unicodedata, webbrowser, threading, datetime
from flask import Flask, request, jsonify, send_from_directory, abort

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO = os.environ.get("MODELO_CHAT", "claude-sonnet-5-5")
PUERTO = int(os.environ.get("PUERTO", "8770"))
MAX_FICHA = 30000          # caracteres de cada ficha que se mandan al modelo
EXT_OK = {".html", ".js", ".css", ".jpg", ".jpeg", ".png", ".webp", ".svg", ".pdf", ".ico"}

def buscar_clave():
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if k: return k
    for p in (os.path.join(AQUI, "clave_api.txt"), os.path.join(AQUI, "..", "..", "API_KEY_CLAUDE_FERNANDO.txt")):
        if os.path.exists(p):
            m = re.search(r"sk-ant-[A-Za-z0-9_\-]+", open(p, encoding="utf-8", errors="ignore").read())
            if m: return m.group(0)
    return ""

CLAVE = buscar_clave()
cliente = None
if CLAVE:
    import anthropic
    cliente = anthropic.Anthropic(api_key=CLAVE)

# Gemini (cuota gratuita de Google AI Studio): clave en GEMINI_API_KEY o en clave_gemini.txt (junto a este archivo). Nunca va al navegador.
GEMINI_MODELO = os.environ.get("GEMINI_MODELO", "gemini-2.5-flash")
def buscar_clave_gemini():
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    if k: return k
    p = os.path.join(AQUI, "clave_gemini.txt")
    if os.path.exists(p):
        m = re.search(r"AIza[A-Za-z0-9_\-]{30,}", open(p, encoding="utf-8", errors="ignore").read())
        if m: return m.group(0)
    return ""
GCLAVE = buscar_clave_gemini()

def preguntar_gemini(sistema_txt, msgs):
    """Llama a la API REST de Gemini (sin dependencias). Devuelve (texto, tokens_entrada, tokens_salida)."""
    import urllib.request, urllib.error
    cuerpo = {"system_instruction": {"parts": [{"text": sistema_txt}]},
              "contents": [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in msgs],
              "generationConfig": {"maxOutputTokens": 1500, "temperature": 0.2}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODELO}:generateContent",
                                 data=json.dumps(cuerpo).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": GCLAVE})
    try:
        j = json.load(urllib.request.urlopen(req, timeout=90))
    except urllib.error.HTTPError as e:
        msg = {429: "Se alcanzó el límite gratuito de Gemini (probá en un rato o usá el modo Claude).", 400: "Gemini rechazó la consulta o la clave no es válida.",
               403: "La clave de Gemini no tiene permiso.", 404: f"El modelo {GEMINI_MODELO} no existe (cambiá GEMINI_MODELO)."}.get(e.code, f"Gemini respondió error {e.code}.")
        raise RuntimeError(msg)
    partes = (j.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
    texto = "".join(p.get("text", "") for p in partes) or "Gemini no devolvió respuesta (puede haberla bloqueado). Probá reformular."
    um = j.get("usageMetadata", {})
    return texto, um.get("promptTokenCount", 0), um.get("candidatesTokenCount", 0)

def cargar_datos():
    t = open(os.path.join(AQUI, "datos.js"), encoding="utf-8").read()
    return json.loads(t.split("window.DATOS = ", 1)[1].rstrip().rstrip(";"))
DATOS = cargar_datos()
FILAS = DATOS["filas"]

def cargar_specs():
    p = os.path.join(AQUI, "specs.js")
    if not os.path.exists(p): return {}
    return json.loads(open(p, encoding="utf-8").read().split("window.SPECS = ", 1)[1].rstrip().rstrip(";"))
SPECS = cargar_specs()
for _r in FILAS:   # doc = ficha que lee la IA: el PDF original (su .txt curado) o la ficha armada con fuentes de internet
    _r["spec"] = SPECS.get(f"{_r['marca']}|{_r['modelo']}|{_r['version']}") or {}
    _r["doc"] = _r.get("ficha") or _r["spec"].get("txt")

def toks(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9]+", re.sub(r"\([^)]*\)", " ", s))
GENERICAS = set("de la el los las un una con sin y o a en que cual cuales tiene tienen viene vienen es son ser como cuanto cuesta precio modelo version auto camioneta lleva trae tiene para por del al lo se me te".split())

def fichas_relevantes(pregunta, previas, ctx_id):
    """Elige hasta 3 fichas: la del vehículo abierto + las de los modelos que se nombran en la charla."""
    out = []
    def add(f):
        if f and f not in out: out.append(f)
    if ctx_id is not None and 0 <= ctx_id < len(FILAS): add(FILAS[ctx_id].get("doc"))
    q = set(toks(" ".join(previas[-2:] + [pregunta]))) - GENERICAS
    peso = lambda t: 1.0 if (t.isalpha() and len(t) >= 3) else 0.3
    puntaje = {}
    for r in FILAS:
        if not r.get("doc"): continue
        rt = set(toks(r["marca"] + " " + r["modelo"] + " " + r["version"])) - GENERICAS
        ov = rt & q
        if not any(t.isalpha() and len(t) >= 3 for t in ov): continue      # tiene que coincidir una palabra (marca/modelo/versión), no solo un número
        sc = sum(peso(t) for t in ov) / max(1.0, sum(peso(t) for t in rt))
        puntaje[r["doc"]] = max(puntaje.get(r["doc"], 0), sc)
    mejor = max(puntaje.values(), default=0)
    for f, sc in sorted(puntaje.items(), key=lambda x: -x[1]):
        if sc >= 0.5 * mejor: add(f)
    return out[:3]

def tabla_precios(ediciones, interno):
    filas = []
    for r in FILAS:
        e = ediciones.get(str(r["id"]), {})
        if e.get("eliminado"): continue
        pvp = e.get("pvp", r["pvp"]); bono = e.get("bono", r["bono"]) or 0
        extra = ""   # leasing/CIF no van al chat: el cliente puede estar escuchando
        est = f"|{r['estado']}" if r["estado"] else ""
        nota = f"|{r['nota'][:140]}" if r["nota"] else ""
        filas.append(f"[{r['id']}] {r['marca']} | {r['modelo']} | {r['version']} | PVP {pvp}" + (f" | bono {bono}" if bono else "") + f" | final {pvp - bono}{extra}{est}{nota}")
    return "\n".join(filas)

SISTEMA = open(os.path.join(AQUI, "asesor_sistema.txt"), encoding="utf-8").read()   # mismas reglas que usa el Worker de la versión web

# USD por millón de tokens: (entrada, salida, lectura de caché, escritura de caché 5 min). Fuente: tabla de modelos de Anthropic.
PRECIOS = {"claude-sonnet-5-5": (2.00, 10.00, 0.20, 2.50), "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125),
           "claude-opus-5-5": (4.00, 20.00, 0.40, 5.00)}
GASTO_ARCHIVO = os.path.join(AQUI, "gasto_ia.json")

CALIDADES = {"preciso": (MODELO, "medium"), "rapido": ("claude-haiku-5-5", "low")}   # (modelo, esfuerzo de razonamiento)

def registrar_gasto(ent, sal, c_leida, c_escrita, modelo=MODELO):
    p = PRECIOS.get(modelo, PRECIOS["claude-sonnet-5-5"])
    usd = 0.0 if modelo.startswith("gemini") else (ent * p[0] + sal * p[1] + c_leida * p[2] + c_escrita * p[3]) / 1e6   # Gemini: cuota gratuita
    try:
        g = json.load(open(GASTO_ARCHIVO, encoding="utf-8")) if os.path.exists(GASTO_ARCHIVO) else {}
        hoy = datetime.date.today().isoformat(); d = g.setdefault(hoy, {"consultas": 0, "usd": 0.0})
        d["consultas"] += 1; d["usd"] = round(d["usd"] + usd, 6)
        json.dump(g, open(GASTO_ARCHIVO, "w", encoding="utf-8"))
    except Exception:
        pass
    return usd

def resumen_gasto():
    try:
        g = json.load(open(GASTO_ARCHIVO, encoding="utf-8")) if os.path.exists(GASTO_ARCHIVO) else {}
    except Exception:
        g = {}
    hoy = datetime.date.today().isoformat(); mes = hoy[:7]
    return dict(hoy=round(g.get(hoy, {}).get("usd", 0), 4), consultas_hoy=g.get(hoy, {}).get("consultas", 0),
                mes=round(sum(v["usd"] for k, v in g.items() if k.startswith(mes)), 4), consultas_mes=sum(v["consultas"] for k, v in g.items() if k.startswith(mes)))

app = Flask(__name__)

@app.get("/")
def raiz():
    return send_from_directory(AQUI, "index.html")

@app.get("/api/estado")
def estado():
    return jsonify(ok=bool(cliente), gemini=bool(GCLAVE), modelo=MODELO, filas=len(FILAS), gasto=resumen_gasto())

@app.post("/api/chat")
def chat():
    d = request.get_json(silent=True) or {}
    usa_gemini = d.get("calidad") == "gemini"
    if usa_gemini and not GCLAVE:
        return jsonify(error="Falta la clave de Gemini: guardala en clave_gemini.txt (carpeta de la lista) o en GEMINI_API_KEY, y reiniciá la lista."), 503
    if not usa_gemini and not cliente:
        return jsonify(error="No hay clave de Anthropic configurada (ANTHROPIC_API_KEY o API_KEY_CLAUDE_FERNANDO.txt)."), 503
    pregunta = str(d.get("pregunta", "")).strip()[:1200]
    if not pregunta: return jsonify(error="Pregunta vacía."), 400
    hist = [m for m in (d.get("historial") or [])[-8:] if m.get("rol") in ("user", "assistant") and str(m.get("texto", "")).strip()]
    ctx_id = d.get("contexto_id") if isinstance(d.get("contexto_id"), int) else None
    interno = bool(d.get("interno"))
    ediciones = d.get("ediciones") if isinstance(d.get("ediciones"), dict) else {}
    previas = [m["texto"] for m in hist if m["rol"] == "user"]
    comparar = [i for i in (d.get("comparar") or []) if isinstance(i, int) and 0 <= i < len(FILAS)][:4]
    if comparar:
        fichas = list(dict.fromkeys(FILAS[i]["doc"] for i in comparar if FILAS[i].get("doc")))
    else:
        fichas = fichas_relevantes(pregunta, previas, ctx_id)
    lim = MAX_FICHA if len(fichas) < 2 else 14000
    bloques = []
    for f in fichas:
        p = os.path.join(AQUI, "fichas_txt", os.path.splitext(f)[0] + ".txt")
        if os.path.exists(p):
            bloques.append(f"=== FICHA TÉCNICA: {f} ===\n" + re.sub(r"--- p\d+ ---", "", open(p, encoding="utf-8", errors="ignore").read())[:lim])
    ctx = ""
    if ctx_id is not None and 0 <= ctx_id < len(FILAS):
        r = FILAS[ctx_id]; ctx = f"\nVEHÍCULO ABIERTO EN PANTALLA: [{r['id']}] {r['marca']} {r['modelo']} — {r['version']}\n"
    if comparar:
        ctx = "\nVERSIONES EN COMPARACIÓN (datos técnicos estructurados de cada una):\n" + "\n".join(
            f"[{i}] {FILAS[i]['marca']} {FILAS[i]['modelo']} — {FILAS[i]['version']} | datos: {json.dumps(FILAS[i]['spec'].get('d', {}), ensure_ascii=False)} | equipamiento: {json.dumps(FILAS[i]['spec'].get('eq', {}), ensure_ascii=False)}"
            for i in comparar) + "\n"
    # Bloque 1 (estable → se cachea: las lecturas de caché cuestan 10 % del precio normal): reglas + lista de precios.
    estable = SISTEMA + "\n=== LISTA DE PRECIOS VIGENTE (Excel de Santa Rosa, " + str(DATOS.get("generado")) + ") ===\n" + tabla_precios(ediciones, interno)
    # Bloque 2 (cambia en cada pregunta): vehículo abierto, usados y fichas elegidas.
    usados = d.get("usados") if isinstance(d.get("usados"), list) else []
    lu = "\n".join(f"- {u.get('marca','')} {u.get('modelo','')} {u.get('version','')} {u.get('anio','')}, {u.get('km','?')} km, {u.get('combustible','')}, {u.get('color','')}, USD {u.get('precio','?')}" + (f" · {str(u.get('accesorios',''))[:160]}" if u.get('accesorios') else "") + (" [DEMO]" if u.get("demo") else "") for u in usados[:80] if isinstance(u, dict))
    dinamico = ctx + ("\n=== USADOS EN STOCK ===\n" + lu + "\n" if lu else "") + "\n" + ("\n\n".join(bloques) if bloques else "(No hay ficha técnica cargada para este pedido: si preguntan por equipamiento, decí que necesitás saber el modelo.)")
    sistema = [{"type": "text", "text": estable, "cache_control": {"type": "ephemeral"}}, {"type": "text", "text": dinamico}]
    msgs = [{"role": m["rol"], "content": str(m["texto"])[:3000]} for m in hist] + [{"role": "user", "content": pregunta}]
    if usa_gemini:
        try:
            texto, t_ent, t_sal = preguntar_gemini(estable + "\n" + dinamico, msgs)
        except Exception as e:
            return jsonify(error=str(e) if isinstance(e, RuntimeError) else "No se pudo conectar con Gemini."), 502
        usd = registrar_gasto(t_ent, t_sal, 0, 0, GEMINI_MODELO)
        return jsonify(respuesta=texto, fichas=fichas, usd=0, gasto=resumen_gasto(), tokens=dict(entrada=t_ent, salida=t_sal, cache_leida=0, cache_escrita=0))
    modelo, esfuerzo = CALIDADES.get(d.get("calidad"), CALIDADES["preciso"])
    try:
        r = cliente.messages.create(model=modelo, max_tokens=1500, system=sistema, messages=msgs, output_config={"effort": esfuerzo})
        texto = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
    except Exception as e:
        return jsonify(error=f"Error al consultar la IA: {type(e).__name__}"), 502
    u = r.usage
    usd = registrar_gasto(u.input_tokens, u.output_tokens, getattr(u, "cache_read_input_tokens", 0) or 0, getattr(u, "cache_creation_input_tokens", 0) or 0, modelo)
    return jsonify(respuesta=texto, fichas=fichas, usd=round(usd, 5), gasto=resumen_gasto(),
                   tokens=dict(entrada=u.input_tokens, salida=u.output_tokens, cache_leida=getattr(u, "cache_read_input_tokens", 0) or 0, cache_escrita=getattr(u, "cache_creation_input_tokens", 0) or 0))

@app.get("/<path:ruta>")
def estatico(ruta):
    if os.path.splitext(ruta)[1].lower() not in EXT_OK: abort(404)
    return send_from_directory(AQUI, ruta)

if __name__ == "__main__":
    if os.environ.get("NO_ABRIR") != "1":
        threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{PUERTO}")).start()
    print(f"Lista de precios AutoStore en http://127.0.0.1:{PUERTO}  (IA: {'lista' if cliente else 'sin clave'}, modelo {MODELO})")
    app.run(host="127.0.0.1", port=PUERTO, debug=False)
