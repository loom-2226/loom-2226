
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'l2_organic_study'))
import l4geom,raster,sys,geom
l4geom.build(); T=l4geom.by_material(); W=geom.W
raster.X0F=10.8; raster.COVE=(3.87,2.25); raster.WASH=(4.10,0.10)
v=sys.argv[1]
V={'shelter':(W(2.35,30,1.45),W(3.4,105,0.75),88),'medical':(W(1.95,202,1.6),W(3.9,222,0.8),86),'eclss':(W(1.95,315,1.6),W(3.6,300,1.0),86)}
e,t,f=V[v]; raster.render(T,geom.MAT,e,t,f,out=f'l4_{v}.png')
