#!/usr/bin/env python3
"""Nozzle band face partition, v2.5.9.

Exact five longitudinal material boundaries on EXISTING triangulated surface.
Split intersected triangles using plane clipping and interpolate existing
vertex attributes. Do not add solids, shift vertex coordinates away from the
source triangles, alter the nozzle envelope or assign source-booked mass.
"""
from __future__ import annotations
import math,struct

_STATIONS=[47.2,48.5,49.8,51.1,52.4]
_TYPES={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4}
_TYPES.update({"MAT2":4,"MAT3":9,"MAT4":16})
_CODES={5120:"b",5121:"B",5122:"h",5123:"H",5125:"I",5126:"f"}
_SIZES={k:struct.calcsize("<"+v) for k,v in _CODES.items()}

def split_nozzle_rings(data,tail,node,dark_material,stations):
    assert stations==_STATIONS
    assert node["name"]=="dry:nozzle" and len(data["buffers"])==1
    size,kind=struct.unpack_from("<II",tail,0)
    if kind!=0x004e4942 or len(tail)!=8+size:
        raise RuntimeError("STOP export: nozzle GLB BIN chunk malformed")
    binary=bytearray(tail[8:])
    mesh=data["meshes"][node["mesh"]]
    original=mesh["primitives"]
    if not original:raise RuntimeError("STOP export: nozzle primitive absent")

    def read_accessor(index):
        a=data["accessors"][index]
        if "sparse" in a or "bufferView" not in a:
            raise RuntimeError("STOP export: nozzle sparse vertex accessor unsupported")
        v=data["bufferViews"][a["bufferView"]]
        component=a["componentType"]
        if component not in _CODES or a["type"] not in _TYPES:
            raise RuntimeError("STOP export: nozzle accessor type unsupported "+str(a))
        n=_TYPES[a["type"]]
        code="<"+_CODES[component]*n
        length=n*_SIZES[component]
        stride=v.get("byteStride",length)
        offset=v.get("byteOffset",0)+a.get("byteOffset",0)
        vals=[list(struct.unpack_from(code,binary,offset+stride*i))
              for i in range(a["count"])]
        if a.get("normalized"):
            signed=component in (5120,5122)
            lim={5120:127,5121:255,5122:32767,5123:65535}.get(component)
            if lim is None:raise RuntimeError("STOP export: normalized 32-bit nozzle attribute")
            vals=[[max(-1.,float(x)/lim) if signed else float(x)/lim
                   for x in row] for row in vals]
        return vals

    originals=[]
    all_positions=[]
    for prim in original:
        if prim.get("mode",4)!=4 or "POSITION" not in prim.get("attributes",{}):
            raise RuntimeError("STOP export: nozzle must use triangle primitives with POSITION")
        if prim.get("targets"):
            raise RuntimeError("STOP export: cannot clip morph-target nozzle")
        attrs={name:read_accessor(idx) for name,idx in prim["attributes"].items()}
        n=len(attrs["POSITION"])
        if any(len(values)!=n for values in attrs.values()):
            raise RuntimeError("STOP export: nozzle vertex attributes have different counts")
        if "indices" in prim:
            indices=[int(row[0]) for row in read_accessor(prim["indices"])]
        else:indices=list(range(n))
        if len(indices)%3 or any(i<0 or i>=n for i in indices):
            raise RuntimeError("STOP export: invalid nozzle triangle indices")
        originals.append((prim,attrs,indices))
        all_positions.extend(attrs["POSITION"])
    assert all(len(p)==3 for p in all_positions)
    source_bounds=[(min(p[i] for p in all_positions),
                    max(p[i] for p in all_positions)) for i in range(3)]
    axis=max(range(3),key=lambda i:source_bounds[i][1]-source_bounds[i][0])
    lo,hi=source_bounds[axis];span=hi-lo
    if not 6.7<span<7.3:
        raise RuntimeError("STOP export: unexpected 7m nozzle axis "+str(source_bounds))
    def plane(x):return lo+(x-46.3)*span/7.
    # The appearance boundary is exactly a longitudinal plane, not the
    # triangle centroid classification which produced sawtooth edges.
    edges=[]
    for x in stations:edges.extend([plane(x-.075),plane(x+.075)])
    assert edges==sorted(edges)
    intervals=[(-math.inf,edges[0],None)]
    for i in range(5):
        intervals.append((edges[2*i],edges[2*i+1],i))
        intervals.append((edges[2*i+1],
                          edges[2*i+2] if i<4 else math.inf,None))

    def clipping(poly,edge,lower):
        if not poly:return []
        out=[]
        def inside(v):
            x=v["POSITION"][axis]
            return x>=edge if lower else x<=edge
        prev=poly[-1]
        pi=inside(prev)
        for cur in poly:
            ci=inside(cur)
            if pi!=ci:
                a=prev["POSITION"][axis]
                b=cur["POSITION"][axis]
                if abs(b-a)<1e-12:
                    raise RuntimeError("STOP export: degenerate clipping edge")
                t=max(0.,min(1.,(edge-a)/(b-a)))
                interp={name:[float(u)+t*(float(v)-float(u))
                              for u,v in zip(prev[name],cur[name])]
                        for name in prev}
                interp["POSITION"][axis]=edge
                out.append(interp)
            if ci:out.append(cur)
            prev,pi=cur,ci
        return out

    def area(a,b,c):
        p=a["POSITION"];q=b["POSITION"];r=c["POSITION"]
        u=[q[i]-p[i] for i in range(3)]
        v=[r[i]-p[i] for i in range(3)]
        cross=(u[1]*v[2]-u[2]*v[1],
               u[2]*v[0]-u[0]*v[2],
               u[0]*v[1]-u[1]*v[0])
        return .5*math.sqrt(sum(x*x for x in cross))

    def append_view(raw,target):
        while len(binary)%4:binary.append(0)
        off=len(binary)
        binary.extend(raw)
        j=len(data["bufferViews"])
        data["bufferViews"].append(dict(buffer=0,byteOffset=off,
                                        byteLength=len(raw),target=target))
        return j
    def write_attribute(rows,semantic,typ):
        n=_TYPES[typ]
        assert all(len(row)==n for row in rows)
        flat=[float(v) for row in rows for v in row]
        view=append_view(struct.pack("<"+"f"*len(flat),*flat),34962)
        acc=dict(bufferView=view,byteOffset=0,componentType=5126,
                 count=len(rows),type=typ)
        if semantic=="POSITION":
            acc["min"]=[min(row[i] for row in rows) for i in range(3)]
            acc["max"]=[max(row[i] for row in rows) for i in range(3)]
        idx=len(data["accessors"]);data["accessors"].append(acc)
        return idx
    def write_indices(n):
        view=append_view(struct.pack("<"+"I"*n,*range(n)),34963)
        idx=len(data["accessors"])
        data["accessors"].append(dict(bufferView=view,byteOffset=0,
            componentType=5125,count=n,type="SCALAR",
            min=[0],max=[n-1]))
        return idx

    src_count=out_count=0
    src_area=out_area=0.
    dark_counts=[0]*5
    edge_vertices=[0]*10
    coplanar_cut_triangles=[0]*10
    coplanar_cut_area_m2=[0.]*10
    all_out_positions=[]
    replacement=[]
    for prim,attrs,indices in originals:
        types={name:data["accessors"][idx]["type"]
               for name,idx in prim["attributes"].items()}
        classes={None:[],**{j:[] for j in range(5)}}
        for start in range(0,len(indices),3):
            tri=[{name:list(values[indices[start+j]])
                  for name,values in attrs.items()} for j in range(3)]
            triangle_area=area(*tri)
            if triangle_area<1e-13:
                continue
            src_area+=triangle_area
            src_count+=1
            xmin=min(v["POSITION"][axis] for v in tri)
            xmax=max(v["POSITION"][axis] for v in tri)
            # Groove-wall triangles can be coplanar with the chosen cutting
            # plane. Assign each such triangle to the dark groove ONCE,
            # rather than including its nonzero area in both intervals.
            # 5 micrometres covers source glTF float32 rounding only.
            coplanar_edge=next((i for i,x in enumerate(edges)
                if xmax-xmin<=5e-6 and
                   abs(xmin-x)<=5e-6 and abs(xmax-x)<=5e-6),None)
            if coplanar_edge is not None:
                ring=coplanar_edge//2
                classes[ring].extend(tri)
                all_out_positions.extend(v["POSITION"] for v in tri)
                out_area+=triangle_area
                out_count+=1
                dark_counts[ring]+=1
                coplanar_cut_triangles[coplanar_edge]+=1
                coplanar_cut_area_m2[coplanar_edge]+=triangle_area
                for vertex in tri:
                    for i,x in enumerate(edges):
                        if abs(vertex["POSITION"][axis]-x)<1e-5:
                            edge_vertices[i]+=1
                continue
            for lower,upper,ring in intervals:
                if xmax<lower-1e-9 or xmin>upper+1e-9:
                    continue
                poly=tri
                if math.isfinite(lower):poly=clipping(poly,lower,True)
                if math.isfinite(upper):poly=clipping(poly,upper,False)
                if len(poly)<3:continue
                for j in range(1,len(poly)-1):
                    piece=[poly[0],poly[j],poly[j+1]]
                    a=area(*piece)
                    if a<1e-12:continue
                    out_area+=a;out_count+=1
                    classes[ring].extend(piece)
                    all_out_positions.extend(v["POSITION"] for v in piece)
                    if ring is not None:dark_counts[ring]+=1
                    for vertex in piece:
                        px=vertex["POSITION"][axis]
                        for i,plane_x in enumerate(edges):
                            if abs(px-plane_x)<1e-7:edge_vertices[i]+=1
        for ring,vertices in classes.items():
            if not vertices:continue
            prim_out=dict(prim)
            attrs_out={}
            for name in attrs:
                rows=[v[name] for v in vertices]
                # Interpolated normal/tangent vectors retain their directions.
                if name in ("NORMAL","TANGENT"):
                    for row in rows:
                        nn=math.sqrt(sum(x*x for x in row[:3]))
                        if nn>1e-12:
                            row[:3]=[x/nn for x in row[:3]]
                attrs_out[name]=write_attribute(rows,name,types[name])
            prim_out["attributes"]=attrs_out
            prim_out["indices"]=write_indices(len(vertices))
            if ring is not None:prim_out["material"]=dark_material
            # Retain bronze material, mode and any original render extensions.
            replacement.append(prim_out)
    if not all(dark_counts) or not all(edge_vertices):
        raise RuntimeError("STOP export: missing clean nozzle coil-band boundary "+
                           str((dark_counts,edge_vertices)))
    if not out_area>0 or abs(src_area-out_area)/src_area>1e-6:
        raise RuntimeError("STOP export: nozzle surface area not conserved "+
                           str((src_area,out_area,coplanar_cut_triangles,coplanar_cut_area_m2)))
    output_bounds=[(min(p[i] for p in all_out_positions),
                    max(p[i] for p in all_out_positions)) for i in range(3)]
    if any(abs(a-b)>5e-5 for src,out in zip(source_bounds,output_bounds)
           for a,b in zip(src,out)):
        raise RuntimeError("STOP export: nozzle surface envelope changed "+
                           str((source_bounds,output_bounds)))
    assert sum(data["accessors"][p["indices"]]["count"] for p in replacement)==3*out_count
    mesh["primitives"]=replacement
    data["buffers"][0]["byteLength"]=len(binary)
    binary.extend(b"\0"*((-len(binary))%4))
    tail=struct.pack("<II",len(binary),0x004e4942)+bytes(binary)
    ex=node.setdefault("extras",{})
    ex.update(nozzle_coil_band_role="nozzle_coil_bands",
              nozzle_coil_band_material_index=dark_material,
              nozzle_coil_band_triangles_per_station=dark_counts,
              nozzle_coil_band_edges_vertex_hits=edge_vertices,
              nozzle_coil_band_width_m=.15,
              nozzle_coil_band_depth_m=.03)
    return tail,dict(stations_x_m=stations,width_m=.15,depth_m=.03,
        face_triangles_per_station=dark_counts,
        boundary_edge_vertices=edge_vertices,
        band_edges_split_exactly=True,
        clipped_triangles_total=out_count,
        source_triangles_total=src_count,
        source_surface_area_m2=src_area,
        clipped_surface_area_m2=out_area,
        relative_area_error=abs(src_area-out_area)/src_area,
        coplanar_cut_triangles=coplanar_cut_triangles,
        coplanar_cut_area_m2=coplanar_cut_area_m2,
        surface_area_conservation=True,
        source_bounds=source_bounds,output_bounds=output_bounds,
        nozzle_geometry_envelope_unchanged=True,
        print_band_width_1_100_mm=1.5,
        longitudinal_gltf_axis=axis,
        paint_by_triangle_centroid=False,
        source_mass_rebooking_t=0)
