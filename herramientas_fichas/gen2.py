import subprocess, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
T = os.path.dirname(os.path.abspath(__file__))
V = r"C:\Users\fercu\Downloads\TODOS LOS PROYECTOS CLAUDE\VENTA DE VIDHUB\lista-precios-autostore\fichas_txt\_visual"
# (pdf, páginas, nombres de columnas, claves de cabecera, mitades, env, texto manual)
CFG = [
 ("Omoda E5 modelos 2027", [3, 4, 5, 6, 7], "Comfort STD 350,Luxury STD 350,Luxury 430", "COMFORT,LUXURY,STD,350,430,EV", 1, {},
  "VERSIONES del Omoda E5 EV 2027: «Comfort STD 350» (batería 50 kWh, autonomía 350 km WLTP), «Luxury STD 350» (350 km WLTP) y «Luxury 430» (batería 60 kWh, 430 km WLTP). Las tablas indican qué trae cada una (SÍ/NO); «—» en la ficha significa que no lo trae."),
 ("JAECOO 6", [3, 4, 5], "Luxury 4x2,Flagship 4x4", "Luxury,Flagship,LUXURY,FLAGSHIP,4X2,4X4", 1, {"MARK_H": "1"},
  "VERSIONES del Jaecoo 6 EV: «Luxury 4x2» y «Flagship 4x4». Cuando una fila dice «en todas» las trae ambas; si el valor difiere, el texto de la fila trae primero el de Luxury y después el de Flagship."),
 ("Jaecoo5 Comfort-Luxury 2027", [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], "Comfort,Luxury", "COMFORT,LUXURY,Comfort,Luxury", 1, {"MARK_S": "1"},
  "VERSIONES del Jaecoo 5 EV 2027: Comfort y Luxury. En la ficha «S» significa de serie y «–» que no lo trae."),
 ("Eado Plus IDD", [2, 3, 5], "Luxury,Elite", "LUXURY,ELITE,Luxury,Elite", 1, {},
  "VERSIONES del Changan Eado Plus IDD (híbrido enchufable): Luxury y Elite. ■ en la ficha = lo trae."),
("Changan CS55 Plus Phev LUXURY", [10, 11, 12], "Luxury,Elite", "LUXURY,ELITE", 1, {},
  "VERSIONES del Changan CS55 Plus PHEV (híbrido enchufable 1.5L, transmisión DHT): Luxury y Elite. ■ en la ficha = lo trae."),
 ("DEEPAL-ficha-S05 (1)", [2, 3, 4, 5, 6, 7], "REEV,BEV", "REEV,BEV", 1, {},
  "VERSIONES del Deepal S05: REEV (autonomía extendida) y BEV (eléctrico). ■ en la ficha = lo trae."),
 ("DEEPAL-ficha- S7_2025_CUADRADO_2 (1)", [19, 20, 21, 22], "REEV,BEV", "REEV,BEV", 1, {},
  "VERSIONES del Deepal S7: REEV (autonomía extendida) y BEV (eléctrico)."),
 ("DEEPAL G318", [2, 3, 4, 5, 6], "G318", "G318", 1, {},
  "Deepal G318 REEV (una sola versión). ★ en la ficha = lo trae."),
 ("Changan Unit", [3, 4], "Evolution,Techno", "EVOLUTION,TECHNO", 1, {},
  "VERSIONES del Changan UNI-T: Evolution y Techno (motor 1.5L GDI turbo, 180 HP, 300 Nm, automática 7DCT)."),
 ("Eclipse Cross", [2], "4x2,4x4", "4x2,4x4,4X2,4X4", 2, {},
  "VERSIONES del Mitsubishi Eclipse Cross: 4x2 y 4x4 con S-AWC (1.5 Turbo MIVEC, 1499 cc, CVT)."),

("Nissan Kicks 2025", [14, 15], "Sense,Advance,Exclusive", "Sense,Advance,Exclusive", 1, {},
  "VERSIONES del Nissan Kicks (1.0 L Turbo, 999 cm3, 114 HP, caja DCT automática; Brasil): Sense, Advance y Exclusive. Sube de nivel en cada versión: Exclusive suma llantas R19, panel digital de 12,3\", cámara 360°, techo panorámico, cuero, 10 parlantes premium."),
 ("Nissan Magnite - 2025", [13], "Advance Manual,Advance Automático,Exclusive Manual,Exclusive Automático", "Advance,Exclusive,Manual,Automático", 1, {},
  "VERSIONES del Nissan Magnite (1.0 L Turbo 3 cilindros, nafta): Advance Manual (5 cambios, 99 HP), Advance Automático (CVT, 99 HP), Exclusive Manual y Exclusive Automático."),
 ("Versa 2024", [9], "Sense Manual,Advance Manual,Advance Automática,Exclusive Automática", "Sense,Advance,Exclusive,Manual,Automática", 1, {},
  "VERSIONES del Nissan Versa (1.6 L, 118 HP, 149 Nm): Sense Manual, Advance Manual, Advance Automática (CVT) y Exclusive Automática."),

("LEAPMOTOR_FOLLETO_B10", [23], "Life,Design", "LIFE,DESIGN,B10", 1, {},
  "VERSIONES del Leapmotor B10 EV: LIFE (batería 56,2 kWh, 361 km WLTP, 160 kW) y DESIGN (67,1 kWh, 434 km WLTP). Los datos técnicos (dimensiones, motor, autonomía) están en el texto de la página 22 en el orden Life y luego Design."),
 ("leapmotor-c10- NUEVA", [5, 6], "BEV,REEV", "BEV,REEV,Comfort,Premium", 1, {},
  "VERSIONES del Leapmotor C10: BEV (eléctrico) y REEV (ultra-híbrido, autonomía extendida). • = lo trae; «-» = no."),
 ("Changan Hunter", [3, 4], "ambas versiones (REEV 4x2 y 4x4)", "REEV", 1, {},
  "Changan Hunter REEV (4x2 y 4x4): estas páginas listan el equipamiento común; ■ = lo trae."),

]
for pdf, pgs, nombres, claves, mit, env, manual in CFG:
    partes = []
    for pg in pgs:
        e = dict(os.environ); e.update(env)
        r = subprocess.run([sys.executable, "-I", os.path.join(T, "tabla2.py"), pdf + ".pdf", str(pg), nombres, str(mit), claves], capture_output=True, env=e)
        partes.append(f"[página {pg}]\n" + r.stdout.decode("utf-8", "replace"))
    open(os.path.join(V, pdf + ".txt"), "w", encoding="utf-8").write(f"# paginas: {','.join(map(str, pgs))}\n{manual}\n\nTABLAS (cada fila indica en qué versiones está el equipamiento):\n" + "\n".join(partes))
    print(pdf, sum(len(p) for p in partes))
