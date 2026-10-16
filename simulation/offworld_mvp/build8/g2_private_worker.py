"""Isolated Build 8 policy worker: preloads one source-verified policy.

-I -S, serialized input only; no kernel, WORLD or site import capability.
"""
import builtins
import importlib.util
import json
import pathlib
import sys

path = pathlib.Path(__file__).with_name("g2_private_policy.py")
spec = importlib.util.spec_from_file_location("_g2_private_policy", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def _deny(*a, **k):
    raise PermissionError("G2 policy sandbox denied")


def probe(snapshot):
    probes = {}
    for name in ("os", "time", "random", "secrets", "socket"):
        try:
            builtins.__import__(name)
            probes[name] = "LEAK"
        except PermissionError:
            probes[name] = "BLOCKED"
    try:
        builtins.open("/etc/passwd")
        probes["filesystem"] = "LEAK"
    except PermissionError:
        probes["filesystem"] = "BLOCKED"
    for key in ("world_seed", "hidden_state", "kernel", "scheduler",
                "resources", "run_identity", "universe_id"):
        probes["payload:" + key] = ("LEAK" if key in snapshot else "BLOCKED")
    return probes


def main():
    payload = json.loads(sys.stdin.read())
    builtins.open = _deny
    builtins.__import__ = _deny
    builtins.exec = _deny
    builtins.eval = _deny
    builtins.compile = _deny
    builtins.input = _deny
    if payload["mode"] == "PROBE":
        result = probe(payload["snapshot"])
    elif payload["mode"] == "EVALUATE":
        result = module.evaluate(payload["snapshot"], payload["request"],
                                 payload["parameters"], payload["decision_key"])
    else:
        raise ValueError("worker mode unsupported")
    sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
