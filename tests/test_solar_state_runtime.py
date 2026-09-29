import pytest
from src.loom_solar_state_runtime import HermiteStateFunction,SolarStateRuntime,StateRuntimeError

def obj(body,center,p0,p1,v=(0,0,0)):
 return {'body_id':body,'center_id':center,'reference_frame':'ECLIPJ2000','declared_error_km':1,
 'samples':[{'epoch_et':0,'resolution':'RESOLVED','authority_class':'DIRECT','position_km':p0,'velocity_km_s':v,'source_ref':'s','center_source_ref':'c'},
 {'epoch_et':10,'resolution':'RESOLVED','authority_class':'DIRECT','position_km':p1,'velocity_km_s':v,'source_ref':'s','center_source_ref':'c'}]}

def test_function_evaluates_epoch():
 f=HermiteStateFunction(obj('EARTH','SUN',[0,0,0],[10,0,0])); assert f.state(5).position_km==(5.0,0.0,0.0)

def test_hierarchy_composes_parent_relative_functions():
 r=SolarStateRuntime.from_chunk({'objects':[obj('EARTH','SUN',[0,0,0],[10,0,0]),obj('MOON','EARTH',[0,2,0],[0,2,0])]})
 assert r.world_position('MOON',5)==(5.0,2.0,0.0)

def test_outside_validity_fails_closed():
 f=HermiteStateFunction(obj('EARTH','SUN',[0,0,0],[10,0,0]));
 with pytest.raises(StateRuntimeError): f.state(11)

def test_transition_fails_closed():
 o=obj('EARTH','SUN',[0,0,0],[10,0,0]); o['samples'][1]['source_ref']='other'; f=HermiteStateFunction(o)
 with pytest.raises(StateRuntimeError): f.state(5)
