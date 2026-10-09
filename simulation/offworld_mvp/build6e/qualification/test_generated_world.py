"""Focused generated-WORLD invariants; no database or scientific admission."""
import unittest
from decimal import Decimal as D

from simulation.offworld_mvp.build6e.generated_world import (
    _block, _dimensions, _interval, _sublimation_pressure, bind_generated_target,
    _material_family_truth, MATERIAL_FAMILIES, load_inputs, load_material_policy,
)


class GeneratedWorldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,cls.policy=load_inputs()
        cls.material_policy=load_material_policy()

    def block(self,key,seed='WORLD-GEN-2026',assertions=()):
        row=self.rows[key];domain='GEN_BODY_'+key+'_SITE_1'
        mass,radius,_=_dimensions(row,assertions,seed,key,domain)
        au=_interval(seed,key,domain,'heliocentric_distance',
            row['fallback_heliocentric_distance_min_au'],
            row['fallback_heliocentric_distance_max_au'],0)
        return mass,_block(row,self.policy,seed,key,domain,mass,radius,au)

    def test_every_applicable_prior_compiles_without_resource_evidence(self):
        applicable=[key for key,row in self.rows.items() if row['material_model_applicability']
                    in ('SOLID','SOLID_WITH_ATMOSPHERE')]
        self.assertEqual(len(applicable),90)
        zeros=0
        for key in applicable:
            mass,block=self.block(key)
            self.assertTrue(D(0)<=block['target_mass_kg']<=block['host_mass_kg']<=mass,key)
            self.assertLessEqual(block['target_fraction'],1,key)
            self.assertLessEqual(block['retention_loss_kg'],block['target_mass_kg']*D('.01')
                                 if block['form']=='FREE_ICE' else D(0),key)
            zeros+=block['target_mass_kg']==0
        self.assertGreater(zeros,0)

    def test_replay_and_body_key_independence(self):
        self.assertEqual(self.block('BENNU'),self.block('BENNU'))
        self.assertNotEqual(self.block('BENNU')[1],self.block('PHOBOS')[1])
        self.assertNotEqual(self.block('PHOBOS','WORLD-GEN-2026'),
                            self.block('PHOBOS','OTHER-WORLD-SEED'))

    def test_coarse_four_family_domain_truth_is_seeded_and_unknown_is_not_absence(self):
        outcomes={family:set() for family in MATERIAL_FAMILIES}
        unknown_outcomes={family:set() for family in MATERIAL_FAMILIES}
        for key,row in self.rows.items():
            if row['material_model_applicability'] not in ('SOLID','SOLID_WITH_ATMOSPHERE'):
                continue
            _,block=self.block(key)
            domain='GEN_BODY_'+key+'_SITE_1'
            truth=_material_family_truth(row,block,self.material_policy,'WORLD-GEN-2026',key,domain)
            self.assertEqual(tuple(truth),MATERIAL_FAMILIES)
            self.assertTrue(all(type(value) is bool for value in truth.values()))
            if block['target_mass_kg']>0:self.assertTrue(truth['VOLATILES'])
            for family,value in truth.items():outcomes[family].add(value)
            if int(row['m4b_unknown_family_count'])==4:
                # UNKNOWN_AFTER_SEARCH is no evidence of absence: these
                # bodies can still realize material presence in the fiction.
                for family,value in truth.items():unknown_outcomes[family].add(value)
            self.assertEqual(truth,_material_family_truth(row,block,self.material_policy,
                'WORLD-GEN-2026',key,domain))
        self.assertEqual(outcomes,{family:{False,True} for family in MATERIAL_FAMILIES})
        self.assertEqual(unknown_outcomes,{family:{False,True} for family in MATERIAL_FAMILIES})

    def test_sample_does_not_constrain_body_mass_or_grade(self):
        sample={'scope_kind':'SAMPLE','property_code':'BULK_DENSITY',
                'value_kind':'RANGE','value_min':D('999'),
                'value_max':D('1000'),'unit_lexeme':'g/cm3'}
        self.assertEqual(self.block('BENNU'),self.block('BENNU',assertions=(sample,)))

    def test_thermal_verification_and_explicit_recovery(self):
        self.assertAlmostEqual(float(_sublimation_pressure(D('230'),self.policy)),8.94735,places=4)
        _,block=self.block('EUROPA')
        profile={'resource_id':'RES','node_id':'OFF:EUROPA:TEST','max_depth_m':'100000',
                 'max_temperature_k':'1000','max_pressure_pa':'10000000',
                 'compatible_forms':['FREE_ICE'],'recovery_yield':'0.5',
                 'kg_per_model_unit':'10'}
        resource=bind_generated_target({'block':block},profile)
        self.assertEqual(resource.in_situ,block['target_mass_kg']/D(10))
        self.assertLessEqual(resource.recoverable,resource.accessible)
        self.assertLessEqual(resource.remaining,resource.recoverable)
        incompatible={**profile,'compatible_forms':['MINERAL_BOUND_H2O_OH']}
        self.assertEqual(bind_generated_target({'block':block},incompatible).remaining,0)
        too_hot={**profile,'max_temperature_k':'1'}
        self.assertEqual(bind_generated_target({'block':block},too_hot).accessible,0)
        site=object();deposit_id=object()
        projection={'deposits':[{'deposit_id':deposit_id,'location_id':site,
            'resource_class':'WATER_BEARING_MATERIAL','initial_in_situ_state':'KNOWN',
            'initial_in_situ_quantity':block['target_mass_kg'],'unit_key':'GEN_KG_V1',
            'phase_ref':block['form']}],
            'hidden_states':[{'location_id':site,'property_code':'GEN_BLOCK_TOP_DEPTH_M',
                'value_state':'KNOWN','numeric_value':block['depth_m'],'unit_key':'GEN_M_V1'},
                {'location_id':site,'property_code':'GEN_TEMPERATURE_K',
                'value_state':'KNOWN','numeric_value':block['temperature_k'],'unit_key':'GEN_K_V1'},
                {'location_id':site,'property_code':'GEN_PRESSURE_PA',
                'value_state':'KNOWN','numeric_value':block['pressure_pa'],'unit_key':'GEN_PA_V1'}],
            'stock_history':[]}
        self.assertEqual(bind_generated_target(projection,profile),resource)
        projection['stock_history']=[{'deposit_id':deposit_id,'remaining_state':'KNOWN',
            'remaining_in_situ':D(0),'unit_key':'GEN_KG_V1'}]
        self.assertEqual(bind_generated_target(projection,profile).remaining,0)


if __name__=='__main__':unittest.main()
