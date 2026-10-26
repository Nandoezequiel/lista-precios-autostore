import fitz,os,sys
# uso: render.py "ficha.pdf" pagina dpi [partes] ; guarda %TEMP%\fv\<tag>_p<N>_<k>.png
D=r"C:\Users\fercu\Downloads\TODOS LOS PROYECTOS CLAUDE\VENTA DE VIDHUB\lista-precios-autostore\fichas"
O=os.path.join(os.environ["TEMP"],"fv")
pdf,pg,dpi=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]); partes=int(sys.argv[4]) if len(sys.argv)>4 else 1
tag=sys.argv[5] if len(sys.argv)>5 else pdf[:10].replace(" ","_")
p=fitz.open(os.path.join(D,pdf))[pg-1]; r=p.rect
for k in range(partes):
    clip=fitz.Rect(r.x0,r.y0+r.height*k/partes,r.x1,r.y0+r.height*(k+1)/partes)
    f=os.path.join(O,f"{tag}_p{pg}_{k+1}.png"); p.get_pixmap(dpi=dpi,clip=clip).save(f); print(f)
