#!/usr/bin/env python3
"""Apply an approved second finish to existing glTF nozzle groove faces.

Only splits triangle index arrays of the existing dry:nozzle mesh into two
material primitives. Zero added/removed triangles, geometry, nodes or mass.
"""
from __future__ import annotations
import struct

def colour_nozzle_bands(data,tail,node,coil_material,stations):
    assert stations==[47.2,48.5,49.8,51.1,52.4]
    assert node["name"]=="dry:nozzle"
    if len(data["buffers"])!=1:
        raise RuntimeError("STOP export: expected one GLB binary buffer")
    binary_size,binary_kind=struct.unpack_from("<II",tail,0)
    if binary_kind!=0x004e4942 or len(tail)!=8+binary_size:
        raise RuntimeError("STOP export: unexpected GLB binary structure")
    binary=bytearray(tail[8:])
    mesh=data["meshes"][node["mesh"]]
    primitives=mesh["primitives"]
    assert primitives

    def unpack_accessor(aidx):
        a=data["accessors"][aidx]
        v=data["bufferViews"][a["bufferView"]]
        off=v.get("byteOffset",0)+a.get("byteOffset",0)
        component=a["componentType"]
        if a["type"]=="VEC3" and component==5126:
            code="fff";width=12
        elif a["type"]=="SCALAR" and component in (5121,5123,5125):
            code={5121:"B",5123:"H",5125:"I"}[component]
            width=struct.calcsize("<"+code)
        else:
            raise RuntimeError("STOP export: unsupported nozzle accessor "+str(a))
        stride=v.get("byteStride",width)
        return [struct.unpack_from("<"+code,binary,off+stride*i)
                for i in range(a["count"])]

    def add_index_accessor(indices):
        assert indices and len(indices)%3==0
        while len(binary)%4:binary.append(0)
        off=len(binary)
        payload=struct.pack("<"+"I"*len(indices),*indices)
        binary.extend(payload)
        view=len(data["bufferViews"])
        data["bufferViews"].append(dict(buffer=0,byteOffset=off,
                                        byteLength=len(payload),target=34963))
        accessor=len(data["accessors"])
        data["accessors"].append(dict(bufferView=view,byteOffset=0,
            componentType=5125,count=len(indices),type="SCALAR",
            min=[min(indices)],max=[max(indices)]))
        return accessor

    geometry=[]
    points=[]
    for prim in primitives:
        if prim.get("mode",4)!=4 or "POSITION" not in prim["attributes"]:
            raise RuntimeError("STOP export: nozzle must use triangles and positions")
        pos=[tuple(v) for v in unpack_accessor(prim["attributes"]["POSITION"])]
        inds=([v[0] for v in unpack_accessor(prim["indices"])]
              if "indices" in prim else list(range(len(pos))))
        if len(inds)%3:raise RuntimeError("STOP export: malformed nozzle triangle")
        geometry.append((prim,pos,inds))
        points.extend(pos)
    extents=[(min(p[d] for p in points),max(p[d] for p in points))
             for d in range(3)]
    axis=max(range(3),key=lambda d:extents[d][1]-extents[d][0])
    lo,hi=extents[axis];span=hi-lo
    if not 6.7<span<7.3:
        raise RuntimeError("STOP export: nozzle longitudinal axis not 7m "+str(extents))

    def source_x(p):
        # Local glTF translations do not matter; parametric x from exact
        # 7m source extent [46.3,53.3] preserves all five ring stations.
        return 46.3+7.*(p[axis]-lo)/span

    hits=[0]*5;kept=[];original_triangles=0;dark_triangles=0
    for prim,pos,indices in geometry:
        bronze=[];dark=[]
        for i in range(0,len(indices),3):
            tri=indices[i:i+3]
            center=sum(source_x(pos[j]) for j in tri)/3.
            station=next((j for j,x in enumerate(stations)
                          if abs(center-x)<=.075001),None)
            if station is None:
                bronze.extend(tri)
            else:
                dark.extend(tri)
                hits[station]+=1
        original_triangles+=len(indices)//3
        dark_triangles+=len(dark)//3
        if bronze:
            p=dict(prim)
            p["indices"]=add_index_accessor(bronze)
            kept.append(p)
        if dark:
            p=dict(prim)
            p["indices"]=add_index_accessor(dark)
            p["material"]=coil_material
            kept.append(p)
    if any(x==0 for x in hits):
        raise RuntimeError("STOP export: no band faces for one or more stations "+str(hits))
    assert sum(hits)==dark_triangles
    assert sum(data["accessors"][p["indices"]]["count"] for p in kept)==3*original_triangles
    mesh["primitives"]=kept
    data["buffers"][0]["byteLength"]=len(binary)
    binary.extend(b"\0"*((-len(binary))%4))
    tail=struct.pack("<II",len(binary),0x004e4942)+bytes(binary)
    extras=node.setdefault("extras",{})
    extras["nozzle_coil_band_role"]="nozzle_coil_bands"
    extras["nozzle_coil_band_material_index"]=coil_material
    extras["nozzle_coil_band_triangles_per_station"]=hits
    extras["nozzle_coil_band_width_m"]=.15
    extras["nozzle_coil_band_depth_m"]=.03
    return tail,dict(stations_x_m=stations,
                     width_m=.15,depth_m=.03,
                     face_triangles_per_station=hits,
                     face_triangles_total=dark_triangles,
                     source_triangles_total=original_triangles,
                     triangle_conservation=True,
                     nozzle_geometry_envelope_unchanged=True,
                     print_band_width_1_100_mm=1.5,
                     longitudinal_gltf_axis=axis)
