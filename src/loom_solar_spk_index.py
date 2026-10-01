"""Governed indexed evaluator for structurally simple direct SPK sources.

This is an acceleration layer, not a new state authority. It evaluates the
selected primary SPK's own segment descriptors with CSPICE spkpvn and CSPICE
frame transforms. Sources that cannot prove the required structural invariants
are ineligible and callers must use the ordinary governed resolver.
"""
from __future__ import annotations
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from src.loom_spice_ephemeris_adapter import SPICE_FRAME

@dataclass(frozen=True)
class IndexedSegment:
    start_et: float
    end_et: float
    descriptor: object
    center: int
    frame: int
    spk_type: int

class IndexedDirectSpk:
    def __init__(self, adapter, body_id, epoch_et):
        self.adapter=adapter; self.body_id=body_id
        ident=adapter.registry.body_identifier(body_id)
        if ident.authority!='NAIF' or ident.identifier_type!='NAIF_ID':
            raise ValueError('indexed SPK requires governed NAIF_ID')
        self.target=int(ident.identifier_value)
        self.source,self.coverage=adapter.registry.source_for(body_id,epoch_et)
        if not self.source.state_capability.startswith(('DIRECT_','HORIZONS_')):
            raise ValueError('indexed SPK requires direct source authority')
        self.primary=adapter._source_asset(self.source)
        self.segments=self._index()
        self.starts=[x.start_et for x in self.segments]
        if not self.segments: raise ValueError('primary SPK has no target segments')
        if any(seg.center != 10 for seg in self.segments):
            raise ValueError('indexed fast path requires Sun-centered segments')
        if any(seg.frame not in (1,17) for seg in self.segments):
            raise ValueError('indexed fast path requires J2000 or ECLIPJ2000 segments')

    def _index(self):
        spice=self.adapter._spice(); h=spice.dafopr(str(self.primary)); out=[]
        try:
            spice.dafbfs(h)
            while spice.daffna():
                summary=spice.dafgs(); dc,ic=spice.dafus(summary,2,6)
                if int(ic[0])==self.target:
                    out.append(IndexedSegment(float(dc[0]),float(dc[1]),summary[:5].copy(),
                                              int(ic[1]),int(ic[2]),int(ic[3])))
        finally: spice.dafcls(h)
        out.sort(key=lambda x:(x.start_et,x.end_et))
        return tuple(out)

    def _segment(self,et):
        j=bisect_right(self.starts,et)-1
        if j<0: raise ValueError('epoch precedes indexed SPK coverage')
        seg=self.segments[j]
        if not(seg.start_et<=et<=seg.end_et): raise ValueError('epoch falls in indexed SPK gap')
        return seg

    def evaluate_many(self,epochs):
        epochs=tuple(float(x) for x in epochs)
        if not epochs:return tuple()
        lo=self.coverage.coverage_start_et; hi=self.coverage.coverage_end_et
        if lo is None or hi is None or any(not(lo<=t<=hi) for t in epochs):
            raise ValueError('epoch outside governed source coverage')
        # The source selected at both extremes must remain this exact governed source.
        for t in (min(epochs),max(epochs)):
            source,_=self.adapter.registry.source_for(self.body_id,t)
            if source.ephemeris_source_id!=self.source.ephemeris_source_id:
                raise ValueError('batch crosses governed source authority seam')
        with self.adapter._source_pool(self.source) as spice:
            handles=[spice.kdata(i,'SPK') for i in range(spice.ktotal('SPK'))]
            ph=[x[3] for x in handles if Path(x[0]).resolve()==self.primary]
            if len(ph)!=1: raise ValueError('selected primary SPK is not uniquely furnished')
            ph=ph[0]; out=[]
            for et in epochs:
                seg=self._segment(et)
                frame,state,center=spice.spkpvn(ph,seg.descriptor,et)
                if frame!=seg.frame or center!=seg.center:
                    raise ValueError('SPK descriptor metadata changed during evaluation')
                # Current fast-path proof only admits Sun-centered segments. This
                # avoids reimplementing SPICE center-chain composition.
                if center!=10: raise ValueError('indexed fast path requires Sun-centered segment')
                if frame==17: transformed=state  # ECLIPJ2000
                elif frame==1:
                    transformed=spice.mxvg(spice.sxform('J2000',SPICE_FRAME,et),state)
                else: raise ValueError(f'unsupported indexed SPK frame {frame}')
                out.append(tuple(float(v) for v in transformed))
            return tuple(out)
