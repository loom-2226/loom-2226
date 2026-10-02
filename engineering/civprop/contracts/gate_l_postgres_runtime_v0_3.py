"""Gate L PostgreSQL durable-runtime qualification contract. NON-CANON."""
SCHEMA="loom_gate_l_qual"
TABLES=("runtime_state","event_queue","transaction_ledger","processed_events")
def schema_sql():
 return """CREATE SCHEMA IF NOT EXISTS loom_gate_l_qual;
CREATE TABLE IF NOT EXISTS loom_gate_l_qual.runtime_state(key text PRIMARY KEY,value jsonb NOT NULL);
CREATE TABLE IF NOT EXISTS loom_gate_l_qual.event_queue(event_id text PRIMARY KEY,year int NOT NULL,event_type text NOT NULL,payload jsonb NOT NULL,provenance_refs jsonb NOT NULL,status text NOT NULL DEFAULT 'PENDING');
CREATE TABLE IF NOT EXISTS loom_gate_l_qual.transaction_ledger(transaction_id text PRIMARY KEY,opportunity_id text NOT NULL,committed_at timestamptz NOT NULL DEFAULT clock_timestamp(),provenance_refs jsonb NOT NULL);
CREATE TABLE IF NOT EXISTS loom_gate_l_qual.processed_events(event_id text PRIMARY KEY,processed_at timestamptz NOT NULL DEFAULT clock_timestamp());"""
def qualification_invariants():
 return ("DURABLE_ACROSS_CONNECTIONS","ATOMIC_ROLLBACK","TRANSACTION_IDEMPOTENCE","EVENT_IDEMPOTENCE","PERSISTENT_EVENT_QUEUE","QUALIFICATION_SCHEMA_ISOLATION")
