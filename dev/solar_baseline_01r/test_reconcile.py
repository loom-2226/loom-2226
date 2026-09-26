import json
import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from reconcile import compare, parse_number, normalize_unit, build


def row(body="TEST", prop="GM", value="1", unit="km^3/s^2", uncertainty=None,
        lineage="L1", artifact="A1", epistemic="DYNAMICAL_INFERENCE", kind="REFERENCE_CONSTANT"):
    return {"assertion_id":f"{body}-{prop}-{lineage}-{value}","body_id":body,"property_code":prop,
            "reported_value":value,"reported_unit":unit,"reported_uncertainty":uncertainty,
            "normalized_value":value,"normalized_unit":unit,"normalized_uncertainty":uncertainty,
            "source_lineage":lineage,"source_artifact_id":artifact,"epistemic_class":epistemic,
            "source_value_kind":kind,"source_reference":None}


class NumericParsingTests(unittest.TestCase):
    def test_scientific_and_fortran_notation(self):
        self.assertEqual(parse_number("1.25D+03").lo, 1250)
        self.assertEqual(parse_number("( 3.0D-4 )").lo, __import__('decimal').Decimal("0.00030"))
        self.assertEqual(parse_number("~3.0e-4").lo, __import__('decimal').Decimal("0.00030"))

    def test_limits_keep_inequality_and_open_endpoint(self):
        self.assertEqual(parse_number("<0.0002").op,"<")
        self.assertTrue(parse_number("<0.0002").hi_open)
        self.assertFalse(parse_number("<=0.0002").hi_open)
        self.assertEqual(parse_number("0.2..0.4").kind,"RANGE")


