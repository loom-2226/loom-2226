import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "build_database_data_dictionary.py"
SPEC = importlib.util.spec_from_file_location("build_database_data_dictionary", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def test_dictionary_generator_covers_every_current_table_and_column():
    defs = ROOT / "docs" / "database_semantics" / "DATA_DICTIONARY_FIELD_DEFINITIONS_v0.1.json"
    doc = mod.build(
        [ROOT / "data" / "LOOM_2226.sqlite3", ROOT / "data" / "LOOM_2226_CIVSTATE.sqlite3"],
        defs,
    )

    observed = set()
    for db in doc["databases"]:
        for table in db["tables"]:
            for col in table["columns"]:
                key = (db["database"], table["table"], col["name"])
                assert key not in observed
                observed.add(key)
                assert "definition_status" in col

    # Independently enumerate SQLite and prove the generator omitted nothing.
    expected = set()
    import sqlite3
    for db_path in (ROOT / "data" / "LOOM_2226.sqlite3", ROOT / "data" / "LOOM_2226_CIVSTATE.sqlite3"):
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )]
        for table in tables:
            safe = table.replace("'", "''")
            for r in con.execute(f"PRAGMA table_info('{safe}')"):
                expected.add((db_path.name, table, r[1]))
        con.close()

    assert observed == expected


def test_every_definition_registry_entry_resolves_to_a_real_column_or_table_wildcard():
    defs_path = ROOT / "docs" / "database_semantics" / "DATA_DICTIONARY_FIELD_DEFINITIONS_v0.1.json"
    payload = json.loads(defs_path.read_text(encoding="utf-8"))

    import sqlite3
    schemas = {}
    for db_path in (ROOT / "data" / "LOOM_2226.sqlite3", ROOT / "data" / "LOOM_2226_CIVSTATE.sqlite3"):
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )]
        schemas[db_path.name] = {
            t: {r[1] for r in con.execute(f"PRAGMA table_info('{t.replace(chr(39), chr(39)*2)}')")}
            for t in tables
        }
        con.close()

    for row in payload["fields"]:
        assert row["database"] in schemas
        assert row["table"] in schemas[row["database"]]
        if row["column"] != "*":
            assert row["column"] in schemas[row["database"]][row["table"]]
