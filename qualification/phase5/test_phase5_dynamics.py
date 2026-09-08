import unittest
from dataclasses import replace
from portable_dynamics import *


def diag(a,b,c): return ((a,0.,0.),(0.,b,0.),(0.,0.,c))


class Phase5DynamicsTests(unittest.TestCase):
    def setUp(self):
        self.s0=VehicleState(0.,(10.,-2.,3.),(1.,2.,-1.),(1.,0.,0.,0.),(0.,0.,0.),10.)

    def mp_fixed(self,s): return MassProperties(1000.,(0.,0.,0.),diag(2000.,3000.,4000.))
    def none(self,s,mp): return []

    def test_zero_force_coast(self):
        f=propagate(self.s0,10.,0.01,self.mp_fixed,self.none)[-1]
        self.assertEqual(f.v_N_m_s,self.s0.v_N_m_s)
        for i in range(3): self.assertAlmostEqual(f.r_N_m[i],self.s0.r_N_m[i]+10*self.s0.v_N_m_s[i],12)

    def test_single_axial_inertial_force(self):
        def eff(s,mp): return [EffectorCommand(force_N_N=(500.,0.,0.))]
        f=propagate(replace(self.s0,r_N_m=(0.,0.,0.),v_N_m_s=(0.,0.,0.)),4.,0.01,self.mp_fixed,eff)[-1]
        self.assertAlmostEqual(f.v_N_m_s[0],2.0,11)
        self.assertAlmostEqual(f.r_N_m[0],4.0,10)

    def test_offset_thruster_initial_wrench(self):
        s=replace(self.s0,r_N_m=(0.,0.,0.),v_N_m_s=(0.,0.,0.))
        def eff(s,mp): return [EffectorCommand(force_B_N=(100.,0.,0.),application_B_m=(0.,2.,0.))]
        d=derivative(s,self.mp_fixed,eff)
        self.assertAlmostEqual(d.dv[0],0.1,12)
        self.assertAlmostEqual(d.domega[2],-200./4000.,12)

    def test_symmetric_pair_near_pure_rotation_initial_wrench(self):
        s=replace(self.s0,r_N_m=(0.,0.,0.),v_N_m_s=(0.,0.,0.))
        def eff(s,mp): return [
            EffectorCommand(force_B_N=(100.,0.,0.),application_B_m=(0.,2.,0.)),
            EffectorCommand(force_B_N=(-100.,0.,0.),application_B_m=(0.,-2.,0.)),
        ]
        d=derivative(s,self.mp_fixed,eff)
        self.assertEqual(d.dv,(0.,0.,0.))
        self.assertAlmostEqual(d.domega[2],-400./4000.,12)

    def test_pitch_yaw_roll_intrinsic_couples(self):
        axes=[(0,300.,2000.),(1,300.,3000.),(2,300.,4000.)]
        for axis,tau,I in axes:
            with self.subTest(axis=axis):
                vec=[0.,0.,0.]; vec[axis]=tau
                def eff(s,mp,v=tuple(vec)): return [EffectorCommand(intrinsic_torque_B_Nm=v)]
                d=derivative(self.s0,self.mp_fixed,eff)
                self.assertAlmostEqual(d.domega[axis],tau/I,12)

    def test_combined_6dof_initial_derivative(self):
        def eff(s,mp): return [EffectorCommand(force_B_N=(100.,200.,300.),application_B_m=(0.,1.,0.),intrinsic_torque_B_Nm=(10.,20.,30.))]
        d=derivative(replace(self.s0,v_N_m_s=(0.,0.,0.)),self.mp_fixed,eff)
        self.assertEqual(d.dv,(0.1,0.2,0.3))
        self.assertAlmostEqual(d.domega[0],310./2000.,12)
        self.assertAlmostEqual(d.domega[1],20./3000.,12)
        self.assertAlmostEqual(d.domega[2],-70./4000.,12)

    def test_resource_depletion_and_cutoff(self):
        def mp(s): return MassProperties(900.+s.resource_kg,(0.,0.,0.),diag(2000.,3000.,4000.))
        def eff(s,mp):
            if s.resource_kg <= 0: return []
            return [EffectorCommand(force_N_N=(1000.,0.,0.),mass_flow_kg_s=2.)]
        s=replace(self.s0,r_N_m=(0.,0.,0.),v_N_m_s=(0.,0.,0.),resource_kg=10.)
        tr=propagate(s,10.,0.01,mp,eff)
        self.assertAlmostEqual(tr[-1].resource_kg,0.,12)
        v5=tr[500].v_N_m_s[0]; v10=tr[-1].v_N_m_s[0]
        self.assertAlmostEqual(v5,v10,5)

    def test_feed_cutoff_is_central_fail_closed(self):
        def eff(s,mp): return [EffectorCommand(force_N_N=(1000.,0.,0.),mass_flow_kg_s=2.)]
        s=replace(self.s0,resource_kg=0.,v_N_m_s=(0.,0.,0.))
        d=derivative(s,self.mp_fixed,eff)
        self.assertEqual(d.dv,(0.,0.,0.))
        self.assertEqual(d.dresource,0.0)

    def test_com_migration_changes_torque_arm(self):
        def mp(s):
            y=(10.-s.resource_kg)/10.
            return MassProperties(1000.,(0.,y,0.),diag(2000.,3000.,4000.))
        def eff(s,mp): return [EffectorCommand(force_B_N=(100.,0.,0.),application_B_m=(0.,2.,0.))]
        d_full=derivative(replace(self.s0,resource_kg=10.),mp,eff)
        d_empty=derivative(replace(self.s0,resource_kg=0.),mp,eff)
        self.assertAlmostEqual(d_full.domega[2],-200/4000,12)
        self.assertAlmostEqual(d_empty.domega[2],-100/4000,12)

    def test_inertia_migration_idot_term(self):
        def mp(s): return MassProperties(1000.,(0.,0.,0.),diag(2000.,3000.,4000.-10.*s.t_s),diag(0.,0.,-10.))
        s=replace(self.s0,omega_B_rad_s=(0.,0.,1.))
        d=derivative(s,mp,self.none)
        self.assertAlmostEqual(d.domega[2],10./4000.,12)

    def test_configuration_detachment_mass_property_provider(self):
        def mp(s):
            if s.configuration=='DOCKED': return MassProperties(1200.,(1.,0.,0.),diag(100.,200.,300.))
            if s.configuration=='ABSENT': return MassProperties(1000.,(0.,0.,0.),diag(90.,180.,270.))
            raise DynamicsError('bad config')
        self.assertEqual(mp(replace(self.s0,configuration='DOCKED')).mass_kg,1200.)
        self.assertEqual(mp(replace(self.s0,configuration='ABSENT')).mass_kg,1000.)

    def test_fail_closed_singular_inertia(self):
        def bad(s): return MassProperties(1000.,(0.,0.,0.),diag(1.,1.,0.))
        with self.assertRaises(DynamicsError): derivative(self.s0,bad,self.none)


if __name__=='__main__': unittest.main()