class ReconciliationTests(unittest.TestCase):
    def test_ceres_rotation_unit_and_display_precision(self):
        a=row("CERES","ROTATION_PERIOD","9.074170","h","0.000001","a")
        b=row("CERES","ROTATION_PERIOD","0.37809042","d",None,"b")
        result=compare(a,b)
        self.assertEqual(result["classification"],"PRECISION_EQUIVALENT")
        self.assertEqual(result["reason_code"],"ROUNDS_TO_COARSER_REPORTED_DECIMAL_QUANTUM")

    def test_europa_gm_high_precision_and_rounded(self):
        a=row("EUROPA","GM","3202.71210","km^3/s^2","0.00181","a")
        b=row("EUROPA","GM","3.202712099607295D+03","km^3/s^2",None,"b")
        self.assertEqual(compare(a,b)["classification"],"PRECISION_EQUIVALENT")

    def test_units_gm_density_radius_and_rotation(self):
        self.assertEqual(compare(row(value="1",unit="km^3/s^2"),row(value="1000000000",unit="m^3/s^2",lineage="L2"))["classification"],"UNIT_EQUIVALENT")
        self.assertEqual(compare(row(prop="BULK_DENSITY",value="1",unit="g/cm^3"),row(prop="BULK_DENSITY",value="1000",unit="kg/m^3",lineage="L2"))["classification"],"UNIT_EQUIVALENT")
        self.assertEqual(compare(row(prop="ROTATION_PERIOD",value="24",unit="h"),row(prop="ROTATION_PERIOD",value="86400",unit="s",lineage="L2"))["classification"],"UNIT_EQUIVALENT")
        self.assertEqual(compare(row(prop="MEAN_RADIUS",value="1",unit="km"),row(prop="MEAN_RADIUS",value="1000",unit="m",lineage="L2"))["classification"],"UNIT_EQUIVALENT")
        self.assertEqual(compare(row(prop="POLE_ORIENTATION",value="180",unit="deg"),row(prop="POLE_ORIENTATION",value="3.141592653589793",unit="rad",lineage="L2"))["classification"],"PRECISION_EQUIVALENT")
        # Property code gate prevents diameter/radius cross-comparison.
        self.assertEqual(compare(row(prop="EFFECTIVE_DIAMETER",value="2"),row(prop="MEAN_RADIUS",value="1",lineage="L2"))["classification"],"SEMANTICALLY_DISTINCT")
        self.assertEqual(compare(row(prop="GM",value="1"),row(prop="MASS",value="1",lineage="L2"))["classification"],"SEMANTICALLY_DISTINCT")

    def test_range_is_never_reduced_to_a_midpoint(self):
        self.assertEqual(compare(row(value="1..3"),row(value="2",lineage="L2"))["classification"],"RANGE_COMPATIBLE")
        self.assertEqual(compare(row(value="1..2"),row(value="3",lineage="L2"))["classification"],"CONFLICT")

    def test_source_order_does_not_select_a_winner(self):
        a=row(value="1",lineage="latest")
        b=row(value="2",lineage="older")
        ab=compare(a,b);ba=compare(b,a)
        self.assertEqual((ab["classification"],ab["reason_code"]),(ba["classification"],ba["reason_code"]))
        self.assertNotIn("preferred",json.dumps(compare(a,b)).lower())

    def test_real_disagreement_is_never_averaged(self):
        for left,right in (("5.6251476453852289","7"),("2.8304096393299849","5"),("1.5896582441709424","1.601")):
            self.assertEqual(compare(row(value=left),row(value=right,lineage="L2"))["classification"],"CONFLICT")

    def test_triaxial_vectors_and_source_normalization_defect(self):
        a=row(prop="TRIAXIAL_RADII",value='["605","605","605"]',unit="km",lineage="same")
        b=row(prop="TRIAXIAL_RADII",value='["606","606","606"]',unit="km",lineage="same")
        self.assertEqual(compare(a,b)["classification"],"CONFLICT")
        broken=row(body="MOON",prop="GM",value='["4.9028001184575496","3"]',lineage="broken")
        broken["reported_value"]="( 4.9028001184575496D+03 )"
        self.assertEqual(compare(broken,row(body="MOON",prop="GM",value="4902.800",lineage="other"))["classification"],"NOT_COMPARABLE")
        self.assertEqual(compare(broken,row(body="MOON",prop="GM",value="4902.800",lineage="other"))["reason_code"],"REPORTED_NORMALIZED_VALUE_MISMATCH")

    def test_limits_and_zero_are_preserved(self):
        self.assertEqual(compare(row(value="0.001110040850536676"),row(value="<0.0002",lineage="L2"))["classification"],"LIMIT_CONFLICT")
        self.assertEqual(compare(row(value="0E+0"),row(value="<0.0003",lineage="L2"))["classification"],"LIMIT_COMPATIBLE")
        self.assertEqual(compare(row(value="0.2"),row(value="<0.2",lineage="L2"))["classification"],"LIMIT_CONFLICT")

    def test_no_invented_uncertainty_or_precision_exactness(self):
        self.assertEqual(compare(row(value="1.23456789"),row(value="1.2",lineage="L2"))["classification"],"PRECISION_EQUIVALENT")
        self.assertNotEqual(compare(row(value="1.23456789"),row(value="1.2",lineage="L2"))["classification"],"EXACT_EQUIVALENT")
        self.assertEqual(compare(row(value="~1.2000"),row(value="1.2",lineage="L2"))["classification"],"INSUFFICIENT_INFORMATION")

    def test_reported_uncertainties_overlap_only_when_both_are_present(self):
        self.assertEqual(compare(row(value="1.0",uncertainty="0.2"),row(value="1.3",uncertainty="0.2",lineage="L2"))["classification"],"AGREES_WITHIN_UNCERTAINTY")
        self.assertEqual(compare(row(value="1.0",uncertainty="0.2"),row(value="1.3",lineage="L2"))["classification"],"CONFLICT")

    def test_inline_uncertainty_is_preserved_and_compared(self):
        parsed=parse_number("1.0 ± 0.2")
        self.assertEqual(parsed.lo, __import__('decimal').Decimal("1.0"))
        self.assertEqual(parsed.uncertainty, __import__('decimal').Decimal("0.2"))
        self.assertEqual(compare(row(value="1.0 ± 0.2"),row(value="1.3 +/- 0.2",lineage="L2"))["classification"],"AGREES_WITHIN_UNCERTAINTY")

    def test_lineage_duplicates_are_not_independent_confirmation(self):
        got=compare(row(value="2",lineage="same"),row(value="2",lineage="same",artifact="A2"))
        self.assertEqual(got["classification"],"EXACT_EQUIVALENT")
        self.assertEqual(got["reason_code"],"SAME_LINEAGE_IDENTICAL_VALUE")

    def test_model_and_measurement_semantics_are_distinct(self):
        a=row(value="1",epistemic="PHYSICAL_MODEL",kind="MODEL_COEFFICIENT")
        b=row(value="1",lineage="L2",epistemic="IN_SITU_DIRECT",kind="COMPILED_REFERENCE_PARAMETER")
        self.assertEqual(compare(a,b)["classification"],"SEMANTICALLY_DISTINCT")

    def test_cross_body_comparison_is_prohibited(self):
        self.assertEqual(compare(row(body="EUROPA"),row(body="CERES",lineage="L2"))["classification"],"NOT_COMPARABLE")


