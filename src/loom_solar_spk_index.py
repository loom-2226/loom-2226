"""Governed indexed evaluator for structurally simple direct SPK sources.

This is an acceleration layer, not a new state authority. It evaluates the
selected primary SPK's own segment descriptors with CSPICE spkpvn and CSPICE
frame transforms. Sources that cannot prove the required structural invariants
are ineligible and callers must use the ordinary governed resolver.
"""
from __future__ import annotations
from bisect import bisect_right
from contextlib import contextmanager
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

class IndexedCommonCenterRelativeSpk:
    """Evaluate body relative to center when both share one governed SPK and encoded center."""
    def __init__(self,adapter,body_id,center_id,epoch_et):
        self.adapter=adapter; self.body_id=body_id; self.center_id=center_id
        bi=adapter.registry.body_identifier(body_id); ci=adapter.registry.body_identifier(center_id)
        if any(x.authority!='NAIF' or x.identifier_type!='NAIF_ID' for x in (bi,ci)):
            raise ValueError('indexed relative SPK requires governed NAIF_IDs')
        self.body_target=int(bi.identifier_value); self.center_target=int(ci.identifier_value)
        self.source,self.body_coverage=adapter.registry.source_for(body_id,epoch_et)
        cs,self.center_coverage=adapter.registry.source_for(center_id,epoch_et)
        if cs.ephemeris_source_id!=self.source.ephemeris_source_id:
            raise ValueError('body and center do not share governed source')
        if not self.source.state_capability.startswith(('DIRECT_','HORIZONS_')):
            raise ValueError('indexed relative SPK requires direct source authority')
        self.primary=adapter._source_asset(self.source)
        if adapter._source_asset(cs)!=self.primary: raise ValueError('body and center primary SPKs differ')
        self.body_segments,self.center_segments=self._index()
        self.body_starts=[x.start_et for x in self.body_segments]
        self.center_starts=[x.start_et for x in self.center_segments]
        if not self.body_segments or not self.center_segments: raise ValueError('missing indexed target segments')
        allseg=self.body_segments+self.center_segments
        if any(x.frame not in (1,17) for x in allseg): raise ValueError('unsupported indexed SPK frame')
        centers={x.center for x in allseg}
        if len(centers)!=1: raise ValueError('body and center do not share one encoded SPK center')

    def _index(self):
        spice=self.adapter._spice(); h=spice.dafopr(str(self.primary)); b=[]; c=[]
        try:
            spice.dafbfs(h)
            while spice.daffna():
                summary=spice.dafgs(); dc,ic=spice.dafus(summary,2,6); target=int(ic[0])
                if target in (self.body_target,self.center_target):
                    row=IndexedSegment(float(dc[0]),float(dc[1]),summary[:5].copy(),int(ic[1]),int(ic[2]),int(ic[3]))
                    (b if target==self.body_target else c).append(row)
        finally: spice.dafcls(h)
        b.sort(key=lambda x:(x.start_et,x.end_et)); c.sort(key=lambda x:(x.start_et,x.end_et))
        return tuple(b),tuple(c)

    @staticmethod
    def _segment(rows,starts,et):
        j=bisect_right(starts,et)-1
        if j<0 or not(rows[j].start_et<=et<=rows[j].end_et): raise ValueError('epoch falls in indexed SPK gap')
        return rows[j]

    def evaluate_many(self,epochs):
        epochs=tuple(float(x) for x in epochs)
        if not epochs:return tuple()
        for cov in (self.body_coverage,self.center_coverage):
            if cov.coverage_start_et is None or cov.coverage_end_et is None or any(not(cov.coverage_start_et<=t<=cov.coverage_end_et) for t in epochs):
                raise ValueError('epoch outside governed source coverage')
        for t in (min(epochs),max(epochs)):
            bs,_=self.adapter.registry.source_for(self.body_id,t); cs,_=self.adapter.registry.source_for(self.center_id,t)
            if bs.ephemeris_source_id!=self.source.ephemeris_source_id or cs.ephemeris_source_id!=self.source.ephemeris_source_id:
                raise ValueError('batch crosses governed source authority seam')
        with self.adapter._source_pool(self.source) as spice:
            handles=[spice.kdata(i,'SPK') for i in range(spice.ktotal('SPK'))]
            ph=[x[3] for x in handles if Path(x[0]).resolve()==self.primary]
            if len(ph)!=1: raise ValueError('selected primary SPK is not uniquely furnished')
            ph=ph[0]; out=[]
            for et in epochs:
                a=self._segment(self.body_segments,self.body_starts,et); b=self._segment(self.center_segments,self.center_starts,et)
                fa,sa,ca=spice.spkpvn(ph,a.descriptor,et); fb,sb,cb=spice.spkpvn(ph,b.descriptor,et)
                if ca!=cb or fa!=a.frame or fb!=b.frame: raise ValueError('indexed descriptor metadata mismatch')
                if fa!=fb: raise ValueError('body and center SPK frames differ')
                rel=[float(x-y) for x,y in zip(sa,sb)]
                if fa==1: rel=spice.mxvg(spice.sxform('J2000',SPICE_FRAME,et),rel)
                elif fa!=17: raise ValueError(f'unsupported indexed SPK frame {fa}')
                out.append(tuple(float(v) for v in rel))
            return tuple(out)

