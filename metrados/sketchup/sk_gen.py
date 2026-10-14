# Genera el modelo de la Etapa 1: script Ruby para SketchUp + DAE + datos de verificación
import math, json
OUT='/home/user/Web-catalogo-fremiotstudio3d/metrados/sketchup/'
LX,LY=7.90,15.00   # lote vivienda: x=0 lindero A, x=7.90 lindero C, y=0 frente vivienda (eje 1), y=15 fondo
boxes=[]   # dict(name,tag,x0,x1,y0,y1,z0,z1,enc,axis,info)
bars=[]    # dict(tag,diam,L,pts,name)
def box(name,tag,x0,x1,y0,y1,z0,z1,enc=None,axis=None):
    boxes.append(dict(name=name,tag=tag,x0=round(x0,4),x1=round(x1,4),y0=round(y0,4),y1=round(y1,4),z0=round(z0,4),z1=round(z1,4),enc=enc,axis=axis))
def bar(tag,diam,L,pts,name=''):
    bars.append(dict(tag=tag,d=diam,L=round(L,3),pts=[[round(c,4) for c in p] for p in pts],name=name))
def sub(iv,cuts):
    """intervalo iv=(a,b) menos lista de intervalos cuts"""
    res=[iv]
    for c0,c1 in cuts:
        nr=[]
        for a,b in res:
            if c1<=a or c0>=b: nr.append((a,b)); continue
            if c0>a: nr.append((a,c0))
            if c1<b: nr.append((c1,b))
        res=nr
    return [(a,b) for a,b in res if b-a>1e-4]

# ---------------- ZAPATAS (E-01) ----------------
Z={'A1':('Z-5',0,1.55,0,1.70),'C1':('Z-5',6.35,7.90,0,1.70),'A5':('Z-5',0,1.55,13.30,15.00),'C5':('Z-5',6.35,7.90,13.30,15.00),
   'B1':('Z-4',3.095,5.195,0,1.40),'B5':('Z-4',3.095,5.195,13.60,15.00),
   'A2':('Z-3',0,1.40,3.65,5.85),'C2':('Z-3',6.50,7.90,3.65,5.85),
   'A3':('Z-4',0,1.40,6.88,8.98),'A4':('Z-4',0,1.40,10.06,12.16),'C3':('Z-4',6.50,7.90,6.88,8.98),'C4':('Z-4',6.50,7.90,10.06,12.16),
   'B2':('Z-1',3.045,5.245,3.65,5.85),'B3':('Z-2',3.17,5.12,6.955,8.905),'B4':('Z-2',3.17,5.12,10.135,12.085)}
ZBAR={'Z-1':(11,2.45,11,2.45),'Z-2':(10,2.20,10,2.20),'Z-3':(11,1.65,7,2.45),'Z-4':(10,1.65,7,2.35),'Z-5':(8,1.80,8,1.95)}
for k,(t,x0,x1,y0,y1) in Z.items():
    box(f'{t} {k}','04.01 Zapatas',x0,x1,y0,y1,-1.50,-1.00)
    box(f'Solado {k}','03.01 Solado',x0,x1,y0,y1,-1.60,-1.50)
    # parrilla: barras a lo largo de X (cantidad n1? se ubica según el lado corto/largo del cuadro)
    n1,l1,n2,l2=ZBAR[t]; B=x1-x0; L=y1-y0
    # barras de longitud (B-0.15+0.40) van en X; las de (L-0.15+0.40) van en Y
    cands=[(n1,l1),(n2,l2)]
    nx,lx=min(cands,key=lambda c:abs(c[1]-(B-0.15+0.40))); ny,ly=[c for c in cands if c!=(nx,lx)][0] if cands[0]!=cands[1] else (n2,l2)
    zb=-1.50+0.075+0.008; c=0.075
    for i in range(nx):
        y=y0+c+(L-2*c)*i/max(nx-1,1)
        bar('04.09a Acero zapatas','5/8',lx,[(x0+c,y,zb+0.20),(x0+c,y,zb),(x1-c,y,zb),(x1-c,y,zb+0.20)],f'Parrilla {k}')
    for i in range(ny):
        x=x0+c+(B-2*c)*i/max(ny-1,1)
        bar('04.09a Acero zapatas','5/8',ly,[(x,y0+c,zb+0.216),(x,y0+c,zb+0.016),(x,y1-c,zb+0.016),(x,y1-c,zb+0.216)],f'Parrilla {k}')

