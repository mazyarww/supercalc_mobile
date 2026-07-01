"""
core.math_engine.engine
------------------------
The base numeric calculation engine.

Responsibilities:
- Safe parsing/evaluation of arithmetic & scientific expressions
- Arbitrary precision (via mpmath)
- Complex number support
- A constants library (pi, e, i, physical constants, ...)
- User-defined variables and functions
- Percentages and fractions

This module deliberately does NOT use Python's eval() on raw strings.
Everything is parsed through sympy's safe parser (which does not execute
arbitrary Python) and then evaluated numerically with mpmath for precision.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import mpmath
import sympy
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

_TRANSFORMS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

# ---------------------------------------------------------------------------
# Constants library
# ---------------------------------------------------------------------------
CONSTANTS: dict[str, Any] = {
    "pi": sympy.pi,
    "e": sympy.E,
    "i": sympy.I,
    "j": sympy.I,               # engineering notation
    "inf": sympy.oo,
    "phi": sympy.GoldenRatio,
    "gamma": sympy.EulerGamma,
    # Physical constants (SI units, values as float -> sympy Float)
    "c": sympy.Float(299_792_458),            # speed of light m/s
    "G": sympy.Float(6.67430e-11),             # gravitational constant
    "h": sympy.Float(6.62607015e-34),          # Planck constant
    "hbar": sympy.Float(1.054571817e-34),
    "k_B": sympy.Float(1.380649e-23),          # Boltzmann constant
    "N_A": sympy.Float(6.02214076e23),         # Avogadro's number
    "e_charge": sympy.Float(1.602176634e-19),  # elementary charge
    "m_e": sympy.Float(9.1093837015e-31),      # electron mass
    "m_p": sympy.Float(1.67262192369e-27),     # proton mass
    "eps0": sympy.Float(8.8541878128e-12),     # vacuum permittivity
    "mu0": sympy.Float(1.25663706212e-6),      # vacuum permeability
    "R": sympy.Float(8.314462618),             # gas constant
    "sigma": sympy.Float(5.670374419e-8),      # Stefan-Boltzmann constant
    "g": sympy.Float(9.80665),                 # standard gravity
}


class EngineError(Exception):
    """Raised for any user-facing calculation error (bad syntax, domain error, etc.)."""


@dataclass
class EvalResult:
    input_expr: str
    sympy_expr: Any
    exact: Any            # simplified/exact symbolic form
    approx: Any            # numeric approximation (mpmath value or complex)
    latex: str = ""
    is_exact_integer: bool = False


@dataclass
class Engine:
    """Stateful calculation engine: holds variables, functions and precision settings."""

    precision_digits: int = 50
    angle_mode: str = "rad"       # 'rad' or 'deg'
    variables: dict[str, Any] = field(default_factory=dict)
    functions: dict[str, tuple[list[str], Any]] = field(default_factory=dict)  # name -> (args, expr)
    history: list[EvalResult] = field(default_factory=list)

    def __post_init__(self):
        mpmath.mp.dps = self.precision_digits

    # -- configuration -----------------------------------------------------
    def set_precision(self, digits: int) -> None:
        self.precision_digits = max(1, min(digits, 1000))
        mpmath.mp.dps = self.precision_digits

    def set_angle_mode(self, mode: str) -> None:
        if mode not in ("rad", "deg"):
            raise EngineError("angle mode must be 'rad' or 'deg'")
        self.angle_mode = mode

    # -- variables / functions ----------------------------------------------
    def set_variable(self, name: str, value_expr: str) -> Any:
        result = self.evaluate(value_expr)
        self.variables[name] = result.exact
        return result

    def define_function(self, name: str, args: list[str], body_expr: str) -> None:
        local = self._locals()
        body = parse_expr(body_expr, local_dict=local, transformations=_TRANSFORMS)
        self.functions[name] = (args, body)

    # -- core evaluation ------------------------------------------------------
    def _locals(self) -> dict[str, Any]:
        """Build the symbol table available to the parser: constants + variables + user functions."""
        local: dict[str, Any] = dict(CONSTANTS)
        local.update(self.variables)

        # angle-mode aware trig wrappers
        if self.angle_mode == "deg":
            for fn in ("sin", "cos", "tan", "cot", "sec", "csc"):
                sym_fn = getattr(sympy, fn)
                local[fn] = (lambda f: (lambda x: f(x * sympy.pi / 180)))(sym_fn)

        # user-defined functions become sympy Lambdas
        for fname, (fargs, fbody) in self.functions.items():
            syms = sympy.symbols(fargs)
            if not isinstance(syms, (list, tuple)):
                syms = (syms,)
            local[fname] = sympy.Lambda(tuple(syms), fbody)

        return local

    def evaluate(self, expression: str) -> EvalResult:
        expression = expression.strip()
        if not expression:
            raise EngineError("Empty expression")

        # percentage shorthand: "50%" -> "50/100" ; "20% of 50" -> "(20/100)*50"
        expression = self._preprocess_percent(expression)

        local = self._locals()
        try:
            expr = parse_expr(expression, local_dict=local, transformations=_TRANSFORMS, evaluate=True)
        except Exception as exc:  # noqa: BLE001
            raise EngineError(f"Could not parse expression: {exc}") from exc

        try:
            exact = sympy.simplify(expr)
        except Exception:  # noqa: BLE001
            exact = expr

        approx = self._numeric_approx(exact)

        result = EvalResult(
            input_expr=expression,
            sympy_expr=expr,
            exact=exact,
            approx=approx,
            latex=sympy.latex(exact),
            is_exact_integer=exact.is_Integer if hasattr(exact, "is_Integer") else False,
        )
        self.history.append(result)
        return result

    def _numeric_approx(self, expr: Any) -> Any:
        try:
            val = expr.evalf(self.precision_digits)
            return val
        except Exception:  # noqa: BLE001
            return expr

    @staticmethod
    def _preprocess_percent(expression: str) -> str:
        import re

        # "X% of Y" -> "(X/100)*Y"
        expression = re.sub(
            r"([0-9.]+)\s*%\s*of\s*([0-9.a-zA-Z_()]+)", r"((\1)/100*(\2))", expression
        )
        # bare "X%" -> "(X/100)"
        expression = re.sub(r"([0-9.]+)\s*%", r"(\1/100)", expression)
        return expression

    # -- fractions -----------------------------------------------------------
    def to_fraction(self, expression: str, max_denominator: int = 10_000) -> sympy.Rational:
        result = self.evaluate(expression)
        return sympy.nsimplify(result.approx, rational=True).limit_denominator(max_denominator) \
            if hasattr(result.approx, "limit_denominator") else sympy.Rational(result.approx).limit_denominator(max_denominator)
