import json, collections
D='/home/user/Web-catalogo-fremiotstudio3d/metrados/sketchup/'
d=json.load(open(D+'etapa1_modelo.json'))
COL={'02.01 Excavacion zapatas':(205,133,63,70),'02.02 Excavacion zanjas VE VC':(205,133,63,70),
'03.01 Solado':(150,150,150,255),'03.02 Cimiento corrido ciclopeo':(120,110,100,255),'03.03 Sobrecimiento':(170,170,140,255),
'04.01 Zapatas':(190,190,190,255),'04.02 Vigas de equilibrio VE':(110,140,190,255),'04.04 Tecnopor bajo VE':(250,250,250,255),
'04.05 Vigas de conexion VC':(90,170,120,255),'04.06 Columnas 1er piso':(90,90,90,255),'04.08 Cerco (ZC, CA, solera)':(120,120,160,255),
'05.01 Muro cerco':(214,110,60,255),'05.02 Muro perimetro vivienda':(214,110,60,255),'05.03 Junta tecnopor 1in':(255,255,120,255),
'04.09a Acero zapatas':(220,30,30,255),'04.09b Acero VE y VC':(220,30,30,255),'04.09c Acero columnas':(220,30,30,255)}
# --- agrupar barras por (tag, nombre) para no crear 1,700 grupos
grp=collections.OrderedDict()
for b in d['bars']:
    k=(b['tag'],b['name'].split(' ')[0]+' '+b['name'].split(' ')[-1] if False else b['name'])
    g=grp.setdefault((b['tag'],b['name']),dict(tag=b['tag'],name=b['name'],kg=collections.defaultdict(float),L=collections.defaultdict(float),n=collections.Counter(),polys=[]))
    w={'3/8':0.56,'1/2':0.994,'5/8':1.552,'3/4':2.235}[b['d']]
    g['kg'][b['d']]+=b['L']*w; g['L'][b['d']]+=b['L']; g['n'][b['d']]+=1; g['polys'].append(b['pts'])
bargroups=[dict(tag=g['tag'],name=g['name'],kg=dict(g['kg']),L=dict(g['L']),n=dict(g['n']),polys=g['polys']) for g in grp.values()]
data=json.dumps(dict(boxes=d['boxes'],bars=bargroups,colors=COL),separators=(',',':'))
rb=r'''# =====================================================================
# ETAPA 1 - Vivienda unifamiliar Chorrillos (E-01, E-02/E-03, E-04, E-10)
# Modelo de verificación de metrados para SketchUp (2017 o superior, escritorio)
#
# USO: Ventana > Consola Ruby  ->  load 'C:/ruta/etapa1_sketchup.rb'
#      (o arrastra este archivo a Extensiones > Extension Manager no; usa la consola)
#
# Crea una etiqueta (capa) por partida, con colores, y al final muestra el
# REPORTE DE METRADOS medido sobre el modelo: volúmenes (Entity Info), áreas de
# encofrado, m² de muro y kg de acero por diámetro.
# Origen: x = 0 lindero A, y = 0 frente de la vivienda (eje 1), z = 0 NTN ±0.00.
# =====================================================================
require 'json'
module Etapa1
  DATA_JSON = <<'JSONDATA'
__DATA__
JSONDATA

  def self.m(v); v.to_f.m; end

  def self.build
    data  = JSON.parse(DATA_JSON)
    model = Sketchup.active_model
    model.start_operation('Etapa 1 - modelo de metrados', true)
    ents  = model.active_entities
    root  = ents.add_group; root.name = 'ETAPA 1 - Metrados'
    layers = model.layers; mats = model.materials
    parents = {}
    get_parent = lambda do |tag|
      return parents[tag] if parents[tag]
      lay = layers[tag] || layers.add(tag)
      c = data['colors'][tag] || [200,200,200,255]
      lay.color = Sketchup::Color.new(c[0],c[1],c[2]) if lay.respond_to?(:color=)
      mat = mats[tag] || mats.add(tag)
      mat.color = Sketchup::Color.new(c[0],c[1],c[2]); mat.alpha = c[3]/255.0
      pg = root.entities.add_group; pg.name = tag; pg.layer = lay
      parents[tag] = [pg, lay, mat]
    end
    data['boxes'].each do |b|
      pg, lay, mat = get_parent.call(b['tag'])
      g = pg.entities.add_group; g.name = b['name']; g.layer = lay; g.material = mat
      p = [[b['x0'],b['y0']],[b['x1'],b['y0']],[b['x1'],b['y1']],[b['x0'],b['y1']]].map { |x,y| Geom::Point3d.new(m(x),m(y),m(b['z0'])) }
      f = g.entities.add_face(p); f.reverse! if f.normal.z < 0
      f.pushpull(m(b['z1']) - m(b['z0']))
      g.set_attribute('metrado','enc', b['enc'].to_s); g.set_attribute('metrado','axis', b['axis'].to_s)
    end
    data['bars'].each do |bg|
      pg, lay, mat = get_parent.call(bg['tag'])
      g = pg.entities.add_group; g.name = bg['name']; g.layer = lay
      bg['polys'].each { |pl| g.entities.add_edges(pl.map { |x,y,z| Geom::Point3d.new(m(x),m(y),m(z)) }) }
      bg['kg'].each { |dia,kg| g.set_attribute('acero', "kg #{dia}", kg) }
      bg['L'].each  { |dia,l|  g.set_attribute('acero', "L #{dia}", l) }
      bg['n'].each  { |dia,n|  g.set_attribute('acero', "n #{dia}", n) }
    end
    model.commit_operation
    model.active_view.zoom_extents
    report(root)
  end

  IN3_M3 = 61023.7441; IN2_M2 = 1550.0031
  def self.report(root)
    vol = Hash.new(0.0); area = Hash.new(0.0); kg = Hash.new { |h,k| h[k] = Hash.new(0.0) }
    root.entities.grep(Sketchup::Group).each do |pg|
      tag = pg.name
      pg.entities.grep(Sketchup::Group).each do |g|
        if g.attribute_dictionary('acero')
          g.attribute_dictionary('acero').each { |k,v| kg[tag][k.sub('kg ','')] += v if k.start_with?('kg ') }
          next
        end
        vol[tag] += g.volume / IN3_M3 if g.volume > 0
        enc = g.get_attribute('metrado','enc').to_s; ax = g.get_attribute('metrado','axis').to_s
        g.entities.grep(Sketchup::Face).each do |f|
          n = f.normal; a = f.area / IN2_M2
          next if n.z.abs > 0.9 && !(tag.include?('Tecnopor') || tag.include?('Solado'))
          if tag.include?('Tecnopor') || tag.include?('Solado')
            area[tag] += a if n.z > 0.9
          elsif enc == 'perimetro' then area[tag] += a
          elsif enc == 'lados'
            area[tag] += a if (ax == 'X' && n.y.abs > 0.9) || (ax == 'Y' && n.x.abs > 0.9)
          end
        end
        if enc == 'muro'
          bb = g.bounds; dx = bb.width.to_m; dy = bb.height.to_m; dz = bb.depth.to_m
          area[tag] += [dx,dy].max * dz
        end
      end
    end
    lines = ['REPORTE DE METRADOS MEDIDO EN EL MODELO (Etapa 1)', '']
    (vol.keys | area.keys).sort.each do |t|
      s = format('%-36s', t)
      s += format('  Vol: %8.2f m3', vol[t]) if vol[t] > 0
      s += format('  Area: %7.2f m2', area[t]) if area[t] > 0
      lines << s
    end
    lines << ''; tot = 0.0
    kg.keys.sort.each do |t|
      kg[t].keys.sort.each { |dia| lines << format('%-36s  Ø%-4s %8.1f kg', t, dia, kg[t][dia]); tot += kg[t][dia] }
    end
    lines << format('%-36s        %8.1f kg', 'ACERO MODELADO (sin cerco)', tot)
    lines << '' << 'Cerco: CA, ZC y cimiento corrido son referenciales (falta E-09). VA del cerco no modelada.'
    lines << 'Excavaciones: pozos con sobreancho 0.10 (no en lindero); zanjas solo entre pozos.'
    puts lines.join("\n"); UI.messagebox(lines.join("\n"), MB_MULTILINE, 'Metrados Etapa 1')
  end
end
Etapa1.build
'''
open(D+'etapa1_sketchup.rb','w',encoding='utf-8').write(rb.replace('__DATA__',data))

