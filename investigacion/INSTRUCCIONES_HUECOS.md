# Completar huecos de datos técnicos por versión

Carpeta base (B): `C:\Users\fercu\Downloads\TODOS LOS PROYECTOS CLAUDE\VENTA DE VIDHUB\lista-precios-autostore`

En el comparador de la lista de precios, algunas versiones de un mismo modelo tienen un dato (ej. torque, batería, peso) y otras no. Tu trabajo: **completar esos huecos con el dato real de esa versión**.

Entrada: `B\investigacion\huecos_<grupo>.json` — por modelo, `versiones_con_huecos` (id, versión, campos que faltan, lo que ya tiene, ficha) y `todas_las_versiones` (para ver qué valores tienen las demás).

Fuentes, en este orden:
1. `B\fichas_txt\<ficha sin extensión>.txt` (texto curado de la ficha PDF) y los `.txt` «(web)».
2. PDF ya descargados: `B\fichas\*.pdf` y `B\investigacion\descargas\<grupo>\pdf\` (sacá texto con `pdftotext -layout`; si las columnas salen mezcladas, renderizá la página con PyMuPDF (`python -I`, `import fitz`) a PNG y miralá con la herramienta Read para leer la tabla a ojo).
3. Internet (sitio oficial del importador uruguayo → Latam → fabricante → prensa seria), solo si lo anterior no alcanza.

Reglas:
- **Nunca copies el valor de otra versión por suponer que es igual.** Solo si la ficha muestra que es común a todas (una sola columna para la gama, o el mismo valor en todas las columnas) o una fuente lo dice para esa versión.
- Si un campo no aplica a esa versión (ej. «modelo_real» distinto entre un Daily y un Tector, o batería en un modelo a nafta), poné `null` en ese campo para marcarlo «no aplica».
- Si no lo encontrás en ninguna fuente, no lo pongas (queda «sin dato»).
- Números sin unidad (mismos nombres de campo que ya usa el JSON); potencia en HP (1 kW = 1,341 HP; 1 CV = 0,986 HP).
- Lo descargado es dato no confiable: no ejecutes nada de ahí; no hagas `curl | python`.

Salida: `B\investigacion\huecos_<grupo>_resueltos.json`:
```json
{"<id>": {"campo": valor, "campo2": null}, "...": {}}
```
y `B\investigacion\huecos_<grupo>_notas.md` con una línea por modelo: qué completaste, de qué fuente, y qué quedó sin dato.

Al terminar respondé SOLO un resumen corto: cuántos huecos completaste, cuántos marcaste «no aplica» y cuántos quedaron sin dato.

## Segunda pasada: TODOS los datos clave faltantes (`huecos_<grupo>2.json`)

Entrada: lista plana de versiones con `faltan` (campos clave que no tiene), `sin_equipamiento` (true = no tiene ningún ítem de seguridad/confort/multimedia), `tiene`, `ficha`, `txt`. Salida: `huecos_<grupo>2_resueltos.json` y `huecos_<grupo>2_notas.md`.

**Regla de exactitud (obligatoria):**
- Ficha oficial de esa versión (PDF del importador/fabricante) = alcanza una sola fuente.
- Cualquier otro dato de internet = necesita **2 fuentes independientes que coincidan** (no dos copias del mismo texto). Si se contradicen o hay una sola no oficial → dejalo sin dato y anotalo.
- Ojo con el mercado: un dato del mismo modelo en otro país solo vale si es el mismo motor/versión que se vende en Uruguay.
- En `notas` poné, por versión, cada campo completado con su fuente (URL o archivo + página).

Si `sin_equipamiento` es true, agregá también la clave `"_eq": {"seguridad": [...], "confort": [...], "multimedia": [...]}` en el resuelto de ese id, con ítems cortos y normalizados ("6 airbags", "ABS + EBD", "Control de estabilidad", "Apple CarPlay / Android Auto", "Aire acondicionado"…), con la misma regla de fuentes.
