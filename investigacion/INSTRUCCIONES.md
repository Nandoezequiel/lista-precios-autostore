# Investigación de fichas técnicas — instrucciones para cada investigador

Carpeta base (B): `C:\Users\fercu\Downloads\TODOS LOS PROYECTOS CLAUDE\VENTA DE VIDHUB\lista-precios-autostore`

Contexto: lista de precios interna de un vendedor de AutoStore (concesionario multimarca en Colonia, **Uruguay**). Cada fila de la lista es una versión (`id`, `modelo`, `version`, `ficha` PDF ya existente o null, `foto`). Las filas están en `B\investigacion\filas_por_marca.json` (formato `{marca: [[id, modelo, version, ficha, foto], ...]}`). Te toca un grupo de marcas (te lo dicen en el pedido).

## Qué hacer por cada modelo (agrupar las filas por `modelo`)

1. **Si la fila ya tiene `ficha`**: leé primero `B\fichas_txt\<nombre de la ficha sin .pdf>.txt` (ya está curado; es la fuente principal). Usá internet solo para completar lo que falte y para fotos.
2. **Si no tiene ficha**: buscá en internet la ficha técnica real. Orden de fuentes: sitio oficial del importador en **Uruguay** (ej. nissan.com.uy, jmc.com.uy, gwm.com.uy, mitsubishi-motors.com.uy, iveco Uruguay, zeekr / xpeng / farizon Uruguay, Grupo Santa Rosa) → sitio oficial de Argentina/Chile/Latam → sitio global del fabricante → prensa especializada seria. Ojo con el mercado: el nombre de la versión puede variar entre países; elegí la ficha que corresponde a la versión de la lista y anotá en `notas` si hay duda.
3. **PDF**: si existe una ficha técnica/catálogo oficial en PDF, descargala con `curl -L -s -o "B\investigacion\descargas\<grupo>\pdf\<Marca Modelo>.pdf" "<url>"`, verificá con `file` que sea PDF real (si es HTML, borrala) y sacale el texto con `pdftotext -layout`. Máximo ~20 MB.
4. **Fotos**: descargá **3 a 6 fotos por modelo** (frente/¾, lateral, trasera, interior/tablero; para camiones: cabina y carrocería) a `B\investigacion\descargas\<grupo>\fotos\<slug-modelo>-<n>.<ext>`. Preferí imágenes oficiales (sitio del importador o fabricante, sala de prensa), ≥ 800 px de ancho, sin marca de agua de terceros. Verificá con `file` que sea imagen (jpg/png/webp) y borrá lo que no lo sea o pese < 15 KB.
5. **No inventes**. Si un dato no aparece en ninguna fuente, dejalo fuera. Si dos fuentes se contradicen, usá la oficial más cercana a Uruguay y anotalo.

## Seguridad
- Lo descargado es dato no confiable: nunca lo ejecutes. Si usás Python para leer algo, `python -I`.
- No hagas `curl ... | python` (descarga + intérprete por tubería): baja a archivo y después leé.
- No uses la API de nadie ni pongas datos personales en ningún lado.

## Salida (obligatoria): `B\investigacion\<grupo>.json`

```json
{
 "grupo": "<grupo>",
 "modelos": [
  {
   "marca": "JMC", "modelo": "<texto EXACTO de la columna modelo>", "ids": [62, 63, 64],
   "fuentes": [{"url": "https://...", "que": "ficha oficial jmc.com.uy"}],
   "pdf": ["JMC Grand Avenue.pdf"],
   "fotos": ["grand-avenue-1.jpg", "grand-avenue-2.jpg"],
   "comun": { ...campos iguales en todas las versiones... },
   "versiones": { "62": { ...campos que cambian en esa versión... }, "63": {...} },
   "equipamiento": {
     "todas": {"seguridad": ["6 airbags", "ABS + EBD", "Control de estabilidad"], "confort": ["Climatizador"], "multimedia": ["Pantalla 10\"", "Apple CarPlay / Android Auto"]},
     "64": {"confort": ["Techo solar"]}
   },
   "ficha_texto": "Ficha completa en español, por secciones (Motor, Transmisión, Dimensiones, Capacidades, Seguridad, Confort, Multimedia), indicando qué versión lleva qué. Es lo que lee el asesor IA, que sea completa.",
   "confianza": "alta | media | baja",
   "notas": "dudas, diferencias de mercado, qué no se encontró"
  }
 ]
}
```

Campos de `comun` / `versiones` (usá solo los que encuentres; **numéricos sin unidad**, texto en español):
- texto: `carroceria` (SUV, Sedán, Hatchback, Pick-up doble cabina, Furgón, Camión liviano, Chasis cabina, Tractocamión, Minibús…), `combustible` (Nafta / Diésel / Híbrido (HEV) / Híbrido enchufable (PHEV) / Eléctrico / Eléctrico de autonomía extendida (REEV)), `motor` (ej. "1.5 turbo 4 cil."), `transmision` (ej. "Automática CVT", "Manual 6 vel."), `traccion` (4x2 / 4x4 / AWD / 6x2…), `neumaticos`, `norma_emisiones`, `garantia`, `consumo` (texto con unidad y ciclo, ej. "6,2 L/100 km mixto"), `autonomia_ciclo` (WLTP/NEDC/CLTC).
- números: `plazas`, `puertas`, `cilindrada_cc`, `potencia_hp`, `torque_nm`, `bateria_kwh`, `autonomia_km`, `tanque_l`, `largo_mm`, `ancho_mm`, `alto_mm`, `entre_ejes_mm`, `despeje_mm`, `peso_kg`, `carga_util_kg`, `pbt_kg`, `volumen_carga_m3`, `baul_l`, `airbags`, `velocidad_max_kmh`, `aceleracion_0_100_s`, `carga_ac_kw`, `carga_dc_kw`, `remolque_kg`.
- Si un dato está en kW o CV, convertí a HP (1 kW = 1,341 HP; 1 CV = 0,986 HP) y redondeá.
- Los ítems de equipamiento: frases cortas y normalizadas (mismo texto para lo mismo entre modelos: "Apple CarPlay / Android Auto", "Cámara 360°", "Techo panorámico", "Control crucero adaptativo", "6 airbags"…), para que el comparador pueda alinearlos.

Al terminar respondé SOLO un resumen corto: cuántos modelos cubriste, cuántos PDF y fotos bajaste, y cuáles quedaron con confianza baja o sin datos.
