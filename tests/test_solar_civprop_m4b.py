import hashlib
import json
import sqlite3
import subprocess
import sys
import unittest
import csv
import tempfile
import shutil
from pathlib import Path

R = Path(__file__).resolve().parents[1]
M = R / "dev/solar_civprop_m4b"
DB = M / "LOOM_SOLAR_CIVPROP_M4B_CANDIDATE.sqlite3"
sys.path.insert(0, str(M))
from validate_m4b import validate_campaign, violations


class M4BQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.campaign = json.loads((M / "campaign_assertions.json").read_text())
        with (M / "reports/M4B_COVERAGE_MATRIX.csv").open() as f:
            cls.coverage = list(csv.DictReader(f))
        cls.artifacts = json.loads((M / "reports/M4B_RAW_ARTIFACT_MANIFEST.json").read_text())
        cls.conn = sqlite3.connect(DB)
        cls.conn.row_factory = sqlite3.Row
        cls.identities = {x[0] for x in cls.conn.execute("select body_id from body")}

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_complete_contract_and_unknown_separation(self):
        validate_campaign(self.campaign, self.identities)
        self.assertEqual(len(self.coverage), 380)
        self.assertEqual(len({(r['body_id'], r['resource_family']) for r in self.coverage}), 380)
        self.assertTrue(all(r['research_state'] == 'ASSESSED' for r in self.coverage))
        self.assertEqual(self.conn.execute("select count(*) from material_evidence where fact_status!='CANDIDATE'").fetchone()[0], 0)
        self.assertEqual(self.conn.execute("select count(*) from preferred_fact").fetchone()[0], 0)
        self.assertEqual(self.conn.execute("select count(*) from body").fetchone()[0], 110)
        self.assertFalse(any(r['coverage_disposition'] == 'UNKNOWN_AFTER_SEARCH' and r['evidence_records'] for r in self.coverage))

    def test_hostile_unknown_zero_taxonomy_economics_and_bounds(self):
        base = dict(self.campaign['evidence_assertions'][0])
        attack = dict(base, abundance_semantics='UNKNOWN', abundance_value=0, abundance_unit='wt%')
        self.assertIn('UNKNOWN_LAUNDERED_TO_NUMERIC', violations(attack, self.identities))
        attack = dict(base, material_species='C-type taxonomy', abundance_semantics='QUANTIFIED', abundance_value=6, abundance_unit='wt%')
        self.assertIn('TAXONOMY_LAUNDERED_TO_ABUNDANCE', violations(attack, self.identities))
        attack['economic_score'] = 1
        self.assertIn('DOWNSTREAM_ECONOMIC_OR_ENGINEERING_LEAKAGE', violations(attack, self.identities))
        attack = dict(base, abundance_min=8, abundance_max=2)
        self.assertIn('INVALID_ABUNDANCE_BOUNDS', violations(attack, self.identities))
        attack = dict(base, abundance_semantics='QUANTIFIED', abundance_value=1, abundance_unit=None)
        self.assertIn('QUANTIFIED_WITHOUT_VALUE_OR_UNIT', violations(attack, self.identities))
        attack = dict(base, abundance_semantics='BOUNDED', abundance_min=1, abundance_max=2, abundance_unit=None)
        self.assertIn('BOUNDED_ABUNDANCE_WITHOUT_UNIT', violations(attack, self.identities))
        attack = dict(base, abundance_semantics='QUANTIFIED', abundance_value=101, abundance_unit='wt%')
        self.assertIn('PERCENT_ABUNDANCE_OVER_100', violations(attack, self.identities))

    def test_identity_observation_region_and_candidate_scopes(self):
        bad = dict(self.campaign['evidence_assertions'][0], body_id='NOT_A_LOOM_BODY')
        self.assertIn('IDENTITY_NOT_ELIGIBLE', violations(bad, self.identities))
        for row in self.conn.execute("select m.body_id, m.region_id, m.observation_id, o.body_id ob, r.body_id rb, m.fact_status from material_evidence m left join observation o using(observation_id) left join body_region r using(region_id)"):
            self.assertEqual(row['body_id'], row['ob'])
            self.assertTrue(row['rb'] is None or row['body_id'] == row['rb'])
            self.assertEqual(row['fact_status'], 'CANDIDATE')
        self.assertEqual(self.conn.execute('pragma foreign_key_check').fetchall(), [])
        self.assertEqual(self.conn.execute('pragma integrity_check').fetchone()[0], 'ok')

    def test_unknown_not_synthesized_and_firewalls(self):
        self.assertEqual(self.conn.execute("select count(*) from material_evidence where abundance_semantics='UNKNOWN' and abundance_value is not null").fetchone()[0], 0)
        forbidden = {'delta_v','flight_time','accessibility_score','mining_rate','extraction_efficiency','recovery_efficiency','price','cost','npv','bemr','profit','resource_score','habitation_suitability','settlement_attractiveness'}
        cols = {r[1].lower() for t, in self.conn.execute("select name from sqlite_master where type='table'") for r in self.conn.execute(f'pragma table_info({t})')}
        self.assertFalse(forbidden & cols)
        self.assertEqual(self.conn.execute("select count(*) from material_evidence where lower(coalesce(abundance_unit,'')) in ('wt%','vol%','ppm','ppb') and abundance_semantics like 'QUANTIFIED%' and abundance_value is null").fetchone()[0], 0)

    def test_frozen_source_artifacts_hashes(self):
        acquired = json.loads((M / 'reports/source_acquisition.json').read_text())
        artifacts = [(s['source_key'], a) for s in acquired['sources'] for a in [s] + s.get('related_artifacts', []) if a.get('status') == 'ACQUIRED']
        self.assertGreaterEqual(len(artifacts), 25)
        retained = {a['artifact_path'] for a in self.artifacts['raw_artifacts'] if a.get('retained_in_repository')}
        sql_artifacts = {r[0]: r[1:] for r in self.conn.execute("select artifact_id,sha256,byte_count,local_path from source_artifact where artifact_id like 'M4B:%'")}
        self.assertEqual(len(sql_artifacts), len(artifacts))
        artifact_n = {}
        for source_key, a in artifacts:
            artifact_n[source_key] = artifact_n.get(source_key, 0) + 1
            stored = sql_artifacts[f"M4B:{source_key}:{artifact_n[source_key]}"]
            self.assertEqual(stored, (a['sha256'], a['bytes'], a['artifact_path']))
            path = R / a['artifact_path']
            if path.is_file():
                self.assertEqual(path.stat().st_size, a['bytes'], source_key)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), a['sha256'], source_key)
            if a['artifact_path'] in retained:
                self.assertTrue(path.is_file(), source_key)
            self.assertEqual(len(a['sha256']), 64)

    def test_three_body_non_interference(self):
        report = json.loads((M / 'reports/M4B_NON_INTERFERENCE.json').read_text())
        self.assertTrue(report['body_digests_exactly_unchanged'])
        self.assertTrue(report['inherited_qualified_rows_exactly_unchanged'])
        self.assertTrue(report['candidate_only_new_rows_all_candidate'])
        for body in ('CERES', 'COMET_67P', 'EUROPA'):
            self.assertEqual(report['body_digests_before'][body], report['body_digests_after'][body])

    def test_offline_deterministic_replay(self):
        # Rebuild twice from frozen local inputs and compare byte-level output.
        hashes = []
        for _ in range(2):
            subprocess.run([sys.executable, str(M / 'build_m4b.py')], cwd=R, check=True, capture_output=True, text=True)
            hashes.append(hashlib.sha256(DB.read_bytes()).hexdigest())
        self.assertEqual(hashes[0], hashes[1])

    def test_insertion_order_semantic_equivalence(self):
        def projection(path):
            c = sqlite3.connect(path)
            key = lambda row: json.dumps(row, sort_keys=True, default=str)
            sources = sorted((tuple(r) for r in c.execute("select source_type,provider,title,doi,url,publication_date,persistent_identifier,citation_text,notes from source")), key=key)
            regions = sorted((tuple(r) for r in c.execute("select b.body_id,r.region_type,r.canonical_name,r.description,r.confidence_class,s.doi,s.url from body_region r join body b using(body_id) left join source s using(source_id)")), key=key)
            observations = sorted((tuple(r) for r in c.execute("select b.body_id,r.canonical_name,o.mission,o.spacecraft,o.instrument,o.observation_product_id,o.observation_time_start,o.observation_time_end,o.observation_method,o.spatial_context,s.doi,s.url from observation o join body b using(body_id) left join body_region r on r.region_id=o.region_id left join source s using(source_id)")), key=key)
            materials = sorted((tuple(r) for r in c.execute("select b.body_id,r.canonical_name,m.material_family,m.material_species,m.physical_form,m.host_material,m.location_context,m.evidence_class,m.abundance_semantics,m.abundance_value,m.abundance_min,m.abundance_max,m.abundance_unit,m.reported_abundance,m.depth_min,m.depth_max,m.depth_unit,m.thickness_min,m.thickness_max,m.thickness_unit,m.areal_extent,m.areal_extent_unit,m.estimated_volume,m.estimated_volume_unit,m.spatial_heterogeneity,m.measurement_resolution,m.measurement_method,m.confidence_class,m.fact_status,o.observation_product_id,s.doi,s.url,m.notes from material_evidence m join body b using(body_id) left join body_region r on r.region_id=m.region_id left join observation o using(observation_id) left join source s using(source_id)")), key=key)
            artifacts = sorted((tuple(r) for r in c.execute("select s.doi,s.url,a.locator,a.local_path,a.retrieved_at,a.sha256,a.byte_count,a.media_type,a.original_filename,a.version from source_artifact a join source s using(source_id) where a.artifact_id like 'M4B:%'")), key=key)
            c.close()
            return (sources, regions, observations, materials, artifacts)

        canonical = projection(DB)
        original = {}
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            shutil.copytree(M / 'reports', tmp / 'reports')
            shutil.copy2(DB, tmp / DB.name)
            for name in ('source_catalog.json', 'campaign_assertions.json'):
                path = M / name
                original[name] = path.read_bytes()
            try:
                sources = json.loads(original['source_catalog.json'])
                sources['sources'].reverse()
                (M / 'source_catalog.json').write_text(json.dumps(sources, indent=2) + '\n')
                campaign = json.loads(original['campaign_assertions.json'])
                for key in ('evidence_assertions', 'region_definitions', 'observation_definitions'):
                    campaign[key].reverse()
                (M / 'campaign_assertions.json').write_text(json.dumps(campaign, indent=2) + '\n')
                subprocess.run([sys.executable, str(M / 'build_m4b.py')], cwd=R, check=True, capture_output=True, text=True)
                self.assertEqual(canonical, projection(DB))
            finally:
                for name, data in original.items():
                    (M / name).write_bytes(data)
                shutil.copy2(tmp / DB.name, DB)
                shutil.rmtree(M / 'reports')
                shutil.copytree(tmp / 'reports', M / 'reports')


if __name__ == '__main__':
    unittest.main()