class EngineIntegrationTests(unittest.TestCase):
    def test_baseline_read_only_identity_and_replay(self):
        root=Path(__file__).resolve().parents[1]
        source=root/"solar_baseline_01"/"LOOM_SOLAR_BASELINE_01_CANDIDATE_V20.sqlite3"
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);r1=build(source,p/"a.sqlite3",p/"r1")
            r1b=build(source,p/"a2.sqlite3",p/"r1b")
            r2=build(source,p/"b.sqlite3",p/"r2",reverse=True)
            self.assertEqual(r1["semantic_digest"],r2["semantic_digest"])
            self.assertEqual(hashlib.sha256((p/"a.sqlite3").read_bytes()).hexdigest(),hashlib.sha256((p/"a2.sqlite3").read_bytes()).hexdigest())
            self.assertEqual(r1["classification_counts"],r2["classification_counts"])
            self.assertFalse(r1["input_mutated"])
            self.assertEqual(r1["input_assertions"],788)
            self.assertEqual(r1["identity"]["holds_before"],5)  # 4 families, one duplicate evidence row
            self.assertEqual(r1["identity"]["holds_after"],4)
            self.assertEqual(r1["identity"]["held_identity_families_after"],3)
            self.assertEqual(r1["identity"]["primary_identity_families_resolved"],4)
            self.assertEqual(r1["identity"]["crosswalk_rows_resolved"],1)
            self.assertEqual(r1["identity"]["released_assertions"],11)
            self.assertEqual(r1["effective_coverage"]["supported_after"]-r1["effective_coverage"]["supported_before"],10)
            self.assertEqual(r1["preferred_fact_count"],0)
            ledger=sqlite3.connect(p/"a.sqlite3")
            self.assertEqual(ledger.execute("select count(*) from assertion_disposition_event").fetchone()[0],11)
            self.assertEqual(ledger.execute("select count(*) from assertion_disposition_event where body_id='KLEOPATRA'").fetchone()[0],11)
            self.assertEqual(ledger.execute("select count(*) from assertion_disposition_event where body_id in ('DIDYMOS','EURYBATES','PATROCLUS')").fetchone()[0],0)
            ledger.close()

    def test_identity_alias_collision_and_control_state_remain_unchanged(self):
        root=Path(__file__).resolve().parents[1]
        source=root/"solar_baseline_01"/"LOOM_SOLAR_BASELINE_01_CANDIDATE_V20.sqlite3"
        control=root/"solar_facts_multi_body"/"sf_promote_03_europa_ceres_67p"/"LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_03_EUROPA_CERES_67P.sqlite3"
        sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        source_before=sha(source);control_before=sha(control)
        c=sqlite3.connect(source)
        europa=c.execute("select body_id,identifier_value from body_identifier_ref where identifier_type='NAIF_ID' and identifier_value='502'").fetchall()
        c.close()
        self.assertEqual(europa,[('EUROPA','502')])
        authority_doc=(Path(__file__).resolve().parent/"raw"/"naif_ids_required_reading.html").read_text()
        self.assertIn("'EUROPA'",authority_doc)
        self.assertIn("'52 EUROPA'",authority_doc)
        self.assertEqual(sha(source),source_before)
        self.assertEqual(sha(control),control_before)


if __name__ == "__main__":
    unittest.main()