# ---------------- COLUMNAS (E-04), -1.00 a +2.30 ----------------
C={'A1':('C-1',0,0.30,0,0.50),'A2':('C-2',0,0.30,4.50,5.00),'A3':('C-2',0,0.30,7.68,8.18),'A4':('C-2',0,0.30,10.86,11.36),'A5':('C-1',0,0.30,14.50,15.00),
   'C1':('C-1',7.60,7.90,0,0.50),'C2':('C-2',7.60,7.90,4.50,5.00),'C3':('C-2',7.60,7.90,7.68,8.18),'C4':('C-2',7.60,7.90,10.86,11.36),'C5':('C-1',7.60,7.90,14.50,15.00),
   'B1':('C-3',3.845,4.445,0,0.30),'B2':('C-4',3.845,4.445,4.575,4.925),'B3':('C-4',3.845,4.445,7.755,8.105),'B4':('C-4',3.845,4.445,10.935,11.285),'B5':('C-3',3.845,4.445,14.70,15.00)}
EST={'C-1':(1.48,0.42),'C-2':(1.48,0.42),'C-3':(1.68,0.99),'C-4':(1.78,1.26)}
def colbars(t,x0,x1,y0,y1):
    cv=0.06; pts=[]
    if t in('C-1','C-2'):   # 0.30 (X) x 0.50 (Y): 3 barras en caras de 0.30, 1 al centro en caras de 0.50
        for y in (y0+cv,y1-cv):
            for x in (x0+cv,(x0+x1)/2,x1-cv): pts.append((x,y))
        for x in (x0+cv,x1-cv): pts.append((x,(y0+y1)/2))
    else:
        n=4 if t=='C-3' else 5
        for y in (y0+cv,y1-cv):
            for i in range(n): pts.append((x0+cv+(x1-x0-2*cv)*i/(n-1),y))
        for x in (x0+cv,x1-cv): pts.append((x,(y0+y1)/2))
    return pts
zst=[-1.00+0.05+0.075*i for i in range(9)]
zst+= [2.30-0.05-0.075*i for i in range(9)]
mid0,mid1=-1.00+0.65,2.30-0.65; nmid=math.ceil((mid1-mid0)/0.09)
zst+=[mid0+(mid1-mid0)*(i+0.5)/nmid for i in range(nmid)]
NEST=len(zst)
for k,(t,x0,x1,y0,y1) in C.items():
    box(f'{t} {k}','04.06 Columnas 1er piso',x0,x1,y0,y1,-1.00,2.30,enc='perimetro')
    for (x,y) in colbars(t,x0,x1,y0,y1):
        zb=-1.393; bar('04.09c Acero columnas','5/8',6.00,[(x+0.2*(1 if x<(x0+x1)/2 else -1),y,zb),(x,y,zb),(x,y,zb+5.80)],f'Arranque {k}')
    le,li=EST[t]; r=0.04
    for z in zst:
        bar('04.09c Acero columnas','1/2',le+li,[(x0+r,y0+r,z),(x1-r,y0+r,z),(x1-r,y1-r,z),(x0+r,y1-r,z),(x0+r,y0+r,z)],f'Estribo {k}')
    for z in (-1.40,-1.25,-1.10):
        bar('04.09c Acero columnas','3/8',2*((x1-x0)+(y1-y0))-8*r+0.15,[(x0+r,y0+r,z),(x1-r,y0+r,z),(x1-r,y1-r,z),(x0+r,y1-r,z),(x0+r,y0+r,z)],f'Montaje {k}')

