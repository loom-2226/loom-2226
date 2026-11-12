import geom,raster,math,sys
T=geom.build(); W=geom.W
which=sys.argv[1]
if which=='ward': raster.render(T,geom.MAT,W(1.85,40,1.6),W(3.6,100,0.6),76,out='ward.png')
if which=='gal': raster.render(T,geom.MAT,W(1.9,352,1.6),W(4.0,333,0.85),84,out='gal.png')
