
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'l2_organic_study'))
import l3geom,raster,sys,geom
geom.MAT['linen']=('#EFE9DD',0); raster.X0F=8.2; raster.COVE=(3.82,2.25); raster.WASH=(4.02,0.10)
l3geom.build(); T=l3geom.by_material(); W=geom.W
v=sys.argv[1]
V={'guest':(W(1.95,195,1.6),W(3.9,193,0.75),84),'capt':(W(1.95,45,1.6),W(3.8,24,0.8),84),'crewb':(W(1.95,285,1.6),W(3.8,272,0.8),84),'corr':(W(1.6,60,1.6),W(1.7,120,1.2),80)}
e,t,f=V[v]; raster.render(T,geom.MAT,e,t,f,out=f'l3_{v}.png')
