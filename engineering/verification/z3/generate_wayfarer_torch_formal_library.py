#!/usr/bin/env python3
"""Deterministically emit SMT-LIB torch-card functions from exact engineering inputs."""
from pathlib import Path
from src.wayfarer_torch_mode_cards import MODE_CARDS

OUT = Path(__file__).with_name("wayfarer_torch_generated_cards_v0.1.smt2")


def q(x):
    # SMT-LIB integer numerals have sort Int. These functions return Real, so
    # whole-valued Fractions must be emitted as Real literals rather than bare Ints.
    return f"{x.numerator}.0" if x.denominator == 1 else f"(/ {x.numerator}.0 {x.denominator}.0)"


def generate():
    modes = " ".join(MODE_CARDS)
    lines = [
        "; GENERATED FILE — DO NOT HAND EDIT.",
        "; Source: src/wayfarer_torch_mode_cards.py",
        "; Engineering verification only / non-canon / non-certification.",
        f"(declare-datatypes () ((TorchMode OFF {modes})))",
    ]
    for fn, idx in (("mode-mdot", 0), ("mode-ve", 1)):
        lines.append(f"(define-fun {fn} ((m TorchMode)) Real")
        expr = "0.0"
        for name in reversed(tuple(MODE_CARDS)):
            expr = f"(ite (= m {name}) {q(MODE_CARDS[name][idx])} {expr})"
        lines.append(f"  {expr})")
    lines.extend([
        "(define-fun mode-thrust ((m TorchMode)) Real (* (mode-mdot m) (mode-ve m)))",
        "(define-fun mode-pjet ((m TorchMode)) Real (* (/ 1.0 2.0) (mode-mdot m) (mode-ve m) (mode-ve m)))",
        "(define-fun mode-torch-active ((m TorchMode)) Bool (not (= m OFF)))",
        "",
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    OUT.write_text(generate())
    print(OUT)
