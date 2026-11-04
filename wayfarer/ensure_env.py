"""Bootstrap only the pinned, non-governing Wayfarer Python environment."""
from importlib import metadata
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REQUIREMENTS = ROOT / "requirements.txt"


def pinned():
    return dict(line.strip().split("==", 1) for line in REQUIREMENTS.read_text().splitlines()
                if line.strip() and not line.lstrip().startswith("#"))


def ready():
    try:
        return all(metadata.version(name) == version for name, version in pinned().items())
    except metadata.PackageNotFoundError:
        return False


def select_python():
    if ready():
        return sys.executable
    venv = ROOT / ".venv"
    python = venv / "bin" / "python"
    if not python.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True, stdout=sys.stderr)
    probe = "from importlib import metadata; import sys; " + "; ".join(
        f"sys.exit(1) if metadata.version({name!r}) != {version!r} else None"
        for name, version in pinned().items())
    if subprocess.run([str(python), "-c", probe], stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL).returncode:
        subprocess.run([str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)],
                       check=True, stdout=sys.stderr)
    return str(python)


def use_pinned_python():
    python = select_python()
    if os.path.abspath(python) != os.path.abspath(sys.executable):
        os.execv(python, [python, *sys.argv])


if __name__ == "__main__":
    print(select_python())