# ---------------- COLLADA (.dae) con las cajas (sin acero) ----------------
geo=[];nodes=[];mats=[];effs=[];seen={}
def mid(t):
    if t not in seen:
        i=len(seen); seen[t]=f'm{i}'; c=COL.get(t,(200,200,200,255))
        effs.append(f'<effect id="e{i}"><profile_COMMON><technique sid="c"><lambert><diffuse><color>{c[0]/255:.3f} {c[1]/255:.3f} {c[2]/255:.3f} 1</color></diffuse><transparency><float>{c[3]/255:.2f}</float></transparency></lambert></technique></profile_COMMON></effect>')
        mats.append(f'<material id="m{i}" name="{t}"><instance_effect url="#e{i}"/></material>')
    return seen[t]
bytag=collections.OrderedDict()
for j,b in enumerate(d['boxes']):
    x0,x1,y0,y1,z0,z1=b['x0'],b['x1'],b['y0'],b['y1'],b['z0'],b['z1']
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    tri=[0,2,1,0,3,2,4,5,6,4,6,7,0,1,5,0,5,4,1,2,6,1,6,5,2,3,7,2,7,6,3,0,4,3,4,7]
    m=mid(b['tag']); gid=f'g{j}'
    pos=' '.join(f'{a:.4f} {bb:.4f} {c:.4f}' for a,bb,c in v)
    geo.append(f'<geometry id="{gid}"><mesh><source id="{gid}p"><float_array id="{gid}a" count="24">{pos}</float_array><technique_common><accessor source="#{gid}a" count="8" stride="3"><param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/></accessor></technique_common></source><vertices id="{gid}v"><input semantic="POSITION" source="#{gid}p"/></vertices><triangles material="mat" count="12"><input semantic="VERTEX" source="#{gid}v" offset="0"/><p>{" ".join(map(str,tri))}</p></triangles></mesh></geometry>')
    bytag.setdefault(b['tag'],[]).append(f'<node name="{b["name"]}"><instance_geometry url="#{gid}"><bind_material><technique_common><instance_material symbol="mat" target="#{m}"/></technique_common></bind_material></instance_geometry></node>')
for t,ns in bytag.items(): nodes.append(f'<node name="{t}">{"".join(ns)}</node>')
dae=f'''<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1"><asset><unit name="meter" meter="1"/><up_axis>Z_UP</up_axis></asset>
<library_effects>{"".join(effs)}</library_effects><library_materials>{"".join(mats)}</library_materials>
<library_geometries>{"".join(geo)}</library_geometries>
<library_visual_scenes><visual_scene id="s"><node name="ETAPA 1 - Metrados">{"".join(nodes)}</node></visual_scene></library_visual_scenes><scene><instance_visual_scene url="#s"/></scene></COLLADA>'''
open(D+'etapa1_modelo.dae','w',encoding='utf-8').write(dae)
print('ok', len(data)//1024,'KB data')