class IndexedParentRelativeSpk:
    """Evaluate a governed SPK target whose encoded center is the requested parent."""
    def __init__(self,adapter,body_id,center_id,epoch_et):
        self.adapter=adapter; self.body_id=body_id; self.center_id=center_id
        bi=adapter.registry.body_identifier(body_id); ci=adapter.registry.body_identifier(center_id)
        if bi.identifier_type not in ('NAIF_ID','SPK_TARGET_ID') or ci.authority!='NAIF' or ci.identifier_type!='NAIF_ID':
            raise ValueError('indexed parent-relative SPK requires governed SPK target and NAIF parent')
        self.target=int(bi.identifier_value); self.center=int(ci.identifier_value)
        self.source,self.coverage=adapter.registry.source_for(body_id,epoch_et)
        self.primary=adapter._source_asset(self.source)
        self.segments=self._index(); self.starts=[x.start_et for x in self.segments]
        if not self.segments: raise ValueError('primary SPK has no target segments')
        if any(x.center!=self.center for x in self.segments): raise ValueError('SPK encoded center is not requested parent')
        if any(x.frame not in (1,17) for x in self.segments): raise ValueError('unsupported indexed SPK frame')

    def _index(self):
        spice=self.adapter._spice(); h=spice.dafopr(str(self.primary)); out=[]
        try:
            spice.dafbfs(h)
            while spice.daffna():
                summary=spice.dafgs(); dc,ic=spice.dafus(summary,2,6)
                if int(ic[0])==self.target:
                    out.append(IndexedSegment(float(dc[0]),float(dc[1]),summary[:5].copy(),int(ic[1]),int(ic[2]),int(ic[3])))
        finally: spice.dafcls(h)
        out.sort(key=lambda x:(x.start_et,x.end_et)); return tuple(out)

    @contextmanager
    def session(self):
        with self.adapter._source_pool(self.source) as spice:
            handles=[spice.kdata(i,'SPK') for i in range(spice.ktotal('SPK'))]
            ph=[x[3] for x in handles if Path(x[0]).resolve()==self.primary]
            if len(ph)!=1: raise ValueError('selected primary SPK is not uniquely furnished')
            self._session_spice=spice; self._session_handle=ph[0]
            try: yield self
            finally:
                self._session_spice=None; self._session_handle=None

    def _evaluate_furnished(self,epochs):
        spice=self._session_spice; ph=self._session_handle; out=[]
        for et in epochs:
            j=bisect_right(self.starts,et)-1
            if j<0 or not(self.segments[j].start_et<=et<=self.segments[j].end_et): raise ValueError('epoch falls in indexed SPK gap')
            seg=self.segments[j]; frame,state,center=spice.spkpvn(ph,seg.descriptor,et)
            if center!=self.center or frame!=seg.frame: raise ValueError('indexed descriptor metadata mismatch')
            if frame==1: state=spice.mxvg(spice.sxform('J2000',SPICE_FRAME,et),state)
            elif frame!=17: raise ValueError(f'unsupported indexed SPK frame {frame}')
            out.append(tuple(float(v) for v in state))
        return tuple(out)

    def evaluate_many(self,epochs):
        epochs=tuple(float(x) for x in epochs)
        if getattr(self,'_session_spice',None) is not None: return self._evaluate_furnished(epochs)
        if not epochs:return tuple()
        if self.coverage.coverage_start_et is None or self.coverage.coverage_end_et is None or any(not(self.coverage.coverage_start_et<=t<=self.coverage.coverage_end_et) for t in epochs):
            raise ValueError('epoch outside governed source coverage')
        for t in (min(epochs),max(epochs)):
            s,_=self.adapter.registry.source_for(self.body_id,t)
            if s.ephemeris_source_id!=self.source.ephemeris_source_id: raise ValueError('batch crosses governed source authority seam')
        with self.adapter._source_pool(self.source) as spice:
            handles=[spice.kdata(i,'SPK') for i in range(spice.ktotal('SPK'))]
            ph=[x[3] for x in handles if Path(x[0]).resolve()==self.primary]
            if len(ph)!=1: raise ValueError('selected primary SPK is not uniquely furnished')
            ph=ph[0]; out=[]
            for et in epochs:
                j=bisect_right(self.starts,et)-1
                if j<0 or not(self.segments[j].start_et<=et<=self.segments[j].end_et): raise ValueError('epoch falls in indexed SPK gap')
                seg=self.segments[j]; frame,state,center=spice.spkpvn(ph,seg.descriptor,et)
                if center!=self.center or frame!=seg.frame: raise ValueError('indexed descriptor metadata mismatch')
                if frame==1: state=spice.mxvg(spice.sxform('J2000',SPICE_FRAME,et),state)
                elif frame!=17: raise ValueError(f'unsupported indexed SPK frame {frame}')
                out.append(tuple(float(v) for v in state))
            return tuple(out)

    def truth_many(self,epochs):
        """Independent high-level SPICE truth path for the same governed parent-relative artifact."""
        epochs=tuple(float(x) for x in epochs)
        if getattr(self,'_session_spice',None) is not None:
            return tuple(tuple(float(v) for v in self._session_spice.spkezr(str(self.target),et,SPICE_FRAME,'NONE',str(self.center))[0]) for et in epochs)
        with self.adapter._source_pool(self.source) as spice:
            return tuple(tuple(float(v) for v in spice.spkezr(str(self.target),et,SPICE_FRAME,'NONE',str(self.center))[0])
                         for et in epochs)