# ---------------- VIGAS DE CIMENTACIÓN (E-02/E-03): VE -1.00 a -0.30; VC -1.50 a -1.10 ----------------
# (nombre, tipo, eje dir, inicio, fin, c0, c1, L barra, N estribos)
V=[('VE-2a','VE-2','X',0.30,3.845,0,0.30,5.05,24),('VE-2b','VE-2','X',4.445,7.60,0,0.30,4.65,22),
   ('VE-1a','VE-1','X',0.30,3.845,4.60,4.90,5.05,24),('VE-1b','VE-1','X',4.445,7.60,4.60,4.90,4.65,22),
   ('VE-2c','VE-2','X',0.30,3.845,7.78,8.08,5.05,24),('VE-2d','VE-2','X',4.445,7.60,7.78,8.08,4.65,22),
   ('VE-2e','VE-2','X',0.30,3.845,10.96,11.26,5.05,24),('VE-2f','VE-2','X',4.445,7.60,10.96,11.26,4.65,22),
   ('VE-2g','VE-2','X',0.30,3.845,14.70,15.00,5.05,24),('VE-2h','VE-2','X',4.445,7.60,14.70,15.00,4.65,22),
   ('VE-2i','VE-2','Y',0.50,4.50,0,0.30,5.50,27),('VCa','VC','Y',5.00,7.68,0.025,0.275,3.98,14),('VCb','VC','Y',8.18,10.86,0.025,0.275,3.98,14),('VE-2j','VE-2','Y',11.36,14.50,0,0.30,4.64,22),
   ('VE-2k','VE-2','Y',0.50,4.50,7.60,7.90,5.50,27),('VCc','VC','Y',5.00,7.68,7.625,7.875,3.98,14),('VCd','VC','Y',8.18,10.86,7.625,7.875,3.98,14),('VE-2l','VE-2','Y',11.36,14.50,7.60,7.90,4.64,22),
   ('VE-1c','VE-1','Y',0.30,4.575,3.995,4.295,5.78,29),('VCe','VC','Y',4.925,7.755,4.02,4.27,4.13,15),('VCf','VC','Y',8.105,10.935,4.02,4.27,4.13,15),('VE-1d','VE-1','Y',11.285,14.70,3.995,4.295,4.91,24)]
NBAR={'VE-1':(4,1),'VE-2':(3,1),'VC':(0,3)}   # por cara: n Ø3/4, n Ø5/8
def zap_cuts(axis,c0,c1,pad=0.0):
    cuts=[]
    for k,(t,x0,x1,y0,y1) in Z.items():
        if axis=='X':
            if y1>c0 and y0<c1: cuts.append((x0-pad,x1+pad))
        else:
            if x1>c0 and x0<c1: cuts.append((y0-pad,y1+pad))
    return cuts
def mk(axis,a,b,c0,c1,z0,z1,name,tag,enc=None):
    if axis=='X': box(name,tag,a,b,c0,c1,z0,z1,enc,axis)
    else: box(name,tag,c0,c1,a,b,z0,z1,enc,axis)
