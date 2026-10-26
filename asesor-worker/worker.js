// Asesor IA de la versión web (GitHub Pages). Misma lógica que /api/chat de server.py; la lista, las fichas
// y las reglas se leen de la página publicada. Secretos: ANTHROPIC_API_KEY y CLAVE_ACCESO (contraseña del chat).
const SITIO = "https://nandoezequiel.github.io/lista-precios-autostore/";
const ORIGEN = "https://nandoezequiel.github.io";
const MAX_FICHA = 30000;
const PRECIOS = { "claude-sonnet-5-5": [2.0, 10.0, 0.2, 2.5], "claude-haiku-5-5": [0.1, 0.5, 0.01, 0.125] };   // USD por millón: entrada, salida, caché leída, caché escrita
const CALIDADES = { preciso: ["claude-sonnet-5-5", "medium"], rapido: ["claude-haiku-5-5", "low"] };
const GENERICAS = new Set("de la el los las un una con sin y o a en que cual cuales tiene tienen viene vienen es son ser como cuanto cuesta precio modelo version auto camioneta lleva trae tiene para por del al lo se me te".split(" "));

let datos = null, cargado = 0;
async function cargar() {   // ponytail: caché en memoria 10 min; tras publicar una lista nueva tarda eso en verse
  if (datos && Date.now() - cargado < 600000) return datos;
  const txt = f => fetch(SITIO + f).then(r => { if (!r.ok) throw new Error(f); return r.text() });
  const js = (t, v) => JSON.parse(t.split(`window.${v} = `)[1].trim().replace(/;$/, ""));
  const [d, s, sistema] = await Promise.all([txt("datos.js"), txt("specs.js"), txt("asesor_sistema.txt")]);
  const DATOS = js(d, "DATOS"), SPECS = js(s, "SPECS");
  for (const r of DATOS.filas) { r.spec = SPECS[`${r.marca}|${r.modelo}|${r.version}`] || {}; r.doc = r.ficha || r.spec.txt || null }
  datos = { DATOS, FILAS: DATOS.filas, sistema }; cargado = Date.now();
  return datos;
}

const toks = s => (s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/\([^)]*\)/g, " ").match(/[a-z0-9]+/g) || []);

function fichasRelevantes(FILAS, pregunta, previas, ctxId) {
  const out = [], add = f => { if (f && !out.includes(f)) out.push(f) };
  if (ctxId != null && FILAS[ctxId]) add(FILAS[ctxId].doc);
  const q = new Set(toks([...previas.slice(-2), pregunta].join(" ")).filter(t => !GENERICAS.has(t)));
  const peso = t => (/^[a-z]+$/.test(t) && t.length >= 3 ? 1 : 0.3);
  const puntaje = {};
  for (const r of FILAS) {
    if (!r.doc) continue;
    const rt = [...new Set(toks(`${r.marca} ${r.modelo} ${r.version}`).filter(t => !GENERICAS.has(t)))];
    const ov = rt.filter(t => q.has(t));
    if (!ov.some(t => /^[a-z]+$/.test(t) && t.length >= 3)) continue;
    const sc = ov.reduce((a, t) => a + peso(t), 0) / Math.max(1, rt.reduce((a, t) => a + peso(t), 0));
    puntaje[r.doc] = Math.max(puntaje[r.doc] || 0, sc);
  }
  const mejor = Math.max(0, ...Object.values(puntaje));
  Object.entries(puntaje).sort((a, b) => b[1] - a[1]).forEach(([f, sc]) => { if (sc >= 0.5 * mejor) add(f) });
  return out.slice(0, 3);
}

function tablaPrecios(FILAS, ediciones) {
  return FILAS.filter(r => !(ediciones[r.id] || {}).eliminado).map(r => {
    const e = ediciones[r.id] || {}, pvp = e.pvp ?? r.pvp, bono = (e.bono ?? r.bono) || 0;
    return `[${r.id}] ${r.marca} | ${r.modelo} | ${r.version} | PVP ${pvp}` + (bono ? ` | bono ${bono}` : "") + ` | final ${pvp - bono}`
      + (r.estado ? `|${r.estado}` : "") + (r.nota ? `|${r.nota.slice(0, 140)}` : "");
  }).join("\n");
}

