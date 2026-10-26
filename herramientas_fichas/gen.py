import subprocess, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
T = os.path.dirname(os.path.abspath(__file__))
V = r"C:\Users\fercu\Downloads\TODOS LOS PROYECTOS CLAUDE\VENTA DE VIDHUB\lista-precios-autostore\fichas_txt\_visual"
CFG = [
 ("Ficha tecnica H6 HEV y PHEV", 2, "HEV Elite,HEV Deluxe,PHEV Deluxe 2WD,PHEV Deluxe 4WD", "Elite,Deluxe",
  "VERSIONES: HEV 1.5T (Elite y Deluxe) y PHEV 1.5T (Deluxe 2WD y Deluxe 4WD). Dimensiones: largo 4703 mm, ancho 1886 mm, alto 1730 mm, distancia entre ejes 2738 mm. Las columnas de las tablas siguen ese orden."),
 ("Haval_H7_PHEV", 2, "H7 PHEV 2WD,H7 PHEV 4WD", "2WD,4WD",
  "ESPECIFICACIONES: combustible PHEV (híbrido enchufable), motor 1.5T. 2WD: transmisión DHT-1, 540 Nm / 240 kW, rendimiento mixto 6,0 L/100 km, neumáticos 18-265-60. 4WD: transmisión DHT-3, 760 Nm / 268 kW, rendimiento mixto 6,3 L/100 km, neumáticos 19-255-60. Dimensiones: largo 4800 mm, ancho 1950 mm, alto 1843 mm."),
 ("Poer Family", 2, "Diésel Luxury,Diésel Elite,Diésel Deluxe,Gasolina Elite,Gasolina Deluxe", "Luxury,Elite,Deluxe",
  "ESPECIFICACIONES: motor 2.0 Turbo. Diésel Common Rail VGT: 161 HP (3600 a 5500 rpm), torque 400 Nm (1500 a 2500 rpm). Gasolina: 190 HP (4000 a 5500 rpm), torque 360 Nm (1800 a 3600 rpm). Tracción 4x4, transmisión automática de 8 velocidades, tanque 80 L, carga con pasajeros 1050 kg, neumáticos 265/60 R18, dirección asistida eléctrica, frenos traseros de disco, suspensión delantera independiente de doble horquilla con barra estabilizadora, trasera eje rígido con paquete de resortes, piso de la caja pintado. Dimensiones: largo 5410 mm, ancho 1934 mm, alto 1886 mm, distancia entre ejes 3230 mm, despeje 227 mm. COLUMNAS de las tablas (orden de la ficha): los tres primeros son los diésel (Luxury, Elite, Deluxe) y los dos últimos los de gasolina (Elite, Deluxe)."),
 ("Poer Tool", 2, "Diésel 4x2,Diésel 4x4,Gasolina 4x2,Gasolina 4x4", "Elite",
  "ESPECIFICACIONES: motor 2.0 (Diésel common rail con VGT: 161 HP / 3600, 400 Nm / 1500-2500 rpm; Gasolina: 190 HP / 4000, 360 Nm / 1600-3600 rpm), transmisión manual de 6 velocidades, dirección asistida hidráulica, frenos de disco delanteros y tambor trasero, suspensión delantera independiente de doble horquilla con barra estabilizadora, trasera eje rígido con paquete de resortes, tanque 80 L, carga con pasajeros 1050 kg, neumáticos 245/70 R17. Dimensiones: largo 5425 mm, ancho 1886 mm, alto 1883 mm, distancia entre ejes 3230 mm, despeje 227 mm. COLUMNAS: Elite diésel 4x2, Elite diésel 4x4, Elite gasolina 4x2, Elite gasolina 4x4 (orden de la ficha)."),
 ("Haval Jolion Pro", 2, "Pro Elite HEV,Pro Deluxe HEV", "Elite,Deluxe", "VERSIONES: Haval Jolion Pro HEV Elite y Deluxe (híbrido autorrecargable, DHT, 1.5, 2WD, 188 HP combinados, 375 Nm, rendimiento mixto 19,6 km/L)."),
 ("Wingle 5", 2, "Cabina Simple Luxury,Doble Cabina Luxury,Doble Cabina Dignity", "Luxury,Dignity",
  "ESPECIFICACIONES: nafta, 2378 cc, 134 HP / 5150 rpm, torque 200 Nm / 2000-3000, manual 5 marchas, tracción 4x2, tanque 70 L, dimensiones 5095 x 1800 x 1730 mm, caja 1380 x 1460 x 480 mm, distancia entre ejes 3050 mm, despeje 194 mm, carga de la caja 675 kg, peso en vacío 2035 kg, peso bruto 2710 kg, carga con pasajeros 1050 kg. Suspensión delantera independiente de doble brazo, trasera eje rígido con ballestas, dirección asistida eléctricamente. COLUMNAS: Cabina Simple Luxury, Doble Cabina Luxury, Doble Cabina Dignity."),
 ("Wingle7", 2, "Luxury 4x2,Luxury 4x4", "Luxury",
  "ESPECIFICACIONES: motor GW4D20D, 2.0 L 4 cilindros en línea con TGV, diésel common-rail, 148 HP / 4000 rpm, torque 320 Nm / 1400-2800, caja manual de 6 marchas, caja de carga 1680 x 1460 x 480 mm, peso bruto 1880 kg (4x2) y 1920 kg (4x4), capacidad de carga de la caja 675 kg, con pasajeros 1050 kg, frenos de disco en las 4 ruedas. Dimensiones: largo 5350 mm, distancia entre ejes 3350 mm, despeje 213 mm, ancho 1750 mm, alto 2150 mm."),
]
for pdf, pg, nombres, claves, manual in CFG:
    r = subprocess.run([sys.executable, "-I", os.path.join(T, "tabla2.py"), pdf + ".pdf", str(pg), nombres, "2", claves], capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    open(os.path.join(V, pdf + ".txt"), "w", encoding="utf-8").write(f"# paginas: {pg}\n{manual}\n\nTABLAS (cada fila indica en qué versiones está el equipamiento):\n{out}")
    print(pdf, len(out), r.stderr.decode()[:100])