def P(axis,s,c,z): return (s,c,z) if axis=='X' else (c,s,z)
for nm,t,ax,a,b,c0,c1,lb,ne in V:
    ve=t!='VC'; z0,z1=(-1.50,-0.80) if ve else (-1.50,-1.10)
    if ve:
        cuts=zap_cuts(ax,c0,c1)
        for s0,s1 in sub((a,b),cuts): mk(ax,s0,s1,c0,c1,z0,z1,f'{nm} ({t}) entre zapatas','04.02 Vigas de equilibrio VE','lados')
        for s0,s1 in [(max(a,k0),min(b,k1)) for k0,k1 in cuts if min(b,k1)>max(a,k0)]:
            mk(ax,s0,s1,c0,c1,-1.00,z1,f'{nm} ({t}) sobre zapata','04.02 Vigas de equilibrio VE','lados')
    else:
        for s0,s1 in sub((a,b),zap_cuts(ax,c0,c1)): mk(ax,s0,s1,c0,c1,z0,z1,f'{nm} (VC, fuera de zapata)','04.05 Vigas de conexion VC','lados')
    if ve:
        for s0,s1 in sub((a,b),zap_cuts(ax,c0,c1)):
            mk(ax,s0,s1,c0,c1,-1.60,-1.50,f'Tecnopor {nm}','04.04 Tecnopor bajo VE')
    # acero longitudinal
    n34,n58=NBAR[t]; n=n34+n58; h=0.45 if ve else 0.35; L=b-a; ext=(lb-L-2*h)/2
    cv=0.05+0.0095+0.005
    for face,zf,sg in (('sup',z1-cv,-1),('inf',z0+cv,1)):
        for i in range(n):
            cc=c0+cv+(c1-c0-2*cv)*i/(n-1)
            d='3/4' if i<n34 and not (n58==1 and i==n//2) else '5/8'
            if n58==1: d='5/8' if i==n//2 else '3/4'
            if t=='VC': d='5/8'
            sA,sB=a-ext,b+ext
            bar('04.09b Acero VE y VC',d,lb,[P(ax,sA,cc,zf+sg*h),P(ax,sA,cc,zf),P(ax,sB,cc,zf),P(ax,sB,cc,zf+sg*h)],f'{nm} {face}')
    # estribos 3/8
    le=1.93 if ve else 1.18; r=0.05
    for i in range(ne):
        s=a+0.05+(L-0.10)*i/max(ne-1,1)
        q=[P(ax,s,c0+r,z0+r),P(ax,s,c1-r,z0+r),P(ax,s,c1-r,z1-r),P(ax,s,c0+r,z1-r),P(ax,s,c0+r,z0+r)]
        bar('04.09b Acero VE y VC','3/8',le,q,f'Estribo {nm}')

# ---------------- SOBRECIMIENTO + MUROS + JUNTAS (vivienda) ----------------
walls=[('A','Y',0,0.15,[(0.50,4.50,'VE'),(5.00,7.68,'VC'),(8.18,10.86,'VC'),(11.36,14.50,'VE')]),
       ('C','Y',7.75,7.90,[(0.50,4.50,'VE'),(5.00,7.68,'VC'),(8.18,10.86,'VC'),(11.36,14.50,'VE')]),
       ('5','X',14.85,15.00,[(0.30,3.845,'VE'),(4.445,7.60,'VE')])]
for eje,ax,c0,c1,segs in walls:
    for a,b,sup in segs:
        if sup=='VE': mk(ax,a,b,c0,c1,-0.80,0.20,f'Sobrecimiento eje {eje}','03.03 Sobrecimiento','lados')
        else:
            cuts=zap_cuts(ax,c0,c1)
            for s0,s1 in sub((a,b),cuts): mk(ax,s0,s1,c0,c1,-1.10,0.20,f'Sobrecimiento eje {eje} sobre VC','03.03 Sobrecimiento','lados')
            for z0_,z1_ in [(max(a,k0),min(b,k1)) for k0,k1 in cuts if min(b,k1)>max(a,k0)]:
                mk(ax,z0_,z1_,c0,c1,-1.00,0.20,f'Sobrecimiento eje {eje} sobre zapata','03.03 Sobrecimiento','lados')
        t0=c0 if eje!='C' else 7.77; t1=t0+0.13 if eje!='C' else 7.90
        if eje=='5': t0,t1=14.87,15.00
        if eje in ('A','C'):   # albañilería confinada: muro endentado contra las columnas, sin junta
            mk(ax,a,b,t0,t1,0.20,2.30,f'Muro portante eje {eje}','05.02a Muro portante linderos (KK portante)','muro')
        else:                  # fondo: tabique con junta de 1"
            mk(ax,a+0.025,b-0.025,t0,t1,0.20,2.30,f'Tabique eje {eje}','05.02b Muro fondo (tabique KK 18h)','muro')
            for s_ in (a,b-0.025): mk(ax,s_,s_+0.025,t0,t1,0.20,2.30,f'Junta eje {eje}','05.03 Junta tecnopor 1in')

# ---------------- CERCO DELANTERO (E-10; E-09 no recibido: CA, ZC y cimiento referenciales) ----------------
def cerco(side,x0,x1,elems,first_h):
    y=0.0
    for kind,w in elems:
        ya,yb=y-w,y
        if kind=='P':
            ztop=first_h if (yb==0.0 and first_h) else 2.80
            mk('Y',ya,yb,x0 if side=='A' else x1-0.13,(x0+0.13) if side=='A' else x1,0.20,ztop,f'Muro cerco {side}','05.01 Muro cerco','muro')
            mk('Y',ya,yb,x0 if side=='A' else x1-0.15,(x0+0.15) if side=='A' else x1,-0.20,0.20,f'Sobrecimiento cerco {side}','03.03 Sobrecimiento','lados')
            mk('Y',ya,yb,x0 if side=='A' else x1-0.15,(x0+0.15) if side=='A' else x1,2.80,3.00,f'Solera cerco {side}','04.08 Cerco (ZC, CA, solera)')
        else:
            mk('Y',ya,yb,x0 if side=='A' else x1-0.15,(x0+0.15) if side=='A' else x1,-0.60,3.00,f'{kind} cerco {side}','04.08 Cerco (ZC, CA, solera)','perimetro')
            cy=(ya+yb)/2
            mk('Y',cy-0.50,cy+0.50,x0 if side=='A' else x1-0.80,(x0+0.80) if side=='A' else x1,-1.00,-0.60,f'ZC cerco {side}','04.08 Cerco (ZC, CA, solera)')
            mk('Y',cy-0.50,cy+0.50,x0 if side=='A' else x1-0.80,(x0+0.80) if side=='A' else x1,-1.05,-1.00,f'Solado ZC {side}','03.01 Solado')
        y=ya
    # cimiento corrido ciclópeo entre ZC
    zcs=[(b['y0'],b['y1']) for b in boxes if b['name']==f'ZC cerco {side}']
    for s0,s1 in sub((y,0.0),zcs):
        mk('Y',s0,s1,x0 if side=='A' else x1-0.40,(x0+0.40) if side=='A' else x1,-0.80,-0.20,f'Cimiento corrido {side}','03.02 Cimiento corrido ciclopeo')
cerco('A',0,0.15,[('P',1.20),('CA-1',0.15),('P',1.69),('CA-2',0.25),('P',2.95)],2.275)
cerco('C',7.75,7.90,[('P',1.20),('CA-1',0.15),('P',1.69),('CA-1',0.15),('P',3.05)],None)

# ---------------- EXCAVACIÓN (sólidos transparentes) ----------------
def pit(x0,x1,y0,y1,s=0.10):
    return (x0 if x0<=0.001 else x0-s, x1 if x1>=LX-0.001 else x1+s, y0 if y0<=0.001 else y0-s, y1 if y1>=LY-0.001 else y1+s)
pits={k:pit(*v[1:]) for k,v in Z.items()}
for k,(x0,x1,y0,y1) in pits.items(): box(f'Pozo {k}','02.01 Excavacion zapatas',x0,x1,y0,y1,-1.60,0.0)
for nm,t,ax,a,b,c0,c1,lb,ne in V:
    ve=t!='VC'; w=0.70 if ve else 0.55; d=-1.60 if ve else -1.50
    cm=(c0+c1)/2; t0,t1=cm-w/2,cm+w/2
    lim=LX if ax=='Y' else LY
    if t0<0: t0,t1=0,w
    if t1>lim: t0,t1=lim-w,lim
    cuts=[]
    for k,(x0,x1,y0,y1) in pits.items():
        if ax=='X' and y1>t0 and y0<t1: cuts.append((x0,x1))
        if ax=='Y' and x1>t0 and x0<t1: cuts.append((y0,y1))
    for s0,s1 in sub((a,b),cuts): mk(ax,s0,s1,t0,t1,d,0.0,f'Zanja {nm}','02.02 Excavacion zanjas VE VC')

json.dump(dict(boxes=boxes,bars=bars),open(OUT+'etapa1_modelo.json','w'))
print(len(boxes),'cajas',len(bars),'barras',NEST,'estribos por columna')
