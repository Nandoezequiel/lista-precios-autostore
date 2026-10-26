# Lista de Precios AutoStore (uso personal, sin publicar)

**Abrir:** doble clic en `INICIAR_LISTA.bat` (levanta un servidor local en http://127.0.0.1:8770 y abre el navegador).
Sin el servidor la lista se ve igual, pero el **Asesor IA** y la ficha PDF incrustada necesitan el servidor.

**Pestañas:** 0km · Por marca · Usados (con 6 usados de DEMOSTRACIÓN: se borran con «✎ Editar → Borrar demostración»).

**En otra PC (ej. la del trabajo)** — repo privado en GitHub
1. Instalar Python 3 (python.org, tildar «Add to PATH») y Git.
2. `git clone https://github.com/Nandoezequiel/lista-precios-autostore.git` y, dentro de la carpeta, `pip install -r requirements.txt`.
3. Clave del Asesor IA: crear `clave_api.txt` en la carpeta con la clave de Anthropic (no se sube al repo) o definir `ANTHROPIC_API_KEY`.
4. Doble clic en `INICIAR_LISTA.bat`. Para traer cambios: `git pull`.
Los cambios de «✎ Editar» y los usados quedan en el navegador de cada PC (no viajan por GitHub).

**Actualizar con una lista nueva del gerente**
1. `python -I ml_precios.py` → baja los avisos 0km de Mercado Libre Uruguay (referencia de precios).
2. `python -I generar_datos.py "ruta\PRECIOS SANTA ROSA.xlsx"` → regenera `datos.js`.

**Archivos:** `index.html` (la app), `datos.js` (generado), `mapas.js` (qué foto y qué ficha va a cada modelo), `usados.js` (usados demo),
`server.py` (servidor + Asesor IA), `fichas/` (PDF), `fichas_txt/` (lo que lee la IA; `_crudo/` = texto extraído, `_visual/` = lectura por versión),
`armar_fichas.py` (une _visual + _crudo), `herramientas_fichas/` (lectores de tablas por posición), `fotos/`, `assets/`.

**Datos técnicos, fotos y comparador (25/10/2026)**
- Las 182 versiones tienen datos técnicos estructurados (`specs.js`) investigados por marca: PDF/fichas oficiales del importador uruguayo y, si faltaban, Latam/fabricante/prensa. Cada ficha dice su confianza, fuentes y dudas (pestaña «Datos técnicos» del panel).
- Materia prima en `investigacion/` (`<grupo>.json` + `descargas/`). Para regenerar: `python -I armar_specs.py` (copia PDF nuevos a `fichas/`, fotos a `fotos/galeria/`, textos «(web)» a `fichas_txt/` para la IA).
- «⇄ Comparar» (barra de arriba): tocá filas para elegir hasta 4 versiones → «Ver comparativa»: precio + datos técnicos + equipamiento, «Solo diferencias», agregar versión, imprimir, copiar y Asesor IA sobre esas versiones.
- Reiniciar `INICIAR_LISTA.bat` después de regenerar (el servidor lee `specs.js` al arrancar).

**Asesor IA**
- Necesita la API de Anthropic (no responde «con código»): la app arma el contexto (lista completa + usados + 1 a 3 fichas) y lo manda a Claude.
- Clave: `ANTHROPIC_API_KEY` o, si no existe, `API_KEY_CLAUDE_FERNANDO.txt` (carpeta raíz de proyectos). Nunca llega al navegador.
- Selector «Modo» en el chat: **Preciso** = Claude Sonnet 5.5 (≈ 1,6 a 3,5 centavos de dólar por consulta) · **Rápido** = Claude Haiku 5.5 (≈ 0,1 a 0,2 centavos).
- **Gratis (Gemini)**: tercera opción del selector. Crear una clave gratuita en aistudio.google.com, guardarla sola en `clave_gemini.txt` (o `GEMINI_API_KEY`) y reiniciar la lista. Modelo por defecto `gemini-2.5-flash` (cambiable con `GEMINI_MODELO`). Sin clave el chat avisa. La cuota gratuita tiene límites diarios y Google puede usar lo enviado para mejorar sus productos.
- El chat muestra el gasto de la consulta, del día y del mes (`gasto_ia.json`). No ve leasing ni CIF.

**Ediciones locales:** «✎ Editar» guarda cambios solo en este navegador (localStorage); «Restaurar lista del Excel» los descarta.
Detalle completo en `..\AUDITORIA_FOLLETOS_AUTOSTORE_PARTE3.md`.
