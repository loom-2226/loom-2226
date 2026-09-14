#!/usr/bin/env python3
import json


def build_boundary():
    return {
        "schema": "LOOM_CIVSTATE_PHASE13_PROVENANCE_LOSS_BOUNDARY_V1",
        "status": "PASS",
        "phase13_checkpoint_status": "EXACT_CHECKPOINT_RECOVERED",
        "phase13_sqlite_sha256": "5cb7c3c9faa89dba6ff42500f2b70756a6f9f58027c7f6035df5cb447f186753",
        "navigator_sha256": "906a31616ef4895997ce6e02e389789e884240671f7fef89abc59ca370d5f4a2",
        "navigator_match": True,
        "original_materializer_source_status": "NOT_RECOVERED",
        "repository_history_search": "NO_PHASE13_OR_MATERIALIZER2226_BUILDER_COMMIT_FOUND",
        "retained_file_search": "NO_ORIGINAL_PHASE13_BUILDER_OR_SEED_ARCHIVE_FOUND",
        "generator_reconstruction_authority": "ZERO",
        "allocator_implementation_authority": "ZERO",
        "reverse_regression_as_definition_authority": "ZERO",
        "preserved_runtime_authority": "CURRENT_RUNTIME_VALUES_AND_EXACTLY_REVERIFIED_EQUATIONS_ONLY",
        "interpretation": "RECOVERED_STATE_DOES_NOT_IMPLY_RECOVERED_GENERATOR",
        "unlock_condition": "NEW_PRIMARY_SOURCE_REQUIRED: ORIGINAL_PHASE13_BUILDER_OR_HASH_VALIDATED_SEED_ARCHIVE_OR_EQUIVALENT_DIRECT_GENERATOR_EVIDENCE",
        "next_action": "FREEZE_PROVENANCE_LOSS_BOUNDARY_AND_DO_NOT_REALLOCATE_HEL_FROM_INFERRED_FORMULAS",
    }


def main():
    print(json.dumps(build_boundary(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
