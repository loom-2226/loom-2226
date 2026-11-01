"""Metric scale Option C axial/radial section; SVG coordinates x and r use identical px/metre.
The deeper accepted dome pair retains its rim; AOI illustrated at 12cm axial separation.
Gore depth is shown as an approximate 0.10m equivalent at 2,700kg/m3, NOT a structural proof.
"""
from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[1];G=ROOT/'results/out/wayfarer_v05_geometry.json'
h=hashlib.sha256(G.read_bytes()).hexdigest()
A=json.loads(G.read_text())['crown_option_c'];O=ROOT/'render/out/deck_crown_option_c_section.svg'
S=145.0; xmin=-1.8; rmin=-.2; ox=180; oy=810
def P(x,r):return (ox+(x-xmin)*S,oy-r*S)
def line(x1,r1,x2,r2,colour,width=2,dash=''):
 a,b=P(x1,r1);c,d=P(x2,r2)
 return f'<line x1="{a:.2f}" y1="{b:.2f}" x2="{c:.2f}" y2="{d:.2f}" stroke="{colour}" stroke-width="{width}" '+(f'stroke-dasharray="{dash}" ' if dash else '')+'/>'
def poly(coords,col,width=2,fill='none',dash=''):
 xy=' '.join(f'{P(x,r)[0]:.2f},{P(x,r)[1]:.2f}' for x,r in coords)
 return f'<polyline points="{xy}" fill="{fill}" stroke="{col}" stroke-width="{width}" '+(f'stroke-dasharray="{dash}" ' if dash else '')+'/>'
def txt(x,y,val,size=18,col='#dce8f1',weight=400):
 return f'<text x="{x}" y="{y}" font-family="system-ui,Arial" font-weight="{weight}" font-size="{size}" fill="{col}">{val}</text>'
def outer(r):
 if r<=2:return -1.2
 if r<=3.5:return -1.2+(r-2)*math.tan(math.radians(50))
 t=min(1,(r-3.5));e=-1.2+1.5*math.tan(math.radians(50))
 return e+(2.35-e)*t*t*(3-2*t)
DP=A["deep_pressure_domes"]
def inner(r):return DP["parent_base_x_m"]-DP["parent_depth_m"]*math.sqrt(max(0,1-(r/DP["parent_radius_m"])**2))
def rev(r):return 2.35-2.35*math.sqrt(max(0,1-(r/4.5)**2))
r0=[i*4.5/180 for i in range(181)]
r1=[i*3.5/140 for i in range(141)]
z=['<svg xmlns="http://www.w3.org/2000/svg" width="1560" height="1050" viewBox="0 0 1560 1050">',
'<rect width="1560" height="1050" fill="#101923"/>',
txt(40,45,'WAYFARER OPTION C · TRUE-SCALE CROWN SECTION',28,'#f6f9fc',700),
txt(42,77,'Axial x (m) → aft    ·    radial r (m) ↑    ·    both axes 145 px / metre',18,'#b8d1e5'),
txt(42,105,'Outer panes / AOI / independently pressure-rated primary + backup domes / gores / L1 floor',17,'#b8d1e5'),
line(xmin,0,3.55,0,'#607285',2),line(0,-.15,0,4.6,'#607285',2)]
for x in [-1.2,0,1,2,3]:
 a,b=P(x,0);z.extend([line(x,-.08,x,.08,'#8199a9',2),txt(a-21,b+28,f'{x:g}',14)])
for r in range(0,5):
 x,y=P(xmin,r);z.extend([line(xmin,r,xmin+.09,r,'#8199a9'),txt(x-28,y+5,str(r),15)])
# Original Rev7 comparison, source true envelope, no new shell material here.
z.append(poly([(rev(r),r) for r in r0],'#718295',2,dash='8 9'))
# AOI fill between domes exact physical 0.12m axial envelope. Not a pressure seal.
xy=' '.join(f'{P(inner(r)-.12,r)[0]:.2f},{P(inner(r)-.12,r)[1]:.2f}' for r in r1)+ ' '+' '.join(f'{P(inner(r),r)[0]:.2f},{P(inner(r),r)[1]:.2f}' for r in reversed(r1))
z.append(f'<polygon points="{xy}" fill="#7cc0bb" fill-opacity=".48" stroke="none"/>')
z.append(poly([(inner(r)-.12,r) for r in r1],'#c4faff',3))
z.append(poly([(inner(r),r) for r in r1],'#f6e2a5',3))
# Distinct 1cm outer layer shown at true thickness (1.45px) and gore 27 g/cm2 /2.7t/m3 ~10cm.
z.append(poly([(outer(r),r) for r in r0],'#7ec6ed',2.3))
z.append(poly([(outer(r)-.1,r) for r in r0],'#f49d68',2.5,dash='5 5'))
for r in [0,.75,2,2.75,3.5]:
 x=outer(r);a,b=P(x,r);z.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="5" fill="#ffffff"/>')
 z.append(txt(a+9,b-9,f'r={r:g}',14,'#def2f8'))
# L1 physical deck and cabin region
z.append(line(3,0,3,4.15,'#b9bec4',7))
z.append(txt(*P(3.05,1.2),'L1 FLOOR',15,'#ffffff'))
z.append(txt(*P(2.15,3.75),'PRESSURISED L1',16,'#ffebba'))
# labels with leaders
for x,y,ex,er,textv,color in [
 (1000,275,outer(2.5),2.5,'1 cm outer replaceable dust/debris tiles','#7ec6ed'),
 (1000,320,outer(2.2)-.1,2.2,'CLOSED: Strata 27 g/cm², 16 gores','#f49d68'),
 (1000,375,inner(2.5)-.12,2.5,'Backup seamless pressure dome 28 mm','#c4faff'),
 (1000,420,inner(2.15),2.15,'Primary seamless pressure dome 28 mm','#f6e2a5'),
 (1000,465,inner(1.85)-.06,1.85,'AOI ~3 t, nominal 12 cm axial span','#7cc0bb'),
 (1000,515,outer(2),2,'r=2.0 m flat-to-50° break','#ffffff')]:
 px,py=P(ex,er);z.append(f'<path d="M{x-16},{y-5} L{px:.2f},{py:.2f}" fill="none" stroke="{color}" stroke-width="1.2"/>')
 z.append(txt(x,y,textv,17,color))
z.extend([txt(990,590,'Rev7 bow is the grey dashed comparator.',17,'#a8bacb'),txt(990,625,'External surface: 52.888 m². Closed Strata: 14.280 t gross.',17),
 txt(990,660,'Added armour mass: 3.889 t beyond existing credited coverage.',16),
 txt(990,695,'Outer projected rings [0, .75, 2, 2.75, 3.5]; outer band π/12.',16),
 txt(990,730,'Four tile types; seven spares; outward retainer concept.',16),
 txt(990,765,'Crown OPEN only under default bow/dust-flow doctrine.',16),
 txt(990,825,'HOLD: 7 m ceramic, AOI isolation, seals, gores, impact protection.',16,'#f4c1a5'),
 txt(35,997,'VISUAL SECTION ONLY: 1:1 x/r scale, no perspective. 0.10 m gore material equivalent assumes 2,700 kg/m³ for drawing.',14,'#9eb3c5'),
 txt(35,1025,'SHA256 '+h+' · ALL bodies. ALL sponsors. 2026–2226. · DRAFT ENGINEERING',14,'#aabccc'),'</svg>'])
O.write_text('\n'.join(z))
print('CROWN_SECTION',O,h,'size',O.stat().st_size)
