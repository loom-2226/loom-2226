
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'l2_organic_study'))
import l5geom,raster,sys,geom
l5geom.build(); T=l5geom.by_material(); W=geom.W
raster.X0F=13.4; raster.COVE=(3.87,2.25); raster.WASH=(4.10,0.10)
v=sys.argv[1]
V={'airlock':(W(2.05,-6,1.6),W(4.1,3,1.0),88),'suits':(W(2.0,52,1.6),W(3.7,45,1.1),86),'workshop':(W(1.95,125,1.6),W(3.9,125,0.9),86),'vestibule':(W(1.95,250,1.7),W(3.4,280,0.3),86)}
e,t,f=V[v]; raster.render(T,geom.MAT,e,t,f,out=f'l5_{v}.png')