const cors = { "Access-Control-Allow-Origin": ORIGEN, "Access-Control-Allow-Headers": "Content-Type, x-clave", "Access-Control-Allow-Methods": "GET, POST, OPTIONS" };
const resp = (obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", ...cors } });

async function chat(d, env) {
  if (d.calidad === "gemini") return resp({ error: "El modo Gemini solo funciona en la versión local (INICIAR_LISTA.bat). Elegí Preciso o Rápido." }, 503);
  const { DATOS, FILAS, sistema } = await cargar();
  const pregunta = String(d.pregunta || "").trim().slice(0, 1200);
  if (!pregunta) return resp({ error: "Pregunta vacía." }, 400);
  const hist = (d.historial || []).slice(-8).filter(m => ["user", "assistant"].includes(m.rol) && String(m.texto || "").trim());
  const ctxId = Number.isInteger(d.contexto_id) && FILAS[d.contexto_id] ? d.contexto_id : null;
  const ediciones = d.ediciones && typeof d.ediciones === "object" ? d.ediciones : {};
  const comparar = (d.comparar || []).filter(i => Number.isInteger(i) && FILAS[i]).slice(0, 4);
  const fichas = comparar.length ? [...new Set(comparar.map(i => FILAS[i].doc).filter(Boolean))]
    : fichasRelevantes(FILAS, pregunta, hist.filter(m => m.rol === "user").map(m => m.texto), ctxId);
  const lim = fichas.length < 2 ? MAX_FICHA : 14000;
  const bloques = (await Promise.all(fichas.map(async f => {
    const r = await fetch(SITIO + "fichas_txt/" + encodeURIComponent(f.replace(/\.(pdf|txt)$/i, "")) + ".txt");
    return r.ok ? `=== FICHA TÉCNICA: ${f} ===\n` + (await r.text()).replace(/--- p\d+ ---/g, "").slice(0, lim) : null;
  }))).filter(Boolean);
  let ctx = ctxId != null ? `\nVEHÍCULO ABIERTO EN PANTALLA: [${ctxId}] ${FILAS[ctxId].marca} ${FILAS[ctxId].modelo} — ${FILAS[ctxId].version}\n` : "";
  if (comparar.length) ctx = "\nVERSIONES EN COMPARACIÓN (datos técnicos estructurados de cada una):\n" + comparar.map(i =>
    `[${i}] ${FILAS[i].marca} ${FILAS[i].modelo} — ${FILAS[i].version} | datos: ${JSON.stringify(FILAS[i].spec.d || {})} | equipamiento: ${JSON.stringify(FILAS[i].spec.eq || {})}`).join("\n") + "\n";
  const usados = (Array.isArray(d.usados) ? d.usados : []).slice(0, 80).filter(u => u && typeof u === "object").map(u =>
    `- ${u.marca || ""} ${u.modelo || ""} ${u.version || ""} ${u.anio || ""}, ${u.km ?? "?"} km, ${u.combustible || ""}, ${u.color || ""}, USD ${u.precio ?? "?"}` + (u.accesorios ? ` · ${String(u.accesorios).slice(0, 160)}` : "") + (u.demo ? " [DEMO]" : "")).join("\n");
  const estable = sistema + `\n=== LISTA DE PRECIOS VIGENTE (Excel de Santa Rosa, ${DATOS.generado}) ===\n` + tablaPrecios(FILAS, ediciones);
  const dinamico = ctx + (usados ? "\n=== USADOS EN STOCK ===\n" + usados + "\n" : "") + "\n" + (bloques.length ? bloques.join("\n\n") : "(No hay ficha técnica cargada para este pedido: si preguntan por equipamiento, decí que necesitás saber el modelo.)");
  const [modelo, esfuerzo] = CALIDADES[d.calidad] || CALIDADES.preciso;
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST", headers: { "x-api-key": env.ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json" },
    body: JSON.stringify({ model: modelo, max_tokens: 1500, output_config: { effort: esfuerzo },
      system: [{ type: "text", text: estable, cache_control: { type: "ephemeral" } }, { type: "text", text: dinamico }],
      messages: [...hist.map(m => ({ role: m.rol, content: String(m.texto).slice(0, 3000) })), { role: "user", content: pregunta }] })
  });
  const j = await r.json();
  if (!r.ok) return resp({ error: "Error al consultar la IA: " + ((j.error || {}).type || r.status) }, 502);
  const u = j.usage || {}, p = PRECIOS[modelo];
  const usd = ((u.input_tokens || 0) * p[0] + (u.output_tokens || 0) * p[1] + (u.cache_read_input_tokens || 0) * p[2] + (u.cache_creation_input_tokens || 0) * p[3]) / 1e6;
  return resp({ respuesta: (j.content || []).filter(b => b.type === "text").map(b => b.text).join(""), fichas, usd: Math.round(usd * 1e5) / 1e5 });
}

export default {
  async fetch(req, env) {
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });
    const url = new URL(req.url);
    if (url.pathname === "/api/estado") return resp({ ok: true });
    if (url.pathname !== "/api/chat" || req.method !== "POST") return resp({ error: "No encontrado" }, 404);
    if (!env.CLAVE_ACCESO || req.headers.get("x-clave") !== env.CLAVE_ACCESO) return resp({ error: "clave" }, 401);
    try { return await chat(await req.json(), env) }
    catch (e) { return resp({ error: "Error del asesor: " + e.message }, 500) }
  }
};
