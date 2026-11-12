import geom,raster,math,sys
geom.build(); T=geom.by_material(); W=geom.W
which=sys.argv[1]
if which=='ward': raster.render(T,geom.MAT,W(1.85,40,1.6),W(3.6,100,0.6),76,out='ward.png')
if which=='gal': raster.render(T,geom.MAT,W(1.9,352,1.6),W(4.0,333,0.85),84,out='gal.png')
if which=='obs': raster.render(T,geom.MAT,W(1.85,166,1.6),W(3.7,192,0.45),80,out='obs.png')
if which=='ex': raster.render(T,geom.MAT,W(1.85,212,1.6),W(3.6,242,0.6),82,out='ex.png')
if which=='wc': raster.render(T,geom.MAT,W(2.12,273,1.5),W(3.7,292,0.8),86,out='wc.png')
