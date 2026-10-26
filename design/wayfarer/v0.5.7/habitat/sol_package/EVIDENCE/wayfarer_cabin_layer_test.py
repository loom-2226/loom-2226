exec(open('/tmp/wayfarer_cabin_ray_probe.py').read().split('for label,x,r,a in')[0])
# Additional water ring at r=4.15..4.20 would be OUTSIDE pressure vessel. Instead model layer r=3.95..4.15 inside cabins; baseline occupancy conflicts require re-layout.
angles=[169,221,259,311,360,420]
origins=[]
for a in angles:
 for x in (6.55,7.55):
  rad=math.radians(a);origins.append((f'{a}@{x}',(x,3.05*math.cos(rad),3.05*math.sin(rad))))
for t in (0,.03,.05,.08,.1,.15):
 layer=B.Sector(5.9,8.2,4.15-t,4.15,0,360) if t else None
 sample=items+([(layer,1.,layer.bbox())] if layer else [])
 mins=[]
 for label,o in origins:
  v=min(ray_density(o,d,sample,.05,65) for d in dirs)
  mins.append(v)
 print('thickness_cm',int(t*100),'added_t',round(math.pi*(4.15**2-(4.15-t)**2)*2.3,2),'min',round(min(mins),1),'failing',sum(x<40 for x in mins),'per_bunk',[(origins[i][0],round(mins[i],1)) for i in range(len(mins))],flush=True)
