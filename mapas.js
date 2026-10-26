// Mapas modelo → foto y modelo → ficha PDF. Cada regla: [regex sobre «MARCA MODELO VERSIÓN» en mayúsculas, archivo, ilustrativa?]. Gana la primera que coincide.
// Formato JSON (las barras invertidas se escriben dobles). Lo leen index.html y generar_datos.py.
window.MAPAS = {
"fotos": [
["OUTLANDER","outlander.webp"],["ECLIPSE","eclipse.webp"],["DESTINATOR","destinator.webp"],["L200","l200.webp"],
["JOLION.*(HEV|PRO)","jolionhev.jpg"],["JOLION","jolion.webp"],["H6 GT","h6gt.jpg"],["HAVAL H6","h6.webp"],["H7","h7.jpg"],["TANK","tank300.webp"],
["ORA 5","ora5.jpg"],["ORA 03","ora03.jpg"],["WINGLE 7","wingle7.jpg"],["WINGLE","wingle5.jpg"],["POER FAMILY","poerfamily.jpg"],["POER","poer.webp"],
["CS55","cs55.webp"],["HUNTER","hunter.webp"],["EADO","eado.jpg"],["UNI-T","unit.webp"],["LUMIN","lumin.jpg"],
["G318","g318.jpg"],["DEEPAL.*\\bS7\\b","s7.webp"],["DEEPAL.*\\bS5\\b","s5.jpg"],
["OMODA E5","omodae5.jpg"],["OMODA 5","omoda5.webp"],["JAECOO 5","jaecoo5.jpg"],["JAECOO 6","jaecoo6.jpg"],["JAECOO 7","jaecoo7.webp"],
["B10","b10.jpg"],["C10","c10.jpg"],["C16","c16.jpg"],
["ZEEKR 001","zeekr001.jpg"],["ZEEKR 7X","zeekr7x.jpg"],["ZEEKR X ","zeekrx.jpg"],["XPENG G9","g9.jpg"],["XPENG G6|G6 ","g6.jpg"],
["SENTRA 2026","sentra19.jpg"],["SENTRA","sentra19.jpg",1],["KICKS","kicks.jpg"],["MAGNITE","magnite.jpg"],["VERSA","versa.jpg"],
["E-POWER EXCLUSIVE","xtrailexc.jpg"],["X-TRAIL","xtrail.jpg"],["QASHQAI","qashqai.jpg"],["PHATFINDER|PATHFINDER","pathfinder.jpg"],["FRONTIER","frontier.jpg",1],
["V6E","farizon.jpg"],["SUPERVAN","farizonsuper.jpg"],["JMC JMEV JMEV 2","jmev.jpg"],["JMC JMEV JMEV 3","jmev.jpg",1],
["GRAND AVENUE.*(LUXURY|OFF ROAD)","gapro.jpg"],["GRAND AVENUE","gapro.jpg",1],["L536","touring.jpg"],
["N822 2850 DC","n822dc.jpg"],["N822 2850 CHASIS","n822chasis.jpg"],["N822 2850 CAJA","n822caja.jpg"],["N822 VOLCADORA|N720 VOLCADORA","n822volc.jpg"],
["N822.*WIDE|WIDE","n822wide.jpg"],["N822 3360","n822medium.jpg"],["N822 3815","n822caja.jpg",1],["WORKSHOP","workshop.jpg"],["N720|NHR|N800","n822caja.jpg",1],
["S-WAY|STRALIS","sway.jpg"],["MINIBUS","dailyminibus.jpg"],["FURGÓN","dailyfurgon.jpg"],["CHASIS CABINA","dailychasis.jpg"],["IVECO","tector.jpg",1]
],
"fichas": [
["JOLION.*(HEV|PRO)","Haval Jolion Pro.pdf"],["JOLION","Haval Jolion Nafta.pdf"],["H6 GT",null],["HAVAL H6","Ficha tecnica H6 HEV y PHEV.pdf"],
["H7","Haval_H7_PHEV.pdf"],["ORA 5","GWM ORA5.pdf"],["ORA 03","Ora 03.pdf"],["WINGLE 7","Wingle7.pdf"],["WINGLE","Wingle 5.pdf"],
["POER TOOL","Poer Tool.pdf"],["POER FAMILY","Poer Family.pdf"],
["CS55","Changan CS55 Plus Phev LUXURY.pdf"],["HUNTER","Changan Hunter.pdf"],["EADO","Eado Plus IDD.pdf"],["UNI-T","Changan Unit.pdf"],["LUMIN","Brochure Changan Lumin (2).pdf"],
["G318","DEEPAL G318.pdf"],["DEEPAL.*\\bS7\\b","DEEPAL-ficha- S7_2025_CUADRADO_2 (1).pdf"],["DEEPAL.*\\bS5\\b","DEEPAL-ficha-S05 (1).pdf"],
["OMODA E5","Omoda E5 modelos 2027.pdf"],["OMODA 5","Omoda 5 Super Hybrid System (SHS).pdf"],
["JAECOO 5","Jaecoo5 Comfort-Luxury 2027.pdf"],["JAECOO 6","JAECOO 6.pdf"],["JAECOO 7","Jaecoo7 PHEV.pdf"],
["B10","LEAPMOTOR_FOLLETO_B10.pdf"],["C10","leapmotor-c10- NUEVA.pdf"],["C16","Ficha Leapmotor C16 REEV - Abril 2026.pdf"],
["ECLIPSE","Eclipse Cross.pdf"],["OUTLANDER","Outlander.pdf"],["L200","Mitsubishi-L200- FICHA NUEVA.pdf"],
["ZEEKR X ","X Smart.pdf"],["XPENG G6|G6 ","XPENG G6.pdf"],["V6E","Farizon Van V6E.pdf"],
["KICKS","Nissan Kicks 2025.pdf"],["MAGNITE","Nissan Magnite - 2025.pdf"],["VERSA","Versa 2024.pdf"],["FRONTIER","CATALOGO FRONTIER - TODOS LOS MODELOS.pdf"]
]
};
